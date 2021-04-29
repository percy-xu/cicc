# Industry Momentum + Shiller-CAPE <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->

<<<<<<< HEAD
- [What?](#what)
  - [Goal](#goal)
  - [Literature Review](#literature-review)
    - [Industry Momentum](#industry-momentum)
    - [Shiller-CAPE Ratio](#shiller-cape-ratio)
- [Why?](#why)
- [How?](#how)
=======
- [About](#about)
  - [Purpose](#purpose)
  - [Literature Review](#literature-review)
    - [Industry Momentum](#industry-momentum)
    - [Shiller-CAPE Ratio](#shiller-cape-ratio)
  - [Momentum and Value](#momentum-and-value)
- [Motivation](#motivation)
- [Methodology](#methodology)
>>>>>>> aececf97351d9cb7e780aac0b2c748980388bd1d
  - [Dependencies](#dependencies)
  - [Strategy](#strategy)
    - [Description](#description)
    - [Weighting Scheme](#weighting-scheme)
    - [Look-back Period](#look-back-period)
  - [Portfolio Management](#portfolio-management)
  - [Back-testing](#back-testing)
- [Result](#result)

<<<<<<< HEAD
## What?

### Goal
=======
## About

### Purpose
>>>>>>> aececf97351d9cb7e780aac0b2c748980388bd1d

This project explores two asset price anomalies in the equities market: **momentum** and **value**. More specifically, I attempt to develop a strategy combining the industry momentum effect and the Shiller-CAPE ratio in the China A-shares stock market.

### Literature Review

Both industry momentum effect and Shiller-CAPE ratio have received significant attention from scholars and investors since the 1990s. This section provides some background and relevant literatures for these two topics.

#### Industry Momentum

<<<<<<< HEAD
Eugene Fama, arguably the most prominent researcher on the Efficient Market Hypothesis once said that the momentum effect is *"perhaps the biggest embarrassment to the EMH"*. Indeed, according to the EMH the momentum should not exist at all because past returns and future returns are completely irrelevant. Yet, momentum has been generating consistent excess returns since it was first proposed in [Jegadeesh (1993)](https://www.jstor.org/stable/2328882) over the last three decades.
=======
Eugene Fama, arguably the most prominent researcher on the Efficient Market Hypothesis once said that the momentum effect is *"perhaps the biggest embarrassment to the EMH"*. Indeed, according to the EMH the momentum should not exist at all because past returns and future returns are completely irrelevant. Yet, momentum has been generating consistent excess returns ever since it was first proposed in [Jegadeesh (1993)](https://www.jstor.org/stable/2328882) over the last three decades.
>>>>>>> aececf97351d9cb7e780aac0b2c748980388bd1d

The question that follows is naturally: *"What causes momentum?"* [Moskowitz (1999)](https://www.jstor.org/stable/798005) offers an interesting theory: **momentum effects can be explained by industries**. Moskowitz concluded that stocks within the same industry are under the same regulatory constraints and affected by the same external factors, which causes their stock prices to move in the same direction. Further, the momentum effect largely disappears once industry is being controlled.

So the next question is: *If industries do explain momentum, then why bother with individual stocks?* Moskowitz answers this question as well. He made a portfolio consisted of industry indices only and rotated among the recent winning industries, and found that the excess return exceeds that of a portfolio of recent winning individual stocks.

#### Shiller-CAPE Ratio

If such thing as an economics prophet exists, Robert Shiller will surely be one of them. Shiller famously predicted bursts of the dot com bubble and the real estate bubble in the early and mid 2000s, and one his crystal balls was the CAPE Ratio Shiller developed with John Campbell.

<<<<<<< HEAD
**C**yclically **A**djusted **P**rice-**E**arnings Ratio is centered around the simple idea of *"averaging out fluctuations"*. Shiller argues that measurements of company performance such as the PE ratio or dividend yield can be overly influenced by short term fluctuations. For example, the PE ratio for a company in 2021 Q1 alone can be affected by a temporary price shock and therefore do not have significant predictive power for future returns. When forecasting long-term future returns, one should really look at long-term past returns. **CAPE is calculated by taking the average of inflation-adjusted earnings and prices over the past 10 years, or in short, the smoothed earnings.** [Campbell and Shiller (1998)](https://jpm.pm-research.com/content/24/2/11) examined the smoothed earnings of the US stock market at the turn of the century and concluded it was dangerously overvalued. Sure enough, the dot com bubble bursted in less than 5 years.

More recently, [Bunn and Shiller (2014)](https://www.nber.org/papers/w20370) examined the CAPE ratio in a larger historical scope. Going back to as far as the beginning of the 1870s, Bunn and Shiller computed the CAPE ratios for the Industrials sector, the Utilities sector and the Railroads sector. They then designed a sector rotation strategy that overweighted the undervalued sector and underweighted the overvalued sector. This strategy provided 1.09% annualized, inflation-adjusted excess total return over 110 years.

## Why?

Much of the existing literatures on industry momentum and Shiller-CAPE limit their scopes to the US stock market, and little has been done to test these theories in the Chinese stock market.

The Chinese stock market (China A-shares) is perhaps one of the most imbalanced equities market in the world in terms of market participants. Retail investors far outnumber institutional investors, which makes market behavior in the A-shares vastly different from other equities markets. In fact, many believe *reversal* is a better predictor than *momentum* in China A-shares.

This project hopes to find whether industry momentum exists in China A-shares and the predictive power of the Shiller-CAPE ratio. The performance of an index that incorporates industry momentum and Shiller-CAPE will likely give us the answer.

## How?
=======
**C**yclically **A**djusted **P**rice-**E**arnings ratio is centered around the simple idea of *"averaging out fluctuations"*. Shiller argues that measurements of company performance such as the PE ratio or dividend yield can be overly influenced by short term fluctuations. For example, the PE ratio for a company in 2021 Q1 alone can be affected by a temporary price shock and therefore do not have significant predictive power for future returns. When forecasting long-term future returns, one should really look at long-term past returns. **CAPE is calculated by taking the average of inflation-adjusted earnings and prices over the past 10 years, or in short, the smoothed earnings.** [Campbell and Shiller (1998)](https://jpm.pm-research.com/content/24/2/11) examined the smoothed earnings of the US stock market at the turn of the century and concluded it was dangerously overvalued. Sure enough, the dot com bubble bursted in less than 5 years.

More recently, [Bunn and Shiller (2014)](https://www.nber.org/papers/w20370) examined the CAPE ratio in a larger historical scope. Going back to as far as the beginning of the 1870s, Bunn and Shiller computed the CAPE ratios for the Industrials sector, the Utilities sector, and the Railroads sector. They then designed a sector rotation strategy that overweighted the undervalued (cheap) sector and underweighted the overvalued (expensive) sector. This strategy provided 1.09% annualized, inflation-adjusted excess total return over 110 years.

### Momentum and Value

Combining momentum and value is nothing new. [Asness (1997)](https://www.jstor.org/stable/4479982) first illustrated the negative correlation between momentum and value. By using data from 1963 to 1994 in the US stock market, Asness found that value outperforms among weak momentum stocks and underperforms among strong momentum stocks. Conversely, momentum outperforms among expensive stocks and underperforms among cheap stocks. It ensues then, a strategy that profits from both of the two pricing anomalies enjoys significantly reduced volatility. [Asness, Frazzini, Israel and Moskowitz (2014)](https://jpm.pm-research.com/content/40/5/75) promoted momentum as a strong complement to be used with value strategies.

## Motivation

Much of the existing literatures on industry momentum and Shiller-CAPE limit their scopes to the US stock market, and little has been done to test these theories in the Chinese stock market. This project aims to fill these gaps.

The Chinese stock market (China A-shares) is perhaps one of the most unique equities market in the world, marked by its imbalanced market participants. Retail investors far outnumber institutional investors, which makes market behavior in the A-shares vastly different from other equities markets. For example, China A-Shares has an abnormally high turnover rate, and many believe *reversal* is a better predictor than *momentum* in China A-shares.

This project hopes to find whether industry momentum exists and the predictive power of the Shiller-CAPE ratio in China A-shares. The performance of an index that incorporates industry momentum and Shiller-CAPE will likely give us the answer.

## Methodology
>>>>>>> aececf97351d9cb7e780aac0b2c748980388bd1d

### Dependencies

This project is entirely written in python. It largely uses the [`xquant`](https://github.com/percy-xu/xquant) library developed by myself. In addition, `pandas`, `numpy`, and `plotly` are used for data processing, computation, and visualization.

### Strategy

#### Description

My index is, in essence, an **"index of indices"** - much like a fund of funds (FOF) in terms of structure. For this project, I am defining the CITIC Industry Indices (中信行业指数) as the stock selection universe. The CITIC Industry Indices includes daily-computed index for 28 industries starting from 2004-12-31.

At a cross-section, the *Relative CAPE Ratio* is computed for every industry. Industries are ranked by their Relative CAPE Ratios. The 3 industries with the highest Relative CAPE are underweighted and the 3 industries with the lowest Relative CAPE are overweighted.

This leaves us with 22 remaining industries. By calculating each industry's performance in the past 6 months, we categorize them into winners and losers. Winners (industries with strong momentum) are overweighted and losers (industries with weak momentum) are underweighted.

#### Weighting Scheme

<<<<<<< HEAD
Bunn and Shiller used a point-based weighting scheme which I find easy to understand and implement. A adapted version of this weighting scheme is used in this project. Every time my index is computed, each industry in the cross-section start with 2 points. 1 point is added when an industry is overweighted and 1 point is subtracted when an industry is underweighted. This leaves us 28 industries with points ranging from 1 to 3. Respective weights are then calculated for each industry based on its point.

#### Look-back Period

When determining an industry is a winner or a loser, we look at its performance over a period of time in the past. In our case, 6 months. This might seem like an arbitrary number - and in a sense it is. When Jegadeesh first discovered the momentum effect, he found that momentum strategies with various look-back periods are on average quite profitable and just selected 6 months as the look-back period for the rest of his paper. Moskowitz followed Jegadeesh for simplicity in his paper, and this project selects 6 months for the same reason.

### Portfolio Management

We are constructing an index, and therefore no cash is reserved in the portfolio. Our portfolio shall be a self-financed, zero-cost portfolio.
=======
Bunn and Shiller used a point-based weighting scheme which I find easy to understand and implement. A adapted version of this weighting scheme is used in this project. Every time my index is computed, each industry in the cross-section start with 2 points. 1 point is added when an industry is overweighted and 1 point is subtracted when an industry is underweighted. We now have 28 industries with points ranging from 1 to 3. Respective weights are then calculated for each industry based on its point.

#### Look-back Period

When determining an industry is a winner or a loser, we look at its performance over a period of time in the past. In our case, this look-back period 6 months. This might seem like an arbitrary number - and in a sense it is. When Jegadeesh first discovered the momentum effect, he found that momentum strategies with various look-back periods are on average quite profitable and just selected 6 months as the look-back period for the rest of his paper. Moskowitz followed Jegadeesh for simplicity in his paper, and we shall comply with this "tradition".

### Portfolio Management

We are constructing an index, and therefore no cash is reserved in the portfolio. Our portfolio is a self-financed, zero-cost portfolio.
>>>>>>> aececf97351d9cb7e780aac0b2c748980388bd1d

The portfolio is rebalanced quarterly to always incorporate the most recent information.

### Back-testing

## Result
