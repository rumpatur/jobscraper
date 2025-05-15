import argparse

from constants import CSV_FORMAT, JSON_FORMAT, DB_FORMAT
from launcher import launch


def run():
    parser = argparse.ArgumentParser(description="Скрипт сбора данных о вакансиях в IT")

    parser.add_argument(
        "-o", "--output",
        choices=[CSV_FORMAT, JSON_FORMAT, DB_FORMAT],  # допустимые значения
        default=CSV_FORMAT,  # значение по умолчанию
        help=f"Формат сохранения данных ({CSV_FORMAT}, {JSON_FORMAT}, {DB_FORMAT})"
    )
    parser.add_argument("queries", nargs="+", help="Список запросов для поиска вакансий")

    args = parser.parse_args()

    print(f"Выгрузка данных в {args.output} по запросам: {', '.join(args.queries)}")

    launch(queries=args.queries, output=args.output)


if __name__ == '__main__':
    run()
