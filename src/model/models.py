from src.sqlyzr.custom_runner import CustomRunner
from src.sqlyzr.model_runner import DinRunner, DailRunner, DummyRunner

MODELS = {
    "din": DinRunner(),
    "dail": DailRunner(),
    "dum": DummyRunner(),
    "custom": CustomRunner()
}
