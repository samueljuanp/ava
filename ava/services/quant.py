import numpy as np
import pandas as pd
import datetime as dt
import pandas_datareader as wb
import getFamaFrenchFactors as gff
import statsmodels.formula.api as smf


class Quantitative:
    def __init__(self, ticker, window):
        self.ticker = ticker
        self.end = dt.datetime.today()
        self.start = self.end - dt.timedelta(days=window)
        self.price = None
        self.factor = None

    def _compute_regression(self):

        # fetch price data from Yahoo Finance
        price = wb.DataReader(self.ticker, 'yahoo', self.start, self.end)['Adj Close']
        price.name = self.ticker
        monthly_return = price.resample('M').last().pct_change().dropna()

        # fetch factor data from getFamaFrenchFactors
        factor = gff.carhart4Factor(frequency='m')
        factor.rename(columns={'date_ff_factors': 'Date'}, inplace=True)
        factor.rename(columns={'Mkt-RF': 'MKT'}, inplace=True)
        factor.set_index('Date', inplace=True)

        # assign to attributes
        self.price = price
        self.factor = factor

        # compute regression
        ff_data = factor.merge(monthly_return, on='Date')
        ff_model = smf.ols(formula=f"{self.ticker} ~ MKT + SMB + HML + MOM", data=ff_data)
        result = ff_model.fit()

        return result

    def get_alpha(self):
        result = self._compute_regression()
        alpha = result.params['Intercept']
        print(f"Alpha of {self.ticker}: {alpha:.3f}")

    def get_beta(self):
        result = self._compute_regression()
        beta = result.params['MKT']
        print(f"Beta of {self.ticker}: {beta:.3f}")

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
        if 'Intercept' in significant.index:
            alpha = significant.loc['Intercept', 'Param']
            significant = significant.drop('Intercept')
            exp_month = (self.factor[significant.index].mean() * significant['Param']).sum() + alpha
            exp_annual = exp_month * 12
        else:
            exp_month = (self.factor[significant.index].mean() * significant['Param']).sum()
            exp_annual = exp_month * 12

        return exp_annual

    def _compute_hist_volatility(self):
        return self.price.pct_change().std(skipna=True) * np.sqrt(252)

    def get_risk_return_profile(self):
        exp_annual = self._compute_expected_return()
        vol = self._compute_hist_volatility()
        sharpe = exp_annual / vol

        # log messages
        print(f"\nRisk & Return Profile of {self.ticker}")
        print('=' * (25 + len(self.ticker)))
        print(f"Expected annual return: {(exp_annual * 100):.2f}%")
        print(f"Historical volatility: {(vol * 100):.2f}%")
        print(f"Risk-adjusted return: {sharpe:.3f}")




