import pandas as pd
import numpy as np
import plotly.express as px

from xquant.backtest.data import Data

data = Data(data={
    'df_price': pd.read_csv('data\\price.csv', parse_dates=['date']),
    'df_mkt_cap': pd.read_csv('data\\market_cap.csv', parse_dates=['date']),
    'df_industry_idx': pd.read_csv('data\\WIND_industry_index.csv', parse_dates=['Date']),
    'df_idx_members': pd.read_csv('data\\WIND_index_members.csv', parse_dates=['included', 'excluded']),
    'df_earnings': pd.read_csv('data\\earnings.csv', parse_dates=['announced', 'reported']),
    'df_dividends': pd.read_csv('data\\dividends.csv', parse_dates=['announced'])
})

