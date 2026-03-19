import os.path

OUT_DIR = "/tmp/output"
os.makedirs(OUT_DIR, exist_ok=True)

class Messanger:
    def __init__(self, pid=None):
        if not pid:
            pid = os.getpid()
        self.pid = pid

    @property
    def file_path(self):
        return os.path.join(OUT_DIR, f"{self.pid}")

    def write(self, msg):
        with open(self.file_path, "w") as f:
            f.write(msg)

    def read(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                return f.read()
        return None
