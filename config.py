import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def raise_error(message: str):
    """
    Raise error if a .env var is unassigned
    """
    raise RuntimeError(message)

def number_type_check(**kwargs):
    """
    Check if .env values for numbers are numbers, else : raise error
    """
    for key, value in kwargs.items():
        try:
            float(value)
        except ValueError as e:
            raise TypeError(f"The value {value} for key {key} must be a float or int in .env") from e

# Environement Variables
# Weather
LAT= os.getenv("LAT") or raise_error("LAT is missing in .env")
LON= os.getenv("LON") or raise_error("LON is missing in .env")

number_type_check(LAT=LAT, LON=LON)

# ICAL calendar
ICAL_URL = os.getenv("ICAL_URL") or raise_error("ICAL Url is missing in .env")


# Paths
BASE_DIR = Path(__file__).resolve().parent
## data
DB_PATH = BASE_DIR / "data" / "display.db"
CAL_TXT_PATH = BASE_DIR / "data" / "calendar.txt"
## front
INDEX_PATH = BASE_DIR / "front" / "index.html"
JS_SCRIPT_PATH = BASE_DIR / "front" / "script.js"
