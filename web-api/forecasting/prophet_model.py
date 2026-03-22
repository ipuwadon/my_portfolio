import pandas as pd
from prophet import Prophet
from db.gold_price import get_gold_prices

def forecast_gold_prices(periods: int = 10):
    # 1. Load data
    data = get_gold_prices()
    df = pd.DataFrame(data)

    # 2. Rename columns for Prophet
    df = df.rename(columns={"date": "ds"})
    # ใช้ค่าเฉลี่ยระหว่าง buy/sell เพื่อสะท้อนราคาตลาดจริง
    df["y"] = (df["gold_bar_buy"] + df["gold_bar_sell"]) / 2

    # 3. Clean outliers (ตัดค่าที่ <= 0)
    df = df[df["y"] > 0]

    # 4. Smooth series เพื่อลดผลกระทบจาก outlier
    df["y"] = df["y"].rolling(window=3, min_periods=1).mean()

    # 5. สร้าง Prophet model พร้อม parameter ที่ปรับแล้ว
    model = Prophet(
        changepoint_prior_scale=0.05,   # ลดความยืดหยุ่นของ trend
        seasonality_mode="additive",    # ใช้ additive seasonality
        yearly_seasonality=True,
        weekly_seasonality=False,       # ปิด weekly ถ้าไม่มี pattern ชัดเจน
        daily_seasonality=False,
        interval_width=0.95             # ขยายช่วงความเชื่อมั่น
    )

    # 6. Fit model
    model.fit(df)

    # 7. สร้าง future dataframe
    future = model.make_future_dataframe(periods=periods)

    # 8. Predict
    forecast = model.predict(future)
    future_forecast = forecast.tail(periods)

    # 9. Return forecast records
    return future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_dict(orient="records")