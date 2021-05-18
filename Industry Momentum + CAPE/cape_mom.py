import pandas as pd
import numpy as np
from scipy.stats.mstats import winsorize
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

from xquant.backtest.data import Data
from xquant.backtest.backtest import run_backtest
from xquant.strategy import Strategy
from xquant.portfolio import Portfolio
from xquant.util import closest_trading_day


data = Data(data={
    'industry_index': pd.read_csv('Industry Momentum + CAPE\\data\\WIND_industry_index.csv', index_col=['Date'], parse_dates=['Date']),
    'total_returns': pd.read_csv('Industry Momentum + CAPE\\data\\quarterly_total_returns.csv', index_col=['Date'], parse_dates=['Date']),
    'earnings': pd.read_csv('Industry Momentum + CAPE\\data\\quarterly_earnings.csv', index_col=['Date'], parse_dates=['Date']),
    'benchmark': pd.read_csv('Industry Momentum + CAPE\\data\\csi_300.csv', index_col=['date'], parse_dates=['date'])
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

    def get_relative_cape_rank(self, industry, date, n_period=40) -> float:
        '''calculates the numeric rank of an industry's relative Shiller-CAPE ratio among peers'''
        rel_capes = [self.get_relative_cape(sector, date, n_period) for sector in SECTORS]
        rel_capes_dict = dict(zip(SECTORS, rel_capes))

        series = pd.Series(rel_capes_dict).fillna(99)
        df = pd.DataFrame(series, columns=['rel_cape'])
        df.sort_values(by=['rel_cape'], inplace=True)
        df['rank'] = np.arange(1,len(df)+1)
        
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
        
        rank = df.at[industry, 'rank']
        return rank

    def stock_selection(self, funds, date) -> Portfolio:
        '''overrides the stock_selection method in the parent class'''
        points = [2] * len(SECTORS)
        points_dict = dict(zip(SECTORS, points))

        for industry in tqdm(SECTORS):
            rel_cape_rank = self.get_relative_cape_rank(industry, date, 10) # NEED TO ADJUST TO 40
            mom_rank = self.get_mom_rank(industry, date)
            # over/underweight sectors based on their ranks
            if rel_cape_rank <= 2 or mom_rank <= 2:
                points_dict[industry] += 1
            elif rel_cape_rank >= len(SECTORS)-2 or mom_rank >= len(SECTORS)-2:
                points_dict[industry] -= 1
        
        total_points = sum(points_dict.values())
        weights = [points_dict[industry]/total_points for industry in SECTORS]
        budgets = [funds*weight for weight in weights] # budget available for each industry
        
        df_prices = data.get_data('industry_index')
        prices = df_prices.loc[closest_trading_day(date, df_prices.index, 'bfill')]
        
        shares = np.divide(budgets, prices)
        shares_dict = dict(zip(SECTORS, shares))

        portfolio = Portfolio(long=shares_dict, short={}, cash=0)
        return portfolio

if __name__ == '__main__':
    cape_mom = CAPE_MOM(strategy_name='CAPE + Momentum')

    holdings = run_backtest(pd.Timestamp('20180101'), pd.Timestamp('20191231'), cape_mom.stock_selection, 100, 3)
    
    
