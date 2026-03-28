import multiprocessing as mp
import platform


def setup_app():
    if platform.system() == "Linux":
        mp.set_start_method("spawn", force=True)
