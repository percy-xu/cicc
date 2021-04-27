# Industry Momentum + Shiller-CAPE <!-- omit in toc -->

- [What?](#what)
  - [Goal](#goal)
  - [Background](#background)
    - [Industry Momentum](#industry-momentum)
    - [Shiller-CAPE Ratio](#shiller-cape-ratio)
- [Why?](#why)
- [How?](#how)
  - [Dependencies](#dependencies)
  - [Stock Selection](#stock-selection)
  - [Portfolio Management](#portfolio-management)
  - [Back-testing](#back-testing)
- [Result](#result)

## What?

### Goal

This project explores two asset price anomalies in the equities market: **momentum** and **value**. More specifically, I attempt to develop a strategy combining the industry momentum effect and the Shiller-CAPE ratio in the China A-shares stock market.

### Background

Both industry momentum effect and Shiller-CAPE ratio have received significant attention from scholars and investors since the 1990s. This section provides some background and relevant literatures for these two topics.

#### Industry Momentum

Eugene Fama, arguably the most prominent researcher on the Efficient Market Hypothesis once said that the momentum effect is *"perhaps the biggest embarrassment to the EMH"*. Indeed, according to the EMH the momentum should not exist at all because past returns and future returns are completely irrelevant. Yet, momentum has been generating consistent excess returns since it was first proposed in [Jegadeesh (1993)](https://www.jstor.org/stable/2328882) over the last three decades.

The question that follows is naturally: *"What causes momentum?"* [Moskowitz (1999)](https://www.jstor.org/stable/798005) offers an interesting theory: **momentum effects can be explained by industries**. Moskowitz concluded that stocks within the same industry are under the same regulatory constraints and affected by the same external factors, which causes their stock prices to move in the same direction. Further, the momentum effect largely disappears once industry is being controlled.

So the next question is: *If industries do explain momentum, then why bother with individual stocks?* Moskowitz answers this question as well. He made a portfolio consisted of industry indices only and rotated among the recent winning industries, and found that the excess return exceeds that of a portfolio of recent winning individual stocks.

#### Shiller-CAPE Ratio

If such thing as an economics prophet exists, Robert Shiller will surely be one of them. Shiller famously predicted bursts of the dot com bubble and the real estate bubble in the early and mid 2000s, and one his crystal balls was the CAPE Ratio Shiller developed with John Campbell.

**C**yclically **A**djusted **P**rice-**E**arnings Ratio is centered around the simple idea of *"averaging out fluctuations"*. Shiller argues that measurements of company performance such as the PE ratio or dividend yield can be overly influenced by short term fluctuations. For example, the PE ratio for a company in 2021 Q1 alone can be affected by a temporary price shock and therefore do not have significant predictive power for future returns. When forecasting long-term future returns, one should really look at long-term past returns. **CAPE is calculated by taking the average of inflation-adjusted earnings and prices over the past 10 years, or in short, the smoothed earnings.** [Campbell and Shiller (1998)](https://jpm.pm-research.com/content/24/2/11) examined the smoothed earnings of the US stock market and concluded it was dangerously overvalued. Sure enough, the dot com bubble bursted in less than 5 years.

More recently, [Bunn and Shiller (2014)](https://www.nber.org/papers/w20370) examined the CAPE ratio in a larger historical scope. Going back to as far as the beginning of the 1870s, Bunn and Shiller computed the CAPE ratios for the Industrials sector, the Utilities sector and the Railroads sector. They then designed a sector rotation strategy that overweighed the undervalued sector and underweighed the overvalued sector. This strategy provided 1.09% annualized, inflation-adjusted excess total return over 110 years.

## Why?

Much of the existing literatures on industry momentum and Shiller-CAPE limit their scopes to the US stock market, and little has been done to test these theories in the Chinese stock market.

The Chinese stock market (China A-shares) is perhaps one of the most imbalanced equities market in the world in terms of market participants. Retail investors far outnumber institutional investors, which makes market behavior in the A-shares vastly different from other equities markets. In fact, many believe *reversal* is a better predictor than *momentum* in China A-shares.

This project hopes to find whether industry momentum exists in China A-shares and the predictive power of the Shiller-CAPE ratio. The performance of an index that incorporates industry momentum and Shiller-CAPE will likely give us the answer.

## How?

### Dependencies

### Stock Selection

### Portfolio Management

### Back-testing

## Result
