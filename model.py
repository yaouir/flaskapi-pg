import datetime
from pathlib import Path

import joblib
import pandas as pd 
import yfinance as yf
from prophet import Prophet 

BASE_DIR = Path(__file__).resolve(strict=True).parent
TODAY = datetime.date.today()

def train(ticker= 'MSFT'):
    data = yf.download(ticker, "2020-01-01", TODAY.strftime('%Y-%m-%d'))
    data.head()
    data["Adj Close"].plot(title = f"{ticker} stock Adjusted Clsoing Price")
    
    df_forcast = data.copy()
    df_forcast.reset_index(inplace=True)
    df_forcast["ds"] = df_forcast["Date"]
    df_forcast["y"] = df_forcast["Adj Close"]
    df_forcast = df_forcast[["ds", "y"]]
    df_forcast

    model = Prophet()
    model.fit(df_forcast)

    joblib.dump(model, Path(BASE_DIR).joinpath(f"{ticker}.joblib"))


def predict(ticker = 'MSFT', days = 7):
    model_file = Path(BASE_DIR).joinpath(f"{ticker}.joblib")
    if not model_file.exists():
        return False

    model = joblib.load(model_file)

    future = TODAY + datetime.timedelta(days=days)

    dates = pd.date_range(start="2020-01-01", end=future.strftime("%m/%d/%Y"),)
    df = pd.DataFrame({"ds": dates})

    forecast = model.predict(df)

    # model.plot(forecast).savefig(f"{ticker}_plot.png")
    # model.plot_components(forecast).savefig(f"{ticker}_plot_components.png")

    return forecast.tail(days).to_dict("records")

def convert(prediction_list):
    output = {}
    for data in prediction_list:
        date = data["ds"].strftime("%m/%d/%Y")
        output[date] = data["trend"]
    return output