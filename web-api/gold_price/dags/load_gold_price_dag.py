from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
from gold_price.load_gold import (
    scrape_gold_prices,
    transform_gold_prices,
    insert_into_mysql,
    get_latest_date,
    build_next_url
)
import pandas as pd
from io import StringIO

def scrape_task(**context):
    latest_date = get_latest_date()
    next_url = build_next_url(latest_date)
    print("Next URL:", next_url)

    raw_text = scrape_gold_prices(next_url)
    print("Raw text length:", len(raw_text) if raw_text else None)
    print("Raw text sample:", raw_text[:200] if raw_text else None)

    if not raw_text:
        raise ValueError(f"scrape_gold_prices returned None for {next_url}")
    return raw_text

def transform_task(**context):
    raw_text = context['ti'].xcom_pull(task_ids='scrape')
    print("Pulled raw_text length:", len(raw_text) if raw_text else None)

    if not raw_text:
        raise ValueError("No raw_text found in XCom")

    df_daily = transform_gold_prices(raw_text)
    print("DataFrame head:\n", df_daily.head())

    # reset index + orient='records'
    return df_daily.reset_index(drop=True).to_json(orient='records')

def insert_task(**context):
    df_json = context['ti'].xcom_pull(task_ids='transform')
    if not df_json:
        raise ValueError("No df_daily found in XCom")

    # Parse JSON string
    df_daily = pd.read_json(StringIO(df_json), orient='records')
    print("DataFrame loaded for insert:\n", df_daily.head())

    # Convert timestamp (ms) → datetime string
    if "datetime_clean" in df_daily.columns:
        df_daily["datetime_clean"] = pd.to_datetime(
            df_daily["datetime_clean"], unit="ms"
        ).dt.strftime("%Y-%m-%d %H:%M:%S")

    insert_into_mysql(df_daily)

with DAG(
    dag_id="load_gold_price_dag",
    start_date=datetime(2026, 3, 3),
    schedule="*/15 * * * *",   # run every 15 minutes
    catchup=False,
) as dag:

    scrape = PythonOperator(
        task_id="scrape",
        python_callable=scrape_task
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_task
    )

    insert = PythonOperator(
        task_id="insert_mysql",
        python_callable=insert_task
    )

    scrape >> transform >> insert