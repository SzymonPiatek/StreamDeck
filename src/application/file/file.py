import json
import os


class File:
    def __init__(self, path):
        self.path = path


class JSONFile(File):
    def __init__(self, path):
        super().__init__(path)

        self.indent = 2

    def ensure_file_exists(self):
        if not os.path.exists(self.path) or os.stat(self.path).st_size == 0:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=self.indent, ensure_ascii=False)

    def save_file(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=self.indent, ensure_ascii=False)

    def load_file(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
