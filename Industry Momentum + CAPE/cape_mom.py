from datetime import timedelta
import pandas as pd
import numpy as np
import os
import plotly.express as px
from scipy.stats.mstats import winsorize
from dateutil.relativedelta import relativedelta

from xquant.backtest.data import Data
from xquant.strategy import Strategy
from xquant.util import closest_trading_day


data = Data(data={
    'industry_index': pd.read_csv('Industry Momentum + CAPE\\data\\WIND_industry_index.csv', index_col=['Date'], parse_dates=['Date']),
    'total_returns': pd.read_csv('Industry Momentum + CAPE\\data\\quarterly_total_returns.csv', index_col=['Date'], parse_dates=['Date']),
    'earnings': pd.read_csv('Industry Momentum + CAPE\\data\\quarterly_earnings.csv', index_col=['Date'], parse_dates=['Date'])
})

SECTORS = list(data.get_data('industry_index').columns)
PERIODS = data.get_data('total_returns').index

class CAPE_MOM(Strategy):

    def __init__(self, strategy_name) -> None:
        super().__init__(strategy_name)

    def get_cape(self, industry, date) -> float:
        '''calculates the absolute (i.e. raw) Shiller-CAPE ratio of an industry'''
        df_earnings = data.get_data('earnings')
        df_earnings = df_earnings.loc[:date]
        df_tot_rtns = data.get_data('total_returns')
        df_tot_rtns = df_tot_rtns.loc[:date].tail(1)

        # if there is insufficient data, raise error
        if len(df_earnings) < 20:
            raise Exception('Insufficient data, need at least 5 years to calculate CAPE')
        
        df_earnings = df_earnings.tail(20)
        earning = df_earnings.mean()[industry]
        tot_rtn = df_tot_rtns[industry].values[0]

        cape = tot_rtn/earning
        return cape
        
    def get_relative_cape(self, industry, date, n_period=40) -> float:
        '''calculates the relative Shiller-CAPE ratio of an industry'''
        periods = PERIODS[PERIODS<=date][-n_period:]
        if len(periods) < n_period:
            raise Exception('Insufficient data, need at least 10 years to calculate Relative CAPE')

        capes = [self.get_cape(industry, period) for period in periods]
        capes = list(winsorize(capes, limits=[0.05,0.05]))
        relative_cape = capes[-1] / np.mean(capes)

        return relative_cape

    def get_relative_cape_rank(self, industry, date, n_period) -> float:
        '''calculates the numeric rank of an industry's relative Shiller-CAPE ratio among peers'''
        rel_capes = [self.get_relative_cape(sector, date, n_period) for sector in SECTORS]
        rel_capes_dict = dict(zip(SECTORS, rel_capes))

        series = pd.Series(rel_capes_dict).dropna()
        df = pd.DataFrame(series, columns=['rel_cape'])
        df.sort_values(by=['rel_cape'], inplace=True)
        df['rank'] = np.arange(1,len(df)+1)
        
        print(df)
        rank = df.at[industry, 'rank']
        return rank

    def get_momentum(self, industry, date, look_back=6) -> float:
        '''calculates the momentum of an industry'''
        # select and truncate series
        series = data.get_data('industry_index')[industry]
        series = series[series.index <= date]
        # calculate lagged return
        start_date = date - relativedelta(months = 12)
        end_date = date - relativedelta(months = look_back)

        returns = []
        while start_date < end_date:
            local_end = start_date + relativedelta(months=look_back)
            period = series.loc[start_date:local_end]

            start_price = period.head(1)[0]
            end_price = period.tail(1)[0]

            local_return = (end_price/start_price) - 1
            returns.append(local_return)

            start_date += relativedelta(months=1)

        momentum = np.mean(returns)
        return momentum

    def get_mom_rank(self, industry, date) -> float:
        '''calculates the numeric rank of an industry's momentum among peers'''
        mom_list = [self.get_momentum(sector, date) for sector in SECTORS]
        mom_dict = dict(zip(SECTORS, mom_list))

        series = pd.Series(mom_dict).dropna()
        df = pd.DataFrame(series, columns=['momentum'])
        df.sort_values(by=['momentum'], ascending=False, inplace=True)
        df['rank'] = np.arange(1,len(df)+1)
        
        print(df)
        rank = df.at[industry, 'rank']
        return rank

    # TODO
    def stock_selection(self, date) -> dict:
        '''overrides the stock_selection method in the parent class'''
        pass


if __name__ == '__main__':
    cape_mom = CAPE_MOM(strategy_name='CAPE + Momentum')
    cape_mom.get_mom_rank('Energy', pd.Timestamp('20190101'))
    cape_mom.get_relative_cape_rank('Energy', pd.Timestamp('20190101'), 10)