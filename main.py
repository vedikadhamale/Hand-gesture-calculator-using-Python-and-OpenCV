import re
import time
import cv2
import threading
import logging
import webbrowser
from flask import Flask, Response, jsonify, send_file
from flask_cors import CORS

from modules.gesture_detection import GestureDetector
from modules.voice_assistant import VoiceAssistant
from modules.calculator_engine import Calculator
from modules.history_manager import HistoryManager

# --- Silence Flask Logging ---
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)

# --- Global State for Web UI ---
global_state = {
    "expression": "",
    "result": "",
    "voice_status": "on",
    "history": [],
    "hand_detected": False,
    "active_gesture": "✋",
    "is_camera_active": False
}
latest_frame_bytes = None

NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, 
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}
FUNCTION_WORDS = {
    "sin": "sin", "sine": "sin", "cos": "cos", "cosine": "cos",
    "tan": "tan", "tangent": "tan", "log": "log", "sqrt": "sqrt",
}
CONSTANT_WORDS = {"pi": "pi", "e": "e"}
OP_WORDS = {
    "plus": "+", "add": "+", "minus": "-", "subtract": "-",
    "times": "*", "multiply": "*", "divide": "/", "power": "**",
}
OP_SPEAK = {"+": "plus", "-": "minus", "*": "multiply", "/": "divide", "**": "power"}

EMOJI_MAP = {
    "0": "✊", "1": "☝️", "2": "✌️", "3": "🤟", "4": "🖖", "5": "✋",
    "+": "Index 1 + Thumb ", "-": "👎", "clear": "✊✌️",
}

def normalize_voice(text):
    text = text.lower().strip()
    replace = {"square root": "sqrt", "to the power of": "power", "raised to": "power"}
    for a, b in replace.items():
        text = text.replace(a, b)
    return text

def parse_voice_command(text):
    actions = []
    if not text: return actions
    text = normalize_voice(text)
    if "quit" in text or "exit" in text: return [("quit", None)]
    if "clear" in text: actions.append(("clear", None))
    
    tokens = re.findall(r"\d+|[a-zA-Z]+|[+\-*/]", text)
    for token in tokens:
        if token.isdigit(): actions.append(("number", token))
        elif token in NUMBER_WORDS: actions.append(("number", NUMBER_WORDS[token]))
        elif token in FUNCTION_WORDS: actions.append(("function", FUNCTION_WORDS[token]))
        elif token in CONSTANT_WORDS: actions.append(("constant", CONSTANT_WORDS[token]))
        elif token in OP_WORDS: actions.append(("operator", OP_WORDS[token]))
    
    if "calculate" in text or "equals" in text:
        actions.append(("calculate", None))
    return actions

# --- Flask Routes ---
@app.route('/')
def index():
    return send_file('ai_gesture_calculator_ui.html')

@app.route('/state')
def get_state():
    return jsonify(global_state)

def generate_video():
    global latest_frame_bytes
    while True:
        if latest_frame_bytes is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_frame_bytes + b'\r\n')
        time.sleep(0.03)

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- OpenCV Background Thread ---
def opencv_thread_func():
    global global_state, latest_frame_bytes
    
    gesture = GestureDetector()
    voice = VoiceAssistant(enable_listen=True)
    calc = Calculator()
    history = HistoryManager()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera not available")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    voice.start_listening()
    voice.speak("AI calculator started")
    global_state["is_camera_active"] = True

    last_result = ""
    history_items = history.tail(5)

    stable_required = 6
    stable_count = 0
    last_seen = None

    last_commit_time = 0
    commit_delay = 0.8
    ready_for_next = True
    last_committed = None

    while True:
        ret, frame = cap.read()
        if not ret: break

        frame = cv2.flip(frame, 1)

        # Detect Gestures
        frame, gesture_type, gesture_value, gesture_label = gesture.detect(frame)
        
        # Web UI Update
        global_state["hand_detected"] = (gesture_type is not None)
        if gesture_type is not None:
            global_state["active_gesture"] = EMOJI_MAP.get(str(gesture_value), "✋")
            if gesture_type == "clear": global_state["active_gesture"] = EMOJI_MAP["clear"]
            if gesture_type == "equals": global_state["active_gesture"] = "✨"

        # Stability logic
        if gesture_type is None:
            stable_count = 0
            last_seen = None
            ready_for_next = True
        else:
            signature = (gesture_type, str(gesture_value))
            if signature == last_seen:
                stable_count += 1
            else:
                stable_count = 1
                last_seen = signature

            if (stable_count >= stable_required and 
               (ready_for_next or signature != last_committed) and 
               (time.time() - last_commit_time) > commit_delay):
                
                if gesture_type == "number":
                    calc.add(gesture_value)
                    voice.speak(str(gesture_value))
                elif gesture_type == "operator":
                    calc.operator(gesture_value)
                    voice.speak(OP_SPEAK.get(gesture_value, gesture_value))
                elif gesture_type == "clear":
                    calc.clear()
                    last_result = ""
                    voice.speak("cleared")
                elif gesture_type == "equals":
                    expression_before = calc.expression
                    result = calc.calculate()
                    last_result = str(result)
                    if result != "Error":
                        history.save(expression_before, result)
                        history_items = history.tail(5)
                    voice.speak(f"result {result}")

                last_commit_time = time.time()
                ready_for_next = False
                last_committed = signature

        # Voice commands
        voice_text = voice.pop_command()
        if voice_text:
            actions = parse_voice_command(voice_text)
            for action, value in actions:
                if action == "quit": break
                if action == "clear":
                    calc.clear()
                    last_result = ""
                    voice.speak("cleared")
                if action == "calculate":
                    expression_before = calc.expression
                    result = calc.calculate()
                    last_result = str(result)
                    if result != "Error":
                        history.save(expression_before, result)
                        history_items = history.tail(5)
                    voice.speak(f"result {result}")
                if action == "operator":
                    calc.operator(value)
                    voice.speak(OP_SPEAK.get(value, value))
                if action == "function":
                    calc.add(f"{value}(")
                    voice.speak(value)
                if action == "constant":
                    calc.add(value)
                    voice.speak(value)
                if action == "number":
                    calc.add(value)
                    voice.speak(str(value))

        # Push state to global variables for Web UI
        global_state["expression"] = calc.expression
        global_state["result"] = last_result
        global_state["history"] = [{"expr": h[0], "res": str(h[1])} for h in history_items]

        # Draw minimalistic overlay on the feed just in case, but Web UI will handle most
        # We just send the raw frame with NO overlay so the Web UI looks clean
        ret, buffer = cv2.imencode('.jpg', frame)
        if ret:
            latest_frame_bytes = buffer.tobytes()

    cap.release()

def main():
    print("\n" + "="*50)
    print("Starting AI Gesture Calculator Server...")
    print("The UI will open in your browser momentarily.")
    print("="*50 + "\n")
    
    t = threading.Thread(target=opencv_thread_func)
    t.daemon = True
    t.start()

    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5050')
    
    app.run(host='0.0.0.0', port=5050, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()
