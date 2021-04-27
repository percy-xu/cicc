import datetime
import time
import warnings
from collections import Counter, defaultdict
import pickle

import jqdatasdk
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from forex_python.converter import CurrencyRates
from jqdatasdk import api as jqdata
from plotly import graph_objects as go


class Strategy():

    def __init__(self, df_mcap=None, df_prices=None, df_volume=None, date=None):
        self.df_mcap = df_mcap
        self.df_prices = df_prices
        self.df_volume = df_volume
        self.date = date

    def convert_ticker(self, ticker=None):
        if 'XSHG' in ticker:
            ticker = ticker.replace('.XSHG', '.SH')
        elif 'XSHE' in ticker:
            ticker = ticker.replace('.XSHE', '.SZ')
        elif 'SH' in ticker:
            ticker = ticker.replace('.SH', '.XSHG')
        elif 'SZ' in ticker:
            ticker = ticker.replace('.SZ', '.XSHE')
        return ticker

    def next_trading_day(self):
        date = pd.to_datetime(self.date)
        open_days = self.df_mcap.index
        idx = open_days.get_loc(date, method='backfill')
        return open_days[idx]

    def business_days(self, date):
        date = pd.to_datetime(date)
        return self.df_mcap[str(date.year)+'-'+str(date.month)].index

    def get_earliest_date(self, stock=None):
        date = self.df_mcap[stock].first_valid_index()
        date = pd.to_datetime(date)
        return date

    def get_atvr(self, stock=None):
        date = pd.to_datetime(self.date)
        # make a list of all months in consideration a.k.a. last 12 months
        months = [date-pd.DateOffset(months=n) for n in range(1, 13)]
        # what if the stock has only been traded for less than 12 months?
        earliest = self.get_earliest_date(stock)
        if months[0] < earliest:
            m = int((date-earliest).days/30)
            months = [date-pd.DateOffset(months=n) for n in range(1, m)]

        # for each month, get trading values for each day
        mtvr = []
        for month in months:
            # get a list of all trading days in this month
            trading_days = self.business_days(month)
            # compute daily trading values for this month
            dtv = self.df_volume[stock].loc[trading_days[0]:trading_days[-1]].replace(0, np.nan).dropna()*1000
            # if there is missing data then skip this stock
            if len(dtv) == 0:
                return np.nan
            # get the median
            med = np.median(dtv)
            # get monthly traded value for this month
            mtv = med * len(dtv)
            # get the market cap at the end of this month
            last_day = dtv.index[-1]
            mkt_cap = df_mcap.at[last_day, stock]*10000
            # compute the monthly traded value ratio for each month
            mtvr.append(mtv/mkt_cap)
        # finally, compute the average traded value ratio
        atvr = np.mean(mtvr)*12
        return atvr

    def categorize_industries(self, stocks=[]):
        date = pd.to_datetime(self.date)
        stocks = [self.convert_ticker(stock) for stock in stocks]
        industries = jqdata.get_industry(stocks, date)
        d = defaultdict(list)
        # get industry of a stock and add to defultdict
        for stock in stocks:
            try:
                industry_name = industries[stock]['sw_l1']['industry_name']
                d[industry_name].append(self.convert_ticker(stock))
            except KeyError:
                continue
        return d

    def filter_eligibility(self):
        date = pd.to_datetime(self.date)
        # 1st Step: Exclude NaN values
        na_eligible = [
            stock for stock in self.df_mcap.columns if not np.isnan(self.df_mcap.at[date, stock])]
        print(
            f'\n[Screening...] Excluded {len(self.df_mcap.columns)-len(na_eligible)} companies with missing values.')

        # 2nd Step: Exclude companies with market cap not in $200M-1500M
        cap_eligible = []
        c = CurrencyRates()
        try:
            rate = c.get_rate('USD', 'CNY', date)
        except ConnectionError:
            print(f'[Connecting...] Fetching exchange rate on {date.date()}.')
            time.sleep(10)
        min = rate*200000000
        max = rate*1500000000

        for stock in na_eligible:
            if min <= self.df_mcap.at[date, stock]*10000 <= max:
                cap_eligible.append(self.convert_ticker(stock))
        print(
            f'[Screening...] Excluded {len(na_eligible)-len(cap_eligible)} companies with market cap smaller than $200M or larger than $1500M.')

        # 3rd Step: Exclude companies labeled ST or ST*
        st_status = jqdata.get_extras(
            'is_st', cap_eligible, start_date=date, end_date=date)
        st_eligible = [
            self.convert_ticker(stock) for stock in st_status.columns if not st_status.at[date, stock]]
        print(
            f'[Screening...] Excluded {len(cap_eligible)-len(st_eligible)} companies labeled ST or ST* by regulators.')

        # 4th Step: Exclude companies with less than 6 months of trading history
        length_eligible = []
        for stock in st_eligible:
            start_date = self.get_earliest_date(stock)
            if date - start_date > datetime.timedelta(days=180):
                length_eligible.append(stock)
        print(
            f'[Screening...] Excluded {len(st_eligible)-len(length_eligible)} companies with less than 6 months of trading history.')

        # 5th Step: Exclude companies that fail liquidity screening
        liquidity_eligible = []
        dict_atvr = {}
        for stock in st_eligible:
            atvr = self.get_atvr(stock)
            dict_atvr[stock] = atvr
        atvr_values = list(dict_atvr.values())
        # drop NaN values
        atvr_values = [v for v in atvr_values if not np.isnan(v)]
        threshold = np.percentile(atvr_values, 20)
        # criteria 1: average traded value ratio >= 5%
        # criteria 2: belong to the top 80% of the ATVR values in universe
        for k, v in dict_atvr.items():
            if v >= 0.05 and v >= threshold:
                liquidity_eligible.append(k)
        print(
            f'[Screening...] Excluded {len(length_eligible)-len(liquidity_eligible)} companies with inadequate liquidity.')

        # 6th Step: Adjust target market representation
        representation_eligible = []
        industry_dict = self.categorize_industries(liquidity_eligible)
        full_industry_dict = self.categorize_industries(na_eligible)
        for industry in industry_dict.keys():
            # rank stocks within industry by descending ATVR
            industry_stocks = [
                stock for stock in industry_dict[industry] if not np.isnan(dict_atvr[stock])]
            industry_stocks = sorted(
                industry_stocks, key=lambda x: dict_atvr[x], reverse=True)
            # full market cap
            industry_mkt_cap = sum([df_mcap.at[self.date, stock] * 10000
                                    for stock in full_industry_dict[industry]])
            # the cut-off market representation is 40%
            industry_threshold = industry_mkt_cap * 0.4
            # select stocks until market_cap reaches threshold
            industry_eligible = []
            # if there is only one stock within the industry, this stock is included
            if len(industry_dict[industry]) == 1:
                industry_eligible.append(industry_dict[industry][0])
            else:
                current_cap = 0
                idx = 0
                # print(f'{industry} threshold: ', industry_threshold)
                while current_cap <= industry_threshold and idx < len(industry_stocks):
                    current_cap += self.df_mcap.at[date,
                                                   industry_stocks[idx]] * 10000
                    try:
                        industry_eligible.append(industry_stocks[idx])
                        idx += 1
                    except IndexError:
                        print(idx, len(industry_stocks))

                # print(industry, idx, len(industry_stocks))

            representation_eligible += industry_eligible
        print(
            f'[Screening...] Excluded {len(liquidity_eligible)-len(representation_eligible)} companies for representativeness.')

        return representation_eligible


class Portfolio():

    def __init__(self, stocks=None, cash=0, df_prices=None):
        self.stocks = stocks
        self.cash = cash
        self.df_prices = df_prices

    def get_stock_liquidation(self, date=None):
        agg_stock_value = 0
        sell = []

        for stock, shares in self.stocks.items():
            price = self.df_prices.at[date, stock]
            stock_value = price * shares
            # was this stock suspended for trading?
            if np.isnan(self.df_prices.at[date, stock]):
                # when was this stock last traded?
                last_traded = self.df_prices[stock].last_valid_index()
                self.cash += self.df_prices.at[last_traded, stock]
                sell.append(stock)
            else:
                agg_stock_value += stock_value

        for stock in sell:
            del self.stocks[stock]

        return agg_stock_value

    def get_net_liquidation(self, date=None):
        net_liquidation = self.get_stock_liquidation(date) + self.cash
        return net_liquidation

    def print_portfolio(self):
        for stock, shares in self.stocks.items():
            print(stock, shares)


class BackTest():

    def __init__(self, start_date='2010-01-01', end_date='2020-12-31', init_funds=10000000, commission=0, log=[], data=None):
        self.start_date = start_date
        self.end_date = end_date
        self.init_funds = init_funds
        self.commission = commission
        self.log = log
        self.data = data

    def next_trading_day(self, date=None):
        date = pd.to_datetime(date)
        open_days = self.data[0].index
        idx = open_days.get_loc(date, method='backfill')
        return open_days[idx]

    def get_portfolio(self, funds_available=None, cash_ratio=0, date=None, weight='equal'):
        strategy = Strategy(self.data[0], self.data[1], self.data[2], date)
        composition = strategy.filter_eligibility()
        df_mcap, df_prices = self.data[0], self.data[1]
        funds_investable = funds_available*(1-cash_ratio)
        cash = funds_available*cash_ratio
        portfolio_stocks = {}

        # stocks in portfolio are weighted based on market cap
        if weight == 'cap':
            agg_market_cap = sum([df_mcap.at[date, stock]
                                  for stock in composition])

            for stock in composition:
                try:
                    # the fund allocated to a single stock
                    ratio = df_mcap.at[date, stock] / agg_market_cap
                    amount = funds_investable * ratio
                    # calculate how many shares of stock can be bought
                    price = df_prices.at[date, stock]
                    shares = int(amount/price)

                    portfolio_stocks[stock] = shares
                    cash += (amount - price*shares)
                except ValueError:
                    continue

        # stocks in portfolio are equally weighted
        elif weight == 'equal':
            n = len(composition)
            # amount available for a single stock in portfolio
            amount = funds_investable / n
            # calculate how many shares of stock can be bought
            for stock in composition:
                price = df_prices.at[date, stock]
                shares = int(amount / price)
                portfolio_stocks[stock] = shares
                cash += (amount - price*shares)

        portfolio = Portfolio(stocks=portfolio_stocks,
                              cash=cash, df_prices=df_prices)
        return portfolio

    def calculate_pl(self, date=None):
        date = pd.to_datetime(date)
        i = 0
        flag = 0
        # at the current date, which portfolio am I holding?
        for i in range(len(self.log)):
            try:
                if self.log[i][0] <= date < self.log[i+1][0]:
                    flag = i
                else:
                    i += 1
            except IndexError:
                flag = len(self.log) - 1

        current_portfolio = self.log[flag][1]
        # how much is my holding portfolio's worth?
        net_liquidation = current_portfolio.get_net_liquidation(date)
        # calculate profits & losses
        pl = (net_liquidation/self.init_funds) * 100

        return pl

    def run_backtest(self, freq=6):
        start_date = pd.to_datetime(self.start_date)
        end_date = pd.to_datetime(self.end_date)
        now = self.next_trading_day(start_date)

        # intitial portfolio
        p = self.get_portfolio(
            funds_available=self.init_funds, date=now, weight='cap')
        self.log.append((now, p))

        while now <= end_date-pd.DateOffset(months=6):
            # next date for reblancing portfolio
            now += relativedelta(months=freq)
            now = self.next_trading_day(now)
            print(f'\n[Rebalancing...] {now.date()}')
            # how much is the portfolio is worth now
            net_liquidation = p.get_net_liquidation(date=now)
            # make a new portfolio
            old_p = p
            p = self.get_portfolio(funds_available=net_liquidation, date=now)
            self.log.append((now, p))

    def get_daily_change(self, stocks=[]):
        day_change = [0]
        for i in range(1, len(stocks)):
            yesterday = stocks[i-1]
            today = stocks[i]
            change = round((today-yesterday)/yesterday * 100, 4)
            day_change.append(change)
        return day_change

    def generate_performance(self):
        df_performance = jqdata.get_price(
            '000300.XSHG', start_date=self.start_date, end_date=self.end_date)
        df_performance = df_performance[['close']].rename(
            columns={'close': 'CSI 300'})
        # convert to percentage
        df_performance = df_performance / df_performance['CSI 300'][0]*100
        # get performance of portfolio
        dates = df_performance.index
        portfolio_performance = [self.calculate_pl(date) for date in dates]
        df_performance['Small Cap'] = portfolio_performance

        # df_performance.to_csv('performance.csv', index_label='date')
        return df_performance

    def plot_performance(self, df_performance=None):
        # create Metrics instance
        metrics = Metrics(self.log, df_performance)

        date_range = df_performance.index
        csi_300 = df_performance['CSI 300']
        small_cap = df_performance['Small Cap']
        excess_return = metrics.get_excess_return(
            small_cap, csi_300, date_range[0], date_range[-1])

        # plot graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=date_range,
                                 y=csi_300, mode='lines', name='CSI 300'))
        fig.add_trace(go.Scatter(x=date_range,
                                 y=small_cap, mode='lines', name='Small Cap'))
        fig.add_trace(go.Scatter(x=date_range, y=excess_return *
                                 100, line={'dash': 'dot'}, name='Excess Return'))
        fig.show()

    def show_metrics(self, df_performance):
        metrics = Metrics(self.log, df_performance)
        start_date = df_performance.index[0]
        end_date = df_performance.index[-1]
        csi_300 = df_performance['CSI 300']
        small_cap = df_performance['Small Cap']

        cum_r = metrics.get_cumulative_return(small_cap, start_date, end_date)
        ann_r = metrics.get_annualized_return(small_cap, start_date, end_date)
        ann_ex_r = metrics.get_annualized_excess_return(
            small_cap, csi_300, start_date, end_date)
        max_dd = metrics.get_max_drawdown(small_cap, start_date, end_date)
        vo = metrics.get_strategy_volatility(small_cap, start_date, end_date)
        sharpe = metrics.get_sharpe_ratio(small_cap, start_date, end_date)
        ir = metrics.get_information_ratio(
            small_cap, csi_300, start_date, end_date)
        beta = metrics.get_beta(small_cap, csi_300, start_date, end_date)
        alpha = metrics.get_alpha(small_cap, csi_300, start_date, end_date)
        win_r = metrics.get_win_rate(start_date, end_date)
        win_r_d = metrics.get_daily_win_rate(
            small_cap, csi_300, start_date, end_date)
        pl = metrics.get_pl_ratio(start_date, end_date)
        to_r = metrics.get_turnover_ratio(start_date, end_date, self.data[1])
        trk_err = metrics.get_tracking_error(
            small_cap, csi_300, start_date, end_date)

        print('\n============================================')
        print('| Key Metrics ')
        print('============================================')
        print(f'| Start Date:        {start_date.date()}')
        print(f'| End Date:          {end_date.date()}')
        print('============================================')
        print(f'| Cumulative Return: {round(cum_r*100, 2)}%')
        print(f'| Annualized Return: {round(ann_r*100, 2)}%')
        print(f'| Annualized Excess: {round(ann_ex_r*100, 2)}%')
        print(f'| Maximum Drawdown:  {round(max_dd*100, 2)}%')
        print('============================================')
        print(f'| Information Ratio: {round(ir, 3)}')
        print(f'| Sharpe Ratio:      {round(sharpe, 3)}')
        print(f'| Volatility:        {round(vo, 3)}')
        print('============================================')
        print(f'| Alpha:             {round(alpha, 3)}')
        print(f'| Beta:              {round(beta, 3)}')
        print('============================================')
        print(f'| Win Rate:          {round(win_r*100, 2)}%')
        print(f'| Daily Win Rate:    {round(win_r_d*100, 2)}%')
        print(f'| Profit-Loss Ratio: {round(pl, 1)} : 1')
        print('============================================')
        print(f'| Turnover Ratio:    {round(to_r*100, 2)}%')
        print(f'| Tracking Error:    {round(trk_err*100, 2)}%')
        print('============================================')


class Metrics():

    def __init__(self, log=None, df_performance=None):
        self.log = log
        self.df_performance = df_performance

    def get_daily_return(self, stocks=[]):
        day_change = [0]
        for i in range(1, len(stocks)):
            yesterday = stocks[i-1]
            today = stocks[i]
            change = round((today-yesterday)/yesterday, 4)
            day_change.append(change)

        day_change = pd.Series(data=day_change, index=stocks.index)
        return day_change

    def get_cumulative_return(self, time_series, start_date, end_date):
        time_series = time_series.loc[start_date:end_date]
        start_date, end_date = time_series.index[0], time_series.index[-1]
        cost = time_series[start_date]
        revenue = time_series[end_date]
        cum_rtn = (revenue-cost) / cost

        cum_rtn = round(cum_rtn, 4)
        return cum_rtn

    def get_annualized_return(self, time_series, start_date, end_date, period='d'):
        time_series = time_series.loc[start_date:end_date]
        start_date, end_date = time_series.index[0], time_series.index[-1]
        # first get cumulative return
        cum_rtn = self.get_cumulative_return(time_series, start_date, end_date)
        # how many times should return be compounded in this period?
        if period == 'd':
            days = len(time_series.index)
            exp = 250/days
        elif period == 'w':
            weeks = (end_date.to_period('W') - start_date.to_period('W')).n
            exp = 52/weeks
        elif period == 'm':
            months = (end_date.to_period('M') - start_date.to_period('M')).n
            exp = 12/months
        # calculate annualized return
        ann_rtn = pow((1+cum_rtn), exp) - 1

        ann_rtn = round(ann_rtn, 4)
        return ann_rtn

    def get_annualized_excess_return(self, strategy, benchmark, start_date, end_date):
        strategy = strategy.loc[start_date:end_date]
        benchmark = benchmark.loc[start_date:end_date]
        start_date, end_date = strategy.index[0], strategy.index[-1]

        market_return = self.get_annualized_return(
            benchmark, start_date, end_date)
        strategy_return = self.get_annualized_return(
            strategy, start_date, end_date)

        ann_ex_rtn = strategy_return - market_return

        return ann_ex_rtn

    def get_max_drawdown(self, time_series, start_date, end_date):
        time_series = time_series.loc[start_date:end_date]
        start_date, end_date = time_series.index[0], time_series.index[-1]
        max_drawdown = 0
        # for each day, get the lowest price in the period after
        for day in time_series.index:
            day_price = time_series[day]
            lowest = time_series.loc[day:].min()
            drawdown = (day_price-lowest) / day_price
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        max_drawdown = round(max_drawdown, 4)
        return max_drawdown

    def get_strategy_volatility(self, time_series, start_date, end_date):
        time_series = time_series.loc[start_date:end_date]
        start_date, end_date = time_series.index[0], time_series.index[-1]
        time_series_chg = pd.Series(data=self.get_daily_return(
            time_series), index=time_series.index)

        strat_vo = np.std(time_series_chg) * np.sqrt(250)
        return strat_vo

    def get_sharpe_ratio(self, time_series, start_date, end_date, risk_free=0.04):
        time_series = time_series.loc[start_date:end_date]
        start_date, end_date = time_series.index[0], time_series.index[-1]

        ann_rtn = self.get_annualized_return(time_series, start_date, end_date)
        excess_rtn = ann_rtn - risk_free
        vo = self.get_strategy_volatility(time_series, start_date, end_date)

        sharpe_ratio = excess_rtn / vo
        return sharpe_ratio

    def get_information_ratio(self, strategy, benchmark, start_date, end_date):
        excess_return = self.get_annualized_excess_return(
            strategy, benchmark, start_date, end_date)

        daily_excess_return = self.get_daily_return(
            strategy) - self.get_daily_return(benchmark)
        daily_stdev = np.std(daily_excess_return) * np.sqrt(250)

        ir = excess_return / daily_stdev
        return ir

    def get_beta(self, strategy, benchmark, start_date, end_date):
        strategy = strategy.loc[start_date:end_date]
        benchmark = benchmark.loc[start_date:end_date]
        start_date, end_date = strategy.index[0], strategy.index[-1]

        r_strategy = self.get_daily_return(strategy)
        r_benchmark = self.get_daily_return(benchmark)

        var = np.var(r_benchmark, ddof=1)
        cov = np.cov(r_strategy, r_benchmark)[0][1]

        beta = cov/var
        return beta

    def get_alpha(self, strategy, benchmark, start_date, end_date, risk_free=0.04):
        strategy = strategy.loc[start_date:end_date]
        benchmark = benchmark.loc[start_date:end_date]
        start_date, end_date = strategy.index[0], strategy.index[-1]

        market_return = self.get_annualized_return(
            benchmark, start_date, end_date)
        beta = self.get_beta(strategy, benchmark, start_date, end_date)

        capm = risk_free + beta*(market_return-risk_free)
        annualized_return = self.get_annualized_return(
            strategy, start_date, end_date)

        alpha = annualized_return - capm
        return alpha

    def get_win_rate(self, start_date, end_date):
        start_date, end_date = pd.to_datetime(
            start_date), pd.to_datetime(end_date)
        # trim log to fit within the time period
        log = [transaction for transaction in self.log if start_date <=
               transaction[0] <= end_date]
        # how many transactions has taken place?
        transactions = len(log) - 1
        # the initial value is the portfolio's net liquidation at day zero
        current_val = log[0][1].get_net_liquidation(log[0][0])
        # iterate over log and determine portfolio value at each transaction
        gain = 0
        for i in range(1, len(log)):
            current_date = log[i][0]
            portfolio_val = log[i][1].get_net_liquidation(current_date)
            if portfolio_val >= current_val:
                gain += 1
            current_val = portfolio_val
        # calculate win rate
        win_rate = gain / transactions
        return win_rate

    def get_daily_win_rate(self, strategy, benchmark, start_date, end_date):
        strategy = strategy.loc[start_date:end_date]
        benchmark = benchmark.loc[start_date:end_date]
        start_date, end_date = strategy.index[0], strategy.index[-1]

        r_strategy = self.get_daily_return(strategy)
        r_benchmark = self.get_daily_return(benchmark)

        daily_diff = r_strategy - r_benchmark
        win = 0
        for day in daily_diff:
            if day > 0:
                win += 1

        daily_win_rate = win / len(daily_diff)
        return daily_win_rate

    def get_pl_ratio(self, start_date, end_date):
        start_date, end_date = pd.to_datetime(
            start_date), pd.to_datetime(end_date)
        # trim log to fit within the time period
        log = [transaction for transaction in self.log if start_date <=
               transaction[0] <= end_date]
        # the initial value is the portfolio's net liquidation at day zero
        current_val = log[0][1].get_net_liquidation(log[0][0])
        # iterate over log and determine portfolio value at each transaction
        profit, loss = [], []
        for i in range(1, len(log)):
            current_date = log[i][0]
            portfolio_val = log[i][1].get_net_liquidation(current_date)
            if portfolio_val >= current_val:
                profit.append(portfolio_val-current_val)
            else:
                loss.append(current_val-portfolio_val)
        # calculate average profits and losses
        avg_profit = np.mean(profit)
        avg_loss = np.mean(loss)
        # calculate P/L ratio
        pl_ratio = avg_profit / avg_loss
        return pl_ratio

    def get_excess_return(self, strategy, benchmark, start_date, end_date):
        strategy = strategy.loc[start_date:end_date]
        benchmark = benchmark.loc[start_date:end_date]
        start_date, end_date = strategy.index[0], strategy.index[-1]

        r_strategy = self.get_daily_return(strategy)
        r_benchmark = self.get_daily_return(benchmark)

        excess_return = (r_strategy - r_benchmark).cumsum()
        return excess_return

    def get_transaction_history(self):
        days = [transaction[0] for transaction in self.log]
        # first add in the initial portfolio
        history = [{days[0]:{'buy': {}, 'sell': {}}}]
        # loop over the second to last portfolios
        for i in range(1, len(self.log)):
            curr_portfolio = self.log[i][1].stocks
            prev_portfolio = self.log[i-1][1].stocks
            buy = Counter(curr_portfolio) - Counter(prev_portfolio)
            sell = Counter(prev_portfolio) - Counter(curr_portfolio)
            buy, sell = dict(buy), dict(sell)

            key = self.log[i][0]
            value = {'buy': buy, 'sell': sell}

            history.append({key: value})

        return history

    def get_turnover_ratio(self, start_date, end_date, df_prices):
        start_date, end_date = pd.to_datetime(
            start_date), pd.to_datetime(end_date)
        # trim log to fit within the time period
        log = [transaction for transaction in self.log if start_date <=
               transaction[0] <= end_date]

        begin_liquidation = log[0][1].get_net_liquidation(log[0][0])
        end_liquidation = log[-1][1].get_net_liquidation(log[-1][0])
        avg_liquidation = (end_liquidation + begin_liquidation) / 2
        n_years = log[-1][0].year - log[0][0].year

        history = self.get_transaction_history()
        agg_turnover = 0
        for i in range(1, len(history)):
            date = log[i][0]
            curr_transaction = history[i][date]
            buy_portfolio = Portfolio(
                stocks=curr_transaction['buy'], df_prices=df_prices)
            sell_portfolio = Portfolio(
                stocks=curr_transaction['sell'], df_prices=df_prices)

            buy_value = buy_portfolio.get_net_liquidation(date)
            sell_value = sell_portfolio.get_net_liquidation(date)
            turnover = (buy_value + sell_value) / 2
            agg_turnover += turnover

        avg_annual_turnover = agg_turnover / n_years
        avg_turnover_ratio = avg_annual_turnover / avg_liquidation

        return avg_turnover_ratio

    def get_tracking_error(self, strategy, benchmark, start_date, end_date):
        ann_ex_r = self.get_annualized_excess_return(
            strategy, benchmark, start_date, end_date)
        ir = self.get_information_ratio(
            strategy, benchmark, start_date, end_date)

        tracking_error = ann_ex_r / ir
        return tracking_error


if __name__ == '__main__':

    # load in datasets
    print('[Initilizing...] Loading data.')
    df_mcap = pd.read_csv('market_cap.csv', parse_dates=[
        'date']).set_index('date')
    df_prices = pd.read_csv('price.csv', parse_dates=[
                            'date']).set_index('date')
    df_volume = pd.read_csv('volume.csv', parse_dates=[
                            'date']).set_index('date')
    print('[Initilizing...] Data successfully loaded.\n')

    bypass = True
    save_model = False
    if not bypass:
        t_begin = time.time()

        warnings.filterwarnings('ignore')
        # log into account
        jqdatasdk.auth('18070536824', '536824')
        queries = jqdata.get_query_count(field='spare')
        print(f'[Logging in...] {queries} queries left today.')

        # run backtest
        bt = BackTest(start_date='2010-01-01', end_date='2020-12-31',
                      data=(df_mcap, df_prices, df_volume))
        bt.run_backtest()
        performance = bt.generate_performance()

        t_end = time.time()
        print(f'\n[Completed] Backtest completed in {round((t_end - t_begin), 3)} seconds.')

        if save_model == True:
            with open('model.dat', "wb") as f:
                pickle.dump((bt.log, performance), f)
            print('[Saving...] Model saved to folder.')

    else:
        with open('model.dat', 'rb') as f:
            model = pickle.load(f)
            f.close()
        log = model[0]
        performance = model[1]

        bt = BackTest(start_date='2010-01-01', end_date='2020-12-31', log=log,
                      data=(df_mcap, df_prices, df_volume))

    bt.plot_performance(performance)
    bt.show_metrics(performance)
