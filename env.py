
from os import getenv
from utils import load_dict
from constants import AVAILABLE_LOGGING_LEVELS


def get_logging_level(default: int = 5):
    out = default
    try:
        level = int(getenv("LOGGING_LEVEL", f"{default}"))
        assert level in AVAILABLE_LOGGING_LEVELS
        out = level * 10
    except:
        print("Reset to default logging level")
    print(f"Use logging level: {out}")
    return out


def get_secret_dict():
    o = getenv("SECRET_FILE", "secret.json")
    print(f"Use secret file: '{o}'")
    return load_dict(o)
