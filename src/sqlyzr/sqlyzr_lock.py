import os
import atexit
import signal

SQLYZR_LOCK_PATH = "/tmp/sqlyzr.lock"


class SqlyzrLock:
    @staticmethod
    def setup_signals():
        atexit.register(SqlyzrLock.__cleanup)
        signal.signal(signal.SIGTERM, SqlyzrLock.__cleanup_and_exit)
        signal.signal(signal.SIGINT, SqlyzrLock.__cleanup_and_exit)

    def __enter__(self):
        if os.path.exists(SQLYZR_LOCK_PATH):
            raise RuntimeError(f"SQLyzr lock exists!: {SQLYZR_LOCK_PATH}")
        with open(SQLYZR_LOCK_PATH, 'w') as f:
            f.write(f"{os.getpid()}")
        return self

    @staticmethod
    def __cleanup_and_exit(signum, frame):
        SqlyzrLock.__cleanup()
        exit(signum)

    @staticmethod
    def __cleanup():
        if os.path.exists(SQLYZR_LOCK_PATH):
            try:
                os.remove(SQLYZR_LOCK_PATH)
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"Warning: failed to remove lock file: {e}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        SqlyzrLock.__cleanup()
