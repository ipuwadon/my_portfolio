from gold_price.load_price import scrape_gold_prices, transform_gold_prices, insert_into_mysql

import mysql.connector
import calendar

thai_months = {
    1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
    5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
    9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
}

def get_latest_date():
    conn = mysql.connector.connect(
        host="172.26.32.1",
        port=3306,
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

def build_next_url(latest_date):
    next_month = latest_date.month + 1
    next_year = latest_date.year
    if next_month > 12:
        next_month = 1
        next_year += 1
    buddhist_year = next_year + 543
    thai_month = thai_months[next_month]
    return f"https://xn--42cah7d0cxcvbbb9x.com/ราคาทองย้อนหลัง-เดือน-{thai_month}-{buddhist_year}/"