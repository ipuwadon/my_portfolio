import load_price
from load_price import (
    scrape_gold_prices, 
    transform_gold_prices, 
    insert_into_mysql, 
    get_latest_date, 
    build_next_url
)
print(dir(load_price))

def main():
    #url = "https://xn--42cah7d0cxcvbbb9x.com/ราคาทองย้อนหลัง-เดือน-กุมภาพันธ์-2563/"
    #url = "https://www.goldtraders.or.th/GoldPriceHistory.aspx?month=1&year=2563"

    latest_date = get_latest_date()
    url = build_next_url(latest_date)

    raw_text = scrape_gold_prices(url)
    print("Raw text sample:", raw_text[:200])

    df_daily = transform_gold_prices(raw_text)
    print("Transformed DataFrame:")
    print(df_daily.head())

    insert_into_mysql(df_daily)

if __name__ == "__main__":
    main()
