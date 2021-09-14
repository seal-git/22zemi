"""
pytest
"""

import os, yaml
with open(".flask-env.dev.yml", "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)
for key,value in config.items():
    os.environ[key] = str(value)
