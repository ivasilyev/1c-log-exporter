
import os
import logging
from utils import load_dict
from constants import AVAILABLE_LOGGING_LEVELS


def get_logging_level(default: int = 5):
    out = default
    try:
        level = int(os.getenv("LOGGING_LEVEL", f"{default}"))
        assert level in AVAILABLE_LOGGING_LEVELS
        out = level * 10
    except:
        logging.debug("Reset to default logging level")
    logging.debug(f"Use logging level: {out}")
    return out


def get_secret_dict():
    o = os.getenv(
        "SECRET_FILE",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "secret.json")
    )
    logging.debug(f"Use secret file: '{o}'")
    return load_dict(o)
