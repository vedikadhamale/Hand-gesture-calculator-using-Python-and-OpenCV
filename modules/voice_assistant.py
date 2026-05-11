import os
import queue

# Use a user-writable cache so pyttsx3/comtypes can generate typelibs
# without requiring admin write access to site-packages.
_preferred_cache = os.path.join(
    os.getenv("LOCALAPPDATA", os.path.join(os.getcwd(), ".cache")),
    "comtypes_cache",
)
_fallback_cache = os.path.join(os.getcwd(), ".comtypes_cache")

_comtypes_cache = _preferred_cache
try:
    os.makedirs(_comtypes_cache, exist_ok=True)
except PermissionError:
    _comtypes_cache = _fallback_cache
    os.makedirs(_comtypes_cache, exist_ok=True)

os.environ.setdefault("COMTYPES_CACHE", _comtypes_cache)

import pyttsx3
try:
    import comtypes.client
    import comtypes.gen

    comtypes.client.gen_dir = _comtypes_cache
    comtypes.gen.__path__ = [_comtypes_cache]
except Exception:
    pass

try:
    import speech_recognition as sr
except Exception:
    sr = None


class VoiceAssistant:
    def __init__(self, enable_listen=True):
        self.engine = None
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 150)
        except Exception as exc:
            print(f"Voice output disabled: {exc}")

        self._command_queue = queue.Queue()
        self._recognizer = sr.Recognizer() if sr and enable_listen else None
        self._mic = None
        self._listener = None
        self._listening = False

        if self._recognizer:
            try:
                self._mic = sr.Microphone()
            except Exception:
                self._recognizer = None
                self._mic = None

    def speak(self, text):
        print("AI:", text)
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()

    def listening_available(self):
        return bool(self._recognizer and self._mic)

    @property
    def is_listening(self):
        return self._listening

    def start_listening(self, phrase_time_limit=4):
        if not self.listening_available() or self._listening:
            return False

        def _callback(recognizer, audio):
            try:
                text = recognizer.recognize_google(audio)
                if text:
                    self._command_queue.put(text.lower())
            except Exception:
                pass

        self._listener = self._recognizer.listen_in_background(
            self._mic, _callback, phrase_time_limit=phrase_time_limit
        )
        self._listening = True
        return True

    def stop_listening(self):
        if self._listener:
            self._listener(wait_for_stop=False)
        self._listener = None
        self._listening = False

    def pop_command(self):
        try:
            return self._command_queue.get_nowait()
        except queue.Empty:
            return None
