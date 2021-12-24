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
        self.daily_return = None
        self.daily_factor = None

    def _compute_regression(self):

        # fetch price data from Yahoo Finance
        price = wb.DataReader(self.ticker, 'yahoo', self.start, self.end)['Adj Close']
        daily_return = price.pct_change().iloc[1:]
        daily_return.name = self.ticker

        # fetch Fama-French data
        five_factor = wb.DataReader('F-F_Research_Data_5_Factors_2x3_daily', 'famafrench', self.start, self.end)
        five_factor = five_factor[0] / 100
        momentum = wb.DataReader('F-F_Momentum_Factor_daily', 'famafrench', self.start, self.end)
        momentum = momentum[0] / 100
        momentum.columns = ['MOM']
        daily_factor = pd.concat([five_factor, momentum], axis=1)
        daily_factor.rename(columns={'Mkt-RF': 'MKT'}, inplace=True)

        # assign to attributes
        self.daily_return = daily_return
        self.daily_factor = daily_factor

        # compute regression
        ff_data = daily_factor.merge(daily_return, on='Date')
        ff_model = smf.ols(formula=f"{self.ticker} ~ MKT + SMB + HML + RMW + CMA + MOM", data=ff_data)
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
        significant = param_pvalue[param_pvalue['P-Value'] <= 0.05]

        # compute expected return
        if significant.empty:
            ret_daily = self.daily_factor['MKT'].mean() * result.params['MKT']
        else:
            if 'Intercept' in significant.index:
                alpha = significant.loc['Intercept', 'Param']
                significant = significant.drop('Intercept')
                ret_daily = (self.daily_factor[significant.index].mean() * significant['Param']).sum() + alpha
            else:
                ret_daily = (self.daily_factor[significant.index].mean() * significant['Param']).sum()

        ret_annual = ret_daily * 252
        return ret_annual

    def _compute_hist_volatility(self):
        return self.daily_return.std() * np.sqrt(252)

    def get_risk_return_profile(self):
        ret_annual = self._compute_expected_return()
        vol_annual = self._compute_hist_volatility()
        sharpe = ret_annual / vol_annual

        # log messages
        print(f"\nReturn / Risk Profile of {self.ticker} ({int(self.window/365)}Y)")
        print('=' * (30 + len(self.ticker)))
        print(f"Expected annual return : {(ret_annual * 100):.2f}%")
        print(f"Historical volatility  : {(vol_annual * 100):.2f}%")
        print(f"Risk-adjusted return   : {sharpe:.3f}")

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
