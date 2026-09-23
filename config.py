import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def raise_error(message: str):
    raise RuntimeError(message)



# Environement Variables
# Weather
LAT= os.getenv("LAT") or raise_error("LAT is missing in .env")

LON= os.getenv("LON") or raise_error("LON is missing in .env")

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
