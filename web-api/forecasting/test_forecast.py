from forecasting.prophet_model import forecast_gold_prices

def main():
    forecast = forecast_gold_prices(periods=2)

    for row in forecast[-10:]:
        print(row)

if __name__ == "__main__":
    main()