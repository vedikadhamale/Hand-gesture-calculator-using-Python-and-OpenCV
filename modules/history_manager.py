import json
import os


class HistoryManager:
    def __init__(self, filename="history.json"):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.file = os.path.join(data_dir, filename)

    def save(self, expression, result):
        data = self.load()
        data.append(f"{expression} = {result}")

        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self):
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def tail(self, limit=5):
        data = self.load()
        return data[-limit:]
