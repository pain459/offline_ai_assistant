"""
Purpose:
This module loads prediction configuration from `config.yaml` and exposes
a utility function `get_num_predict_for()` to retrieve the `num_predict` value
(i.e., maximum number of tokens to generate) for a given dataset.
"""

import yaml
import os

# Get the absolute path to the current file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the configuration YAML file
path = os.path.join(BASE_DIR, "config.yaml")

# Load the YAML configuration once and reuse it globally
def load_config():
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Parse the YAML config and store it for access
_config = load_config()

# Retrieve the `num_predict` value for a specific dataset
# Falls back to the default value if the dataset is not defined
def get_num_predict_for(dataset: str | None) -> int:
    if dataset and dataset in _config.get("datasets", {}):
        return _config["datasets"][dataset].get("num_predict", _config["default"]["num_predict"])
    return _config["default"]["num_predict"]
