"""
pytest
"""

from app import config

for key, value in config.TestConfig.__dict__.items():
    if not key.startswith("__"): print(f"{key}: {value}")

