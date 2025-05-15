import os.path
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DATA_DIR = str(BASE_DIR / "data")

if not os.path.isdir(OUTPUT_DATA_DIR):
    os.mkdir(OUTPUT_DATA_DIR)

OUTPUT_DATA_FPATH = str(BASE_DIR / "data" / "vacancies")

OUTPUT_CHARTS_DIR = str(BASE_DIR / "charts")

SOURCE_HABR = "habr"
SOURCE_HH = "hh"

# SQLITE
VACANCIES_TABLE = "vacancies"

# OUTPUTS
CSV_FORMAT = "csv"
JSON_FORMAT = "json"
DB_FORMAT = "db"