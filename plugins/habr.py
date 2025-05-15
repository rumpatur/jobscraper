import datetime

import requests
from tqdm import tqdm

from constants import SOURCE_HABR
import fields as fld
from private import HABR_URL


def get_data(query):
    params = {
        "q": query,
        "per_page": 50,
        "page": 1,
        "sort": "relevance",
    }
    response = requests.get(HABR_URL, params=params)
    data = response.json()

    meta = data.get("meta", {})
    total_pages = meta.get('totalPages')

    print(f"Сбор данных с Хабр Карьеры по запросу {query}")
    print(f"Найдено записей: {meta.get('totalResults')}")

    # print(f"per_page: {meta.get('perPage')}")
    # print(f"pages: {total_pages}")
    # print(f"found: {meta.get('totalResults')}")
    # print(f"current page: {meta.get('currentPage')}")

    for _ in tqdm(range(total_pages)):
        response = requests.get(HABR_URL, params=params)
        data = response.json()
        items = data.get("list", [])
        if not items:
            break
        results = list()

        for item in items:
            salary_range = item.get("salary", {})
            if salary_range is None:
                salary_range = {}
            employer = item.get("company", {})
            locations = item.get("locations", [])
            if locations is None:
                locations = list()
            loc_names = [loc.get("title") for loc in locations]
            item_data = {
                fld.VACANCY_ID: item.get("id"),
                fld.QUERY: query,
                fld.VACANCY_TITLE: item.get("title"),
                fld.LOCATIONS: ", ".join(loc_names),
                fld.SALARY_RANGE_FROM: salary_range.get("from"),
                fld.SALARY_RANGE_TO: salary_range.get("to"),
                fld.CURRENCY: salary_range.get("currency"),
                fld.PUBLISHED_AT: item.get("publishedDate", {}).get("date"),
                fld.EMPLOYER: employer.get("title"),
                fld.DETAILS_URL: f"https://career.habr.com{item.get('href')}",
                fld.DATE_ADDED: str(datetime.datetime.now()),
                fld.SOURCE: SOURCE_HABR,
            }
            results.append(item_data)
        params["page"] += 1
        yield results


if __name__ == '__main__':
    get_data("python")