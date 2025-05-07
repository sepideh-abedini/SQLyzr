import platform

from src.sqlyzr.sqlyzr_lock import SqlyzrLock
from src.util.log_util import configure_logging
import multiprocessing as mp


def setup_app():
    configure_logging()
    SqlyzrLock.setup_signals()
    if platform.system() == "Linux":
        mp.set_start_method("spawn", force=True)
