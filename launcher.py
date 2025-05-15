import os
import time

from plugins.hh import get_data as hh_extractor
from plugins.habr import get_data as habr_extractor
from constants import CSV_FORMAT, JSON_FORMAT, DB_FORMAT, OUTPUT_DATA_FPATH
from writer import write_to_csv, write_to_sqlite, write_to_json


def pick_writer(output, chunk, first):
    if output == JSON_FORMAT:
        write_to_json(chunk)
    elif output == DB_FORMAT:
        write_to_sqlite(chunk, first)
    else:
        write_to_csv(chunk, first)


def process_query(first, func, output, query):
    count = 0
    for chunk in func(query):
        if count % 10 == 0:
            # Каждые десять запросов даем серверу отдохнуть от нас
            time.sleep(2)
            pick_writer(output, chunk, first)
        count += 1
        first = False


def launch(queries, output=CSV_FORMAT):
    if os.path.exists(f"{OUTPUT_DATA_FPATH}.{output}"):
        os.remove(f"{OUTPUT_DATA_FPATH}.{output}")
    first = True

    for query in queries:
        process_query(first, hh_extractor, output, query)
        first = False
        process_query(first, habr_extractor, output, query)


if __name__ == '__main__':
    launch(["python", "php", "rust"])

