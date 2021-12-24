import numpy as np
import pandas as pd
import datetime as dt
import pandas_datareader as wb


class Technical:
    def __init__(self, ticker):
        self.ticker = ticker
        self.end = dt.datetime.today()
        self.start = self.end - dt.timedelta(days=730)
        self.price = None

    def status(self):

        # fetch price data from Yahoo Finance
        price = wb.DataReader(self.ticker, 'yahoo', self.start, self.end)
        last_close = price['Close'].iloc[-1]
        last_50_ma = self._compute_last_moving_average(price['Close'], 50)
        last_150_ma = self._compute_last_moving_average(price['Close'], 150)
        last_200_ma = self._compute_last_moving_average(price['Close'], 200)

        print(f"\nTechnical Analysis of {self.ticker}")
        print('=' * (22 + len(self.ticker)))
        print(f"Last close  : {last_close:.2f}")
        print(f"Last 50-MA  : {last_50_ma:.2f} ({(last_close / last_50_ma - 1) * 100:.2f}%)")
        print(f"Last 150-MA : {last_150_ma:.2f} ({(last_close / last_150_ma - 1) * 100:.2f}%)")
        print(f"Last 200-MA : {last_200_ma:.2f} ({(last_close / last_200_ma - 1) * 100:.2f}%)")

    @staticmethod
    def _compute_last_moving_average(close_price: pd.Series, window: int) -> float:
        return close_price.rolling(window=window).mean().iloc[-1]

