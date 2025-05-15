import datetime
import os
import requests
from tqdm import tqdm

from constants import SOURCE_HH
import fields as fld
from private import HH_URL


def get_data(query):
    params = {
        "text": query,
        "per_page": 100,
        "page": 0,
        "industry": 7,  # IT
        # "area": 1,  # Москва
        "period": 7,  # за последние 7 дней
        "order_by": "publication_time",
    }
    response = requests.get(HH_URL, params=params)
    data = response.json()
    total_pages = data.get('pages')

    # print(f"per_page: {data.get('per_page')}")
    # print(f"pages: {total_pages}")
    print(f"Сбор данных с HH по запросу {query}")
    print(f"Найдено записей: {data.get('found')}")

    for _ in tqdm(range(total_pages)):
        response = requests.get(HH_URL, params=params)
        data = response.json()
        items = data.get("items", [])
        if not items:
            break
        results = list()

        for item in items:
            salary_range = item.get("salary_range", {})
            if salary_range is None:
                salary_range = {}
            employer = item.get("employer", {})
            item_data = {
                fld.VACANCY_ID: item.get("id"),
                fld.QUERY: query,
                fld.VACANCY_TITLE: item.get("name"),
                fld.LOCATIONS: item.get("area", {}).get("name"),
                fld.SALARY_RANGE_FROM: salary_range.get("from"),
                fld.SALARY_RANGE_TO: salary_range.get("to"),
                fld.CURRENCY: salary_range.get("currency"),
                fld.PUBLISHED_AT: item.get("published_at"),
                fld.EMPLOYER: employer.get("name"),
                fld.DETAILS_URL: item.get("url"),
                fld.DATE_ADDED: str(datetime.datetime.now()),
                fld.SOURCE: SOURCE_HH,
            }
            results.append(item_data)
        params["page"] += 1
        yield results


if __name__ == '__main__':
    get_data("python")