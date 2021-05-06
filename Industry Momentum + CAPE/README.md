# Industry Momentum + Shiller-CAPE <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->

- [About](#about)
  - [Purpose](#purpose)
  - [Literature Review](#literature-review)
    - [Industry Momentum](#industry-momentum)
    - [Shiller-CAPE Ratio](#shiller-cape-ratio)
  - [Momentum and Value](#momentum-and-value)
- [Motivation](#motivation)
- [Methodology](#methodology)
  - [Dependencies](#dependencies)
  - [Construction of CAPE and Relative CAPE](#construction-of-cape-and-relative-cape)
    - [CAPE](#cape)
    - [Relative CAPE](#relative-cape)
  - [Strategy](#strategy)
    - [Description](#description)
    - [Weighting Scheme](#weighting-scheme)
    - [Look-back Period](#look-back-period)
  - [Portfolio Management](#portfolio-management)
  - [Back-testing](#back-testing)
- [Result](#result)

## About

### Purpose

This project explores two asset price anomalies in the equities market: **momentum** and **value**. More specifically, I attempt to develop a strategy combining the industry momentum effect and the Shiller-CAPE ratio in the China A-shares stock market.

### Literature Review

Both industry momentum effect and Shiller-CAPE ratio have received significant attention from scholars and investors since the 1990s. This section provides some background and relevant literatures for these two topics.

#### Industry Momentum

Eugene Fama, arguably the most prominent researcher on the Efficient Market Hypothesis once said that the momentum effect is *"perhaps the biggest embarrassment to the EMH"*. Indeed, according to the EMH the momentum should not exist at all because past returns and future returns are completely irrelevant. Yet, momentum has been generating consistent excess returns ever since it was first proposed in [Jegadeesh (1993)](https://www.jstor.org/stable/2328882) over the last three decades.

The question that follows is naturally: *"What causes momentum?"* [Moskowitz (1999)](https://www.jstor.org/stable/798005) offers an interesting theory: **momentum effects can be explained by industries**. Moskowitz concluded that stocks within the same industry are under the same regulatory constraints and affected by the same external factors, which causes their stock prices to move in the same direction. Further, the momentum effect largely disappears once industry is being controlled.

So the next question is: *If industries do explain momentum, then why bother with individual stocks?* Moskowitz answers this question as well. He made a portfolio consisted of industry indices only and rotated among the recent winning industries, and found that the excess return exceeds that of a portfolio of recent winning individual stocks.

#### Shiller-CAPE Ratio

If such thing as an economics prophet exists, Robert Shiller will surely be one of them. Shiller famously predicted bursts of the dot com bubble and the real estate bubble in the early and mid 2000s, and one his crystal balls was the CAPE Ratio Shiller developed with John Campbell.

**C**yclically **A**djusted **P**rice-**E**arnings ratio is centered around the simple idea of *"averaging out fluctuations"*. Shiller argues that measurements of company performance such as the PE ratio or dividend yield can be overly influenced by short term fluctuations. For example, the PE ratio for a company in 2021 Q1 alone can be affected by a temporary price shock and therefore do not have significant predictive power for future returns. When forecasting long-term future returns, one should really look at long-term past returns. **CAPE is calculated by taking the average of inflation-adjusted earnings and prices over the past 10 years, or in short, the smoothed earnings.** [Campbell and Shiller (1998)](https://jpm.pm-research.com/content/24/2/11) examined the smoothed earnings of the US stock market at the turn of the century and concluded it was dangerously overvalued. Sure enough, the dot com bubble bursted in less than 5 years.

More recently, [Bunn and Shiller (2014)](https://www.nber.org/papers/w20370) examined the CAPE ratio in a larger historical scope. Going back to as far as the beginning of the 1870s, Bunn and Shiller computed the CAPE ratios for the Industrials sector, the Utilities sector, and the Railroads sector. They then designed a sector rotation strategy that overweighted the undervalued (cheap) sector and underweighted the overvalued (expensive) sector. This strategy provided 1.09% annualized, inflation-adjusted excess total return over 110 years.

### Momentum and Value

Combining momentum and value is nothing new. [Asness (1997)](https://www.jstor.org/stable/4479982) first illustrated the negative correlation between momentum and value. By using data from 1963 to 1994 in the US stock market, Asness found that value outperforms among weak momentum stocks and underperforms among strong momentum stocks. Conversely, momentum outperforms among expensive stocks and underperforms among cheap stocks. It ensues then, a strategy that profits from both of the two pricing anomalies enjoys significantly reduced volatility. [Asness, Frazzini, Israel and Moskowitz (2014)](https://jpm.pm-research.com/content/40/5/75) promoted momentum as a strong complement to be used with value strategies.

## Motivation

Much of the existing literatures on industry momentum and Shiller-CAPE limit their scopes to the US stock market, and little has been done to test these theories in the Chinese stock market. This project aims to fill these gaps.

The Chinese stock market (China A-shares) is perhaps one of the most unique equities market in the world, marked by its imbalanced market participants. Retail investors far outnumber institutional investors, which makes market behavior in the A-shares vastly different from other equities markets. For example, China A-Shares has an abnormally high turnover rate, and many believe *reversal* is a better predictor than *momentum* in China A-shares.

This project hopes to find whether industry momentum exists and the predictive power of the Shiller-CAPE ratio in China A-shares. The performance of an index that incorporates industry momentum and Shiller-CAPE will likely give us the answer.

## Methodology

### Dependencies

This project is entirely written in python. It largely uses the [`xquant`](https://github.com/percy-xu/xquant) library developed by myself. In addition, `pandas`, `numpy`, `scipy` and `plotly` are used for data processing, computation, and visualization.

### Construction of CAPE and Relative CAPE

#### CAPE

As intimidating as it may sound, CAPE is no more than a variation of the traditional P/E-ratio. As mentioned, it is adjusted for business cycles to make long-run predictions. But for now let us step back and look at the traditional P/E-ratio, which in period *t* is defined as:

<!-- $\text{P/E-ratio}_{t}=\frac{P_{t}}{e_{t}}$ -->

![equation](https://latex.codecogs.com/svg.latex?\text{P/E-ratio}_{t}=\frac{P_{t}}{e_{t}})

Both the denominator and the numerator need to be modified for the long-run, but only slightly. We first consider the denominator. To reflect the true cash flow received by the shareholders, Shiller and Bunn constructed a "total return" price series which in period *t* is defined as:

<!-- $P^{TR}_{t}=\frac{P_t+Div_{t-1}}{P_{t-1}}$ -->

![equation](https://latex.codecogs.com/svg.latex?P^{TR}_{t}=\frac{P_t+Div_{t-1}}{P_{t-1}})

By taking dividends into account, differences in company payout policies are effectively eliminated. We now turn to the numerator, which is where the long-term forecasting power originates. At every year *x*, we compute the scaled earning by multiplying the earning with the ratio of total return price and price to reflect the change we made earlier from the price series to the total return price series.

<!-- $e^{scaled}_{x} = e_{x}\cdot\frac{P^{TR}_{x}}{P_{x}}$ -->

![equation](https://latex.codecogs.com/svg.latex?e^{scaled}_{x}=e_{x}\cdot\frac{P^{TR}_{x}}{P_{x}})

Now we have a total return price series and a scaled earnings series. They are then adjusted for inflation using the [Consumer Price Index from the FRED](https://fred.stlouisfed.org/series/CHNCPIALLQINMEI).

By taking the arithmetic mean of these scaled, inflation-adjusted earnings in the last *n* years, we get an "averaged out" earning which in year *t* is defined as:

<!-- $\overline{e}_{t}={\frac{1}{n}}(\sum^{n}_{i=1}e_{t-n+i})=\frac{e_{t-n}+e_{t-n+1}+\cdots+e_{t-1}+e_{t}}{n}$ -->

![equation](https://latex.codecogs.com/svg.latex?\overline{e}_{t}={\frac{1}{n}}(\sum^{n}_{i=1}e_{t-n+i})=\frac{e_{t-n}+e_{t-n+1}+\cdots+e_{t-1}+e_{t}}{n})

When CAPE was first defined, Campbell and Shiller took *n=10* - meaning 10 years of adjusted earnings are averaged. In this project, we shorten this period to 5 years because the China-A Shares is very young and market data is limited. This is a comprise, but it does not contradict the spirit of CAPE. Shiller frequently refers to *Market Analysis*, a textbook written by Graham & Dodd in 1934 that mentions a meaningful valuation should look at earnings *"not less than five years, preferably seven or ten years"*. It can be argued, therefore, five years still (closely) qualifies as a meaningful valuation period albeit being significantly shorter than ten years.

Finally, much like the traditional P/E-ratio, simply divide the inflation-adjusted total return price by the average earnings (inflation-adjusted in each year) to calculate the CAPE ratio in period *t*. The CAPE ratio is computed quarterly.

<!-- $\text{CAPE}_{t}=\frac{P^{TR}_{t}}{\overline{e}_{t}}$ -->

![equation](https://latex.codecogs.com/svg.latex?\text{CAPE}_{t}=\frac{P^{TR}_{t}}{\overline{e}_{t}})

#### Relative CAPE

In an industry-rotation strategy, we would want to compare one industry with other industries. But does it really make sense to compare the CAPE ratios across industries? CAPE ratio is a measure of value, and some industries are just inherently more expensive than others by nature. The technology industry, for example, is almost always more likely to have a higher CAPE ratio than the consumer staples industry. This is why Shiller and Bunn computed a *Relative CAPE Ratio* for every industry. The Relative CAPE ratio of an industry is computed by comparing its current CAPE against historical CAPE ratios, therefore making cross-industry comparisons possible.

The Relative CAPE ratio is calculated by dividing the current CAPE ratio of an industry by the average of its own CAPE ratios in the last 20 years. In this project, we shorten this period to 10 years (or 40 periods, as CAPE is computed quarterly) for the same reason for using 5 years of data when computing the CAPE ratio. Historical CAPE ratios are winsorized at the 5% level, removing outlier periods and reducing turbulence.

For a formulaic expression, the Relative CAPE in period *t* is defined as:

<!-- $\text{Relative CAPE}_{t}=\frac{\text{CAPE}_t}{{\frac{1}{40}\sum^{40}_{i=1}\text{CAPE}_{t-40+i}}}$ -->

![equation](https://latex.codecogs.com/svg.latex?\text{Relative&space;CAPE}_{t}=\frac{\text{CAPE}_t}{{\frac{1}{40}\sum^{40}_{i=1}\text{CAPE}_{t-40&plus;i}}})

### Strategy

#### Description

My index is, in essence, an **"index of indices"** - much like a fund of funds (FOF) in terms of structure. For this project, I am defining the *TBD* as the stock selection universe.

At a cross-section, the *Relative CAPE Ratio* is computed for every industry. Industries are ranked by their Relative CAPE Ratios. The *TBD* industries with the highest Relative CAPE are underweighted and the *TBD* industries with the lowest Relative CAPE are overweighted.

This leaves us with *TBD* remaining industries. By calculating each industry's performance in the past 6 months, we categorize them into winners and losers. Winners (industries with strong momentum) are overweighted and losers (industries with weak momentum) are underweighted.

#### Weighting Scheme

Bunn and Shiller used a point-based weighting scheme which I find easy to understand and implement. A adapted version of this weighting scheme is used in this project. Every time my index is computed, each industry in the cross-section start with 2 points. 1 point is added when an industry is overweighted and 1 point is subtracted when an industry is underweighted. We now have 28 industries with points ranging from 1 to 3. Respective weights are then calculated for each industry based on its point.

#### Look-back Period

When determining an industry is a winner or a loser, we look at its performance over a period of time in the past. In our case, this look-back period 6 months. This might seem like an arbitrary number - and in a sense it is. When Jegadeesh first discovered the momentum effect, he found that momentum strategies with various look-back periods are on average quite profitable and just selected 6 months as the look-back period for the rest of his paper. Moskowitz followed Jegadeesh for simplicity in his paper, and we shall comply with this "tradition".

### Portfolio Management

We are constructing an index, and therefore no cash is reserved in the portfolio. Our portfolio is a self-financed, zero-cost portfolio.

The portfolio is rebalanced quarterly to always incorporate the most recent information.

### Back-testing

COMING SOON

## Result

COMING SOON
