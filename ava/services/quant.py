import numpy as np
import pandas as pd
import datetime as dt
import pandas_datareader as wb
import statsmodels.formula.api as smf


class Quantitative:
    def __init__(self, ticker, window):
        self.ticker = ticker
        self.window = window
        self.end = dt.datetime.today()
        self.start = self.end - dt.timedelta(days=window)
        self.price = None
        self.daily_return = None
        self.daily_factor = None

    def _fetch_price_data(self):

        price = wb.DataReader(self.ticker, 'yahoo', self.start, self.end)['Adj Close']
        daily_return = price.pct_change().iloc[1:]
        daily_return.name = self.ticker

        self.price = price
        self.daily_return = daily_return

    # TODO: AUTOMATE DAILY DATA-PULLING AND STORE INSIDE DATABASE TO AVOID REPETITIVE REQUEST
    def _fetch_factor_data(self):

        # Fama-French 5 factors
        five_factor = wb.DataReader('F-F_Research_Data_5_Factors_2x3_daily', 'famafrench', self.start, self.end)
        five_factor = five_factor[0] / 100

        # short-term reversal
        st_reversal = wb.DataReader('F-F_ST_Reversal_Factor_daily', 'famafrench', self.start, self.end)
        st_reversal = st_reversal[0] / 100

        # momentum factor
        momentum = wb.DataReader('F-F_Momentum_Factor_daily', 'famafrench', self.start, self.end)
        momentum = momentum[0] / 100

        # concatenate dataframes
        daily_factor = pd.concat([five_factor, st_reversal, momentum], axis=1)
        daily_factor.rename(columns={
            'Mkt-RF': 'MKT',
            'Mom   ': 'MOM',
            'ST_Rev': 'STR',
        }, inplace=True)
        daily_factor.drop('RF', axis=1, inplace=True)

        self.daily_factor = daily_factor

    def _compute_regression(self):

        self._fetch_price_data()
        self._fetch_factor_data()

        ff_data = self.daily_factor.merge(self.daily_return, on='Date')
        ff_model = smf.ols(formula=f"{self.ticker} ~ MKT + SMB + HML + RMW + CMA + STR + MOM", data=ff_data)
        result = ff_model.fit()

        return result

    def get_regression_summary(self):
        result = self._compute_regression()
        print()
        print(result.summary())

    def _compute_expected_return(self):
        result = self._compute_regression()
        param_pvalue = pd.concat([result.params, result.pvalues], axis=1)
        param_pvalue.columns = ['Param', 'P-Value']

        # get coefficients with significant p-value
        signif = param_pvalue[param_pvalue['P-Value'] <= 0.05]

        # compute expected return
        if signif.empty:
            print('Significant factor: MKT')
            ret_daily = self.daily_factor['MKT'].mean() * result.params['MKT']
        else:
            print(f"\nSignificant factor(s): {', '.join([s if s != 'Intercept' else 'ALPHA' for s in signif.index])}")
            if 'Intercept' in signif.index:
                alpha = signif.loc['Intercept', 'Param']
                signif = signif.drop('Intercept')
                ret_daily = (self.daily_factor[signif.index].mean() * signif['Param']).sum() + alpha
            else:
                ret_daily = (self.daily_factor[signif.index].mean() * signif['Param']).sum()

        ret_annual = ret_daily * 252
        return ret_annual

    def _compute_hist_return(self):
        return self.daily_return.mean() * 252

    def _compute_hist_volatility(self):
        return self.daily_return.std() * np.sqrt(252)

    def get_risk_return_profile(self):
        expected_return = self._compute_expected_return()
        hist_return = self._compute_hist_return()
        hist_vol = self._compute_hist_volatility()
        conservative_sharpe = min(expected_return, hist_return) / hist_vol

        market_return = self.daily_factor['MKT'].mean() * 252
        market_vol = self.daily_factor['MKT'].std() * np.sqrt(252)
        market_sharpe = market_return / market_vol

        # log messages
        print(f"\nReturn / Risk Profile of {self.ticker} ({int(self.window/365)}Y)")
        print('=' * (30 + len(self.ticker)))
        print(f"Expected return        : {(expected_return * 100):.2f}%")
        print(f"Historical return      : {(hist_return * 100):.2f}%")
        print(f"Historical volatility  : {(hist_vol * 100):.2f}%")
        print(f"Conservative Sharpe    : {conservative_sharpe:.3f}")
        print(f"\nMarket Excess Profile ({int(self.window / 365)}Y)")
        print('=' * (30 + len(self.ticker)))
        print(f"Historical return      : {(market_return * 100):.2f}%")
        print(f"Historical volatility  : {(market_vol * 100):.2f}%")
        print(f"Historical Sharpe      : {market_sharpe:.3f}")

    def get_capm_beta(self):
        """Function to calculate non-equity beta compared to the market"""

        # fetch data
        price = wb.DataReader([self.ticker, 'SPY'], 'yahoo', self.start, self.end)['Adj Close']
        price.rename(columns={'SPY': 'MKT'}, inplace=True)
        daily_return = price.pct_change().iloc[1:]

        # compute regression
        capm = smf.ols(formula=f"{self.ticker} ~ MKT", data=daily_return)
        result = capm.fit()

        print(f"Beta of {self.ticker} ({int(self.window/365)}Y): {result.params['MKT']:.3f}")
