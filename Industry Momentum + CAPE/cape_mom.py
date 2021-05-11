import pandas as pd
import numpy as np
import os
import plotly.express as px

from xquant.backtest.data import Data
from xquant.strategy import Strategy

data = Data(data={
    'df_price': pd.read_csv('Industry Momentum + CAPE\\data\\price.csv', index_col=['date'], parse_dates=['date']),
    'df_mkt_cap': pd.read_csv('Industry Momentum + CAPE\\data\\market_cap.csv', index_col=['date'], parse_dates=['date']),
    'df_industry_idx': pd.read_csv('Industry Momentum + CAPE\\data\\WIND_industry_index.csv', index_col=['Date'], parse_dates=['Date']),
    'df_idx_members': pd.read_csv('Industry Momentum + CAPE\\data\\WIND_index_members.csv', parse_dates=['included', 'excluded']),
    'df_earnings': pd.read_csv('Industry Momentum + CAPE\\data\\earnings.csv', parse_dates=['announced', 'reported']),
    'df_dividends': pd.read_csv('Industry Momentum + CAPE\\data\\dividends.csv', parse_dates=['announced'])
})

sectors = list(data.get_data('df_industry_idx').columns)

class CAPE_MOM(Strategy):

    def __init__(self, strategy_name) -> None:
        super().__init__(strategy_name)

    # TODO
    def get_cape(ticker, date) -> float:
        '''calculates the absolute (i.e. raw) Shiller-CAPE ratio of an industry'''
        pass

    # TODO
    def get_relative_cape(ticker, date) -> float:
        '''calculates the relative Shiller-CAPE ratio of an industry'''
        pass
    
    # TODO
    def get_relative_cape_rank(ticker, date) -> float:
        '''calculates the percentile rank of an industry's relative Shiller-CAPE ratio among peers'''
        pass

    # TODO
    def get_ind_mom(ticker, date, look_back=6) -> float:
        '''calculates the momentum of an industry'''
        pass

    # TODO
    def get_mom_rank(ticker, date) -> float:
        '''calculates the percentile rank of an industry's momentum among peers'''
        pass

    # TODO
    def stock_selection() -> dict:
        '''overrides the stock_selection method in the parent class'''
        pass

# cape_mom = CAPE_MOM(strategy_name='CAPE + Momentum')