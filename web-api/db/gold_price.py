import mysql.connector

def get_gold_prices():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="153289",
        database="portfolio"
    )
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT date, DATE_FORMAT(date, '%Y') AS year, DATE_FORMAT(date, '%m') AS month, gold_bar_buy, gold_bar_sell, gold_spot FROM portfolio.gold_prices_daily where session = 'Close' ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows