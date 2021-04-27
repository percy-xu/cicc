# Small Cap Index

## What?

This project is an attempt to implement the [MSCI Small Cap Index](https://www.msci.com/eqb/gimi/smallcap/MSCI_May07_SCMethod.pdf) methodology in the China A-shares universe. My small cap index tests if excess returns among small-sized firms (i.e. the *SMB* effect in the [Fama-French 3-Factor Model](https://onlinelibrary.wiley.com/doi/full/10.1111/j.1540-6261.1992.tb04398.x)) exists in the Chinese stock market.

## Why?

This is my first project at CICC, so mainly to get myself started as a quant researcher.

## How?

### Dependencies

The entire project is written in python with commonly used packages like pandas and numpy. An external API [`JQData`](https://www.joinquant.com/help/api/help#name:JQData) has also been included for accessing Shen Wan (申万) industry catogory data (in lieu of GICS used by MSCI) 

Finally, [`forex-python`](https://github.com/MicroPyramid/forex-python) is used for exchange rate data and [`plotly`](https://plotly.com/python/) is used for visualization.

### Stock-Selection

The stock-selection process includes the following steps:

1. Clean missing values
2. Exclude firms with market capitalization not in the $200M-1500M range
3. Exclude firms marked ST or ST* by the regulator
4. Exclude firms with less than 6 months of trading history
5. Exclude firms with inadequate liquidity calculated by the average traded value ratio, defined by MSCI

The remaining firms are eligible to be included in my small-cap index.

### Portfolio Management

- This is an index, and therefore no cash is reserved.
- Funds can be distributed either by cap-weight or equal-weight among the eligible stocks.
- Portfolio is rebalanced every 6 months. We assume rebalancing has negligible market impacts.

### Back-testing

- The backtest period starts from 2010-01-01 and ends at 2020-12-31.
- The universe is defined as all stocks listed on the Shanghai Stock Exchange and Shenzhen Exchange.
- The benchmark is defined as the CSI 300 Index.

## Result

Significant size effect exists in the China A-Shares market. Equal-weight distribution generates more excess return, which is expected because it enlarges the size effect by assigning more weight to small firms. This strategy also suffers from large maximum drawdowns due to high volatility, and consequently suppressed Sharpe Ratio and Information Ratio.