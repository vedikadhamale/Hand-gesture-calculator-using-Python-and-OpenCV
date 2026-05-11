import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

# ------------------- Emoji Support -------------------
EMOJI_FONT_PATHS = [
    "C:/Windows/Fonts/seguiemj.ttf",
    "C:/Windows/Fonts/seguiemoji.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
]

EMOJI_FONT_CACHE = {}

def get_emoji_font(size):
    if size not in EMOJI_FONT_CACHE:
        font_loaded = False
        for font_path in EMOJI_FONT_PATHS:
            if os.path.exists(font_path):
                try:
                    EMOJI_FONT_CACHE[size] = ImageFont.truetype(font_path, size)
                    font_loaded = True
                    break
                except:
                    continue
        if not font_loaded:
            EMOJI_FONT_CACHE[size] = ImageFont.load_default()
    return EMOJI_FONT_CACHE[size]

def draw_text_with_emoji(frame, text, position, size=24, color=(255,255,255)):
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = get_emoji_font(size)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def draw_rounded_rect(img, x1, y1, x2, y2, r, color, thickness=-1, alpha=0.85):
    overlay = img.copy()
    
    if thickness < 0:
        cv2.rectangle(overlay, (x1+r, y1), (x2-r, y2), color, -1)
        cv2.rectangle(overlay, (x1, y1+r), (x2, y2-r), color, -1)
        cv2.circle(overlay, (x1+r, y1+r), r, color, -1)
        cv2.circle(overlay, (x2-r, y1+r), r, color, -1)
        cv2.circle(overlay, (x2-r, y2-r), r, color, -1)
        cv2.circle(overlay, (x1+r, y2-r), r, color, -1)
    else:
        cv2.line(overlay, (x1+r, y1), (x2-r, y1), color, thickness)
        cv2.line(overlay, (x1+r, y2), (x2-r, y2), color, thickness)
        cv2.line(overlay, (x1, y1+r), (x1, y2-r), color, thickness)
        cv2.line(overlay, (x2, y1+r), (x2, y2-r), color, thickness)
        cv2.circle(overlay, (x1+r, y1+r), r, color, thickness)
        cv2.circle(overlay, (x2-r, y1+r), r, color, thickness)
        cv2.circle(overlay, (x2-r, y2-r), r, color, thickness)
        cv2.circle(overlay, (x1+r, y2-r), r, color, thickness)
    
    cv2.addWeighted(overlay, alpha, img, 1-alpha, 0, img)

class CalculatorUI:
    def __init__(self):
        self.expression = ""
        self.result = ""
        self.history = []
        self.voice_status = "off"
        
    def draw(self, frame, expression="", result="", detected_label=None, voice_status="off", history=None):
        """Main draw method called from main.py"""
        h, w = frame.shape[:2]
        panel_w = 380
        
        # Draw dark theme background on left panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (panel_w, h), (20, 25, 35), -1)
        cv2.addWeighted(overlay, 0.88, frame, 0.12, 0, frame)
        
        # Title with emoji
        frame = draw_text_with_emoji(frame, "🤖 AI Gesture Calculator", (20, 40), 26, (100, 200, 255))
        
        # Voice status
        status_color = (100, 255, 100) if voice_status == "on" else (150, 150, 150)
        cv2.putText(frame, f"🎤 Voice: {voice_status.upper()}", (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 1)
        
        # Expression section
        cv2.putText(frame, "📝 EXPRESSION", (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 220), 1)
        draw_rounded_rect(frame, 20, 120, panel_w-20, 165, 10, (10, 15, 28), -1, 0.95)
        
        expr_text = expression if expression else "0"
        # Handle long expressions
        if len(expr_text) > 25:
            expr_text = "..." + expr_text[-22:]
        cv2.putText(frame, expr_text, (30, 152),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (100, 255, 150), 2)
        
        # Result section
        cv2.putText(frame, "🎯 RESULT", (20, 195),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 220), 1)
        draw_rounded_rect(frame, 20, 205, panel_w-20, 250, 10, (10, 15, 28), -1, 0.95)
        
        result_text = result if result else "= ?"
        cv2.putText(frame, result_text, (30, 237),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 200, 100), 2)
        
        # Detected gesture display
        y = 280
        if detected_label:
            draw_rounded_rect(frame, 20, y, panel_w-20, y+55, 12, (40, 50, 75), -1, 0.9)
            frame = draw_text_with_emoji(frame, f"🔍 {detected_label}", (35, y+25), 17, (200, 220, 255))
            y += 65
        
        # Instructions title
        y += 10
        cv2.putText(frame, "📖 GESTURE INSTRUCTIONS", (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, (100, 200, 255), 2)
        
        # Gesture instruction list
        instructions = [
            ("✊ Fist", "→ 0"),
            ("☝️ One Finger", "→ 1"),
            ("✌️ Two Fingers", "→ 2"),
            ("🤟 Three Fingers", "→ 3"),
            ("🖖 Four Fingers", "→ 4"),
            ("🖐️ Open Hand", "→ 5"),
            ("👍 Thumb + Index", "→ +"),
            ("👍 Thumb + Middle", "→ -"),
            ("👍 Thumb + Ring", "→ *"),
            ("👍 Thumb + Pinky", "→ /"),
            ("🖐️ All Fingers Spread", "→ ="),
            ("✌️ Victory Hold", "→ Clear"),
        ]
        
        y += 30
        for gesture, action in instructions:
            if y + 25 > h - 100:
                break
            frame = draw_text_with_emoji(frame, f"{gesture}  {action}", (25, y), 14, (180, 210, 240))
            y += 20
        
        # History section
        if history and len(history) > 0:
            y = h - 95
            cv2.putText(frame, "📜 HISTORY", (20, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (150, 150, 200), 1)
            y += 20
            for item in history[-4:]:
                if y < h - 10:
                    # Truncate long history items
                    display_item = item if len(item) < 30 else item[:27] + "..."
                    cv2.putText(frame, display_item, (25, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 200), 1)
                    y += 18
        
        # Keyboard shortcuts
        cv2.putText(frame, "⌨️ [C] Clear  [Bksp] Del  [0-9] Num  [+-*/] Op  [Q] Quit", 
                    (20, h-12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 120), 1)
        
        # Draw camera area border on right side
        cv2.rectangle(frame, (panel_w+15, 10), (w-10, h-10), (50, 150, 200), 2)
        cv2.putText(frame, "📷 CAMERA AREA", (panel_w+30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 200, 255), 1)
        cv2.putText(frame, "Show your hand here", (panel_w+30, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 180), 1)
        
        # Draw corner decorations
        corner_size = 20
        cv2.line(frame, (panel_w+15, 10), (panel_w+15+corner_size, 10), (0, 200, 255), 2)
        cv2.line(frame, (panel_w+15, 10), (panel_w+15, 10+corner_size), (0, 200, 255), 2)
        cv2.line(frame, (w-10, 10), (w-10-corner_size, 10), (0, 200, 255), 2)
        cv2.line(frame, (w-10, 10), (w-10, 10+corner_size), (0, 200, 255), 2)
        cv2.line(frame, (panel_w+15, h-10), (panel_w+15+corner_size, h-10), (0, 200, 255), 2)
        cv2.line(frame, (panel_w+15, h-10), (panel_w+15, h-10-corner_size), (0, 200, 255), 2)
        cv2.line(frame, (w-10, h-10), (w-10-corner_size, h-10), (0, 200, 255), 2)
        cv2.line(frame, (w-10, h-10), (w-10, h-10-corner_size), (0, 200, 255), 2)
        
        return frame