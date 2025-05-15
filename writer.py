import json
import sqlite3

import pandas as pd

from constants import OUTPUT_DATA_FPATH, VACANCIES_TABLE
import fields as fld


def write_to_csv(chunk, is_first):
    pd.DataFrame(chunk).to_csv(f"{OUTPUT_DATA_FPATH}.csv", mode="a", header=is_first, index=False)


def write_to_json(chunk):
    with open(f"{OUTPUT_DATA_FPATH}.json", "a", encoding="utf-8") as handler:
        for item in chunk:
            json.dump(item, handler, ensure_ascii=False, indent=None)
            handler.write("\n")


def write_to_sqlite(chunk, is_first):
    with sqlite3.connect(f"{OUTPUT_DATA_FPATH}.db") as conn:
        cursor = conn.cursor()

        if is_first:
            # Создаем таблицу (если её нет)
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {VACANCIES_TABLE} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {fld.VACANCY_ID} TEXT UNIQUE,
                    {fld.QUERY} TEXT NOT NULL,
                    {fld.VACANCY_TITLE} TEXT,
                    {fld.LOCATIONS} TEXT,
                    {fld.SALARY_RANGE_FROM} REAL,
                    {fld.SALARY_RANGE_TO} REAL,
                    {fld.CURRENCY} TEXT,
                    {fld.PUBLISHED_AT} TEXT,
                    {fld.EMPLOYER} TEXT,
                    {fld.DETAILS_URL} TEXT,
                    {fld.DATE_ADDED} TEXT,
                    {fld.SOURCE} TEXT
                )"""
            )
        place_holders = ", ".join(["?" for _ in fld.ALL_FIELDS])
        values = list()
        for item in chunk:
            values.append(tuple([item[field] for field in fld.ALL_FIELDS]))
        cursor.executemany(
            f"INSERT OR IGNORE INTO {VACANCIES_TABLE} {fld.ALL_FIELDS} VALUES ({place_holders})",
            values
        )
        conn.commit()

