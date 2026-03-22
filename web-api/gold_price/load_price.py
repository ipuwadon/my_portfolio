import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector
from mysql.connector import Error

def get_latest_date():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="153289",
        database="portfolio"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(date) FROM gold_prices_daily")
    latest = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    return latest

thai_months = {
    1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
    5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
    9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
}

def build_next_url(latest_date):
    next_month = latest_date.month + 1
    next_year = latest_date.year

    if next_month > 12:
        next_month = 1
        next_year += 1

    buddhist_year = next_year + 543
    thai_month = thai_months[next_month]

    return f"https://xn--42cah7d0cxcvbbb9x.com/ราคาทองย้อนหลัง-เดือน-{thai_month}-{buddhist_year}/"

def scrape_gold_prices(url: str) -> str:
    """
    Scrape raw text from the gold price table on the given URL.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.select_one("table.table.table-condensed")
    raw_text = table.get_text(" ", strip=True)
    return raw_text


def transform_gold_prices(raw_text: str) -> pd.DataFrame:
    """
    Transform raw text into a cleaned DataFrame with daily open/close records.
    Includes regex extraction, Buddhist→Gregorian conversion, and numeric cleaning.
    """
    # Regex pattern: DateTime + 7 numeric values
    pattern = (
        r"(\d{2}/\d{2}/\d{4}\s\d{2}:\d{2})\s+"   # raw_datetime
        r"([\d,\.]+)\s+"                         # price_change
        r"([\d,\.]+)\s+"                         # Gold Bar Buy
        r"([\d,\.]+)\s+"                         # Gold Bar Sell
        r"([\d,\.]+)\s+"                         # Ornament Buy
        r"([\d,\.]+)\s+"                         # Ornament Sell
        r"([\d,\.]+)\s+"                         # Gold Spot
        r"([\d,\.]+)"                            # Exchange Rate
    )

    matches = re.findall(pattern, raw_text)

    # Create DataFrame
    df = pd.DataFrame(matches, columns=[
        "raw_datetime", "price_change",
        "Gold Bar Buy", "Gold Bar Sell",
        "Ornament Buy", "Ornament Sell",
        "Gold Spot", "Exchange Rate"
    ])

    # Convert Buddhist calendar year → Gregorian year
    def convert_buddhist_to_gregorian(dt_str):
        try:
            date_part, time_part = dt_str.split(" ")
            d, m, y = date_part.split("/")
            y = str(int(y) - 543)  # 2563 → 2020
            return f"{d}/{m}/{y} {time_part}"
        except Exception:
            return None

    df["datetime_clean"] = df["raw_datetime"].apply(convert_buddhist_to_gregorian)
    df["datetime_clean"] = pd.to_datetime(df["datetime_clean"], dayfirst=True, errors="coerce")
    df["date"] = df["datetime_clean"].dt.date

    # Clean numeric values
    for col in ["price_change","Gold Bar Buy","Gold Bar Sell","Ornament Buy","Ornament Sell","Gold Spot","Exchange Rate"]:
        df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors="coerce")

    # Select first (Open) and last (Close) row of each day
    df_open = df.sort_values("datetime_clean").groupby("date").head(1)
    df_close = df.sort_values("datetime_clean").groupby("date").tail(1)

    df_daily = pd.concat([df_open.assign(session="Open"), df_close.assign(session="Close")])
    df_daily = df_daily.sort_values(["date","session"])

    return df_daily


def insert_into_mysql(df_daily: pd.DataFrame):
    """
    Insert the transformed daily gold price data into MySQL.
    Deletes existing records for those dates before inserting new ones.
    """
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
                host="172.26.32.1",
                port=3306,
                user="root",
                password="153289",
                database="portfolio"
            )
        cursor = conn.cursor()

        # Delete old records for all dates in the batch
        for d in df_daily['date'].unique():
            cursor.execute("DELETE FROM gold_prices_daily WHERE date = %s", (d,))

        # Insert new records
        insert_query = """
        INSERT INTO gold_prices_daily 
        (raw_datetime, datetime_clean, date, session, 
         gold_bar_buy, gold_bar_sell, 
         ornament_buy, ornament_sell, 
         gold_spot, exchange_rate, price_change, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """

        for _, row in df_daily.iterrows():
            cursor.execute(insert_query, (
                row['raw_datetime'],      # raw_datetime
                row['datetime_clean'],    # datetime_clean
                row['date'],              # date
                row['session'],           # session
                row['Gold Bar Buy'],
                row['Gold Bar Sell'],
                row['Ornament Buy'],
                row['Ornament Sell'],
                row['Gold Spot'],
                row['Exchange Rate'],
                row['price_change']       # price_change
            ))

        conn.commit()
        print(f"Successfully saved {len(df_daily)} records to MySQL database")

    except Error as err:
        print(f"Error: {err}")
    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection is closed")
