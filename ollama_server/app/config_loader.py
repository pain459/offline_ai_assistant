import yaml
import os

# __all__ = ["get_num_predict"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "config.yaml")

def load_config():
    with open(path, "r") as f:
        return yaml.safe_load(f)

_config = load_config()

def get_num_predict_for(dataset: str | None) -> int:
    if dataset and dataset in _config.get("datasets", {}):
        return _config["datasets"][dataset].get("num_predict", _config["default"]["num_predict"])
    return _config["default"]["num_predict"]
