import os.path
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from constants import OUTPUT_CHARTS_DIR, OUTPUT_DATA_FPATH, VACANCIES_TABLE
import fields as fld


def get_salary_data(db_path):
    """Берем нужные записи и возвращаем датафрейм"""
    with sqlite3.connect(db_path) as conn:
        query = f"""
        SELECT 
            {fld.SALARY_RANGE_FROM},
            {fld.SALARY_RANGE_TO},
            {fld.CURRENCY},
            {fld.QUERY}
        FROM {VACANCIES_TABLE}
        WHERE ({fld.SALARY_RANGE_FROM} IS NOT NULL OR {fld.SALARY_RANGE_TO} IS NOT NULL)
        AND {fld.CURRENCY} IS NOT NULL
        AND {fld.CURRENCY} IN ("rur", "RUR")
        """

        return pd.read_sql(query, conn)


def calculate_avg_salary(row):
    """Рассчитываем среднюю зарплату с учетом неполных данных"""
    salary_from = row[fld.SALARY_RANGE_FROM]
    salary_to = row[fld.SALARY_RANGE_TO]

    if salary_from > 0 and salary_to > 0:
        return (salary_from + salary_to) / 2
    elif salary_from > 0:
        return salary_from
    elif salary_to > 0:
        return salary_to


def prepare_salary_data(df):
    """Преобразуем данные для графика"""
    df[fld.SALARY_RANGE_FROM] = pd.to_numeric(df[fld.SALARY_RANGE_FROM])
    df[fld.SALARY_RANGE_TO] = pd.to_numeric(df[fld.SALARY_RANGE_TO])

    # Фильтруем явные выбросы (например, зарплаты < 1000 или > 1 млн)
    df = df[(df[fld.SALARY_RANGE_FROM] > 1000) & (df[fld.SALARY_RANGE_TO] < 1_000_000)]

    df['avg_salary'] = df.apply(calculate_avg_salary, axis=1)

    # Фильтруем записи, где удалось рассчитать зарплату
    df = df[df['avg_salary'].notna()]

    return df


def plot_salary_distribution(df):
    """Строим график распределения зарплат"""
    plt.figure(figsize=(12, 6))

    # Boxplot по источникам (HH vs Habr)
    sns.boxplot(
        x='avg_salary',
        y=fld.QUERY,
        data=df,
        orient='h',
        showfliers=False  # Не показывать выбросы
    )

    plt.title(f"Распределение зарплат")
    plt.xlabel("Средняя зарплата (руб.)")
    plt.ylabel("Специализация")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_CHARTS_DIR, "salary_distribution.png"), dpi=300)
    plt.close()


def get_salary_ranges_data(db_path):
    """Берем только записи, где есть полная вилка, и возвращаем датафрейм"""
    with sqlite3.connect(db_path) as conn:
        query = f"""
        SELECT 
            {fld.SALARY_RANGE_FROM},
            {fld.SALARY_RANGE_TO},
            {fld.QUERY}
        FROM {VACANCIES_TABLE}
        WHERE {fld.SALARY_RANGE_FROM} IS NOT NULL
        AND {fld.SALARY_RANGE_TO} IS NOT NULL
        AND {fld.SALARY_RANGE_TO} < 1000000
        AND {fld.CURRENCY} IN ("rur", "RUR")
        """
        return pd.read_sql(query, conn)


def plot_salary_ranges(df, top_n=10):
    """Строим график сравнения зарплатных вилок для топ-N запросов
    """
    # Рассчитываем вилку и среднюю зарплату
    df["range"] = df[fld.SALARY_RANGE_TO] - df[fld.SALARY_RANGE_FROM]
    df["avg"] = (df[fld.SALARY_RANGE_FROM] + df[fld.SALARY_RANGE_TO]) / 2

    # Берем топ-N языков по количеству вакансий
    top_queries = df[fld.QUERY].value_counts().head(top_n).index
    df = df[df[fld.QUERY].isin(top_queries)]

    # Строим график
    plt.figure(figsize=(12, 8))
    sns.stripplot(
        x="avg",
        y=fld.QUERY,
        hue="range",
        data=df,
        size=8,
        palette="viridis",
        alpha=0.7,
        jitter=True
    )

    # Настройки отображения
    plt.title(f"Зарплатные вилки для топ-{top_n} языков (рубли)")
    plt.xlabel("Средняя зарплата (руб.)")
    plt.ylabel("Язык/технология")
    plt.legend(title="Размер вилки", bbox_to_anchor=(1.05, 1))
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Сохранение
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_CHARTS_DIR, "salary_ranges.png"), dpi=120, bbox_inches="tight")
    plt.close()


if __name__ == '__main__':
    plot_salary_distribution(prepare_salary_data(get_salary_data(f"{OUTPUT_DATA_FPATH}.db")))
    # plot_salary_ranges(get_salary_ranges_data(f"{OUTPUT_DATA_FPATH}.db"))