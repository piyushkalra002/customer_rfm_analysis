# Customer Retention & RFM Analysis

## Overview
Analyzing real e-commerce transaction data to identify customer segments and quantify revenue at risk from customer churn. The goal is to answer a practical business question: which customers should the business prioritize retaining, and what's the financial case for doing so?

## Dataset
Online Retail II (UCI Machine Learning Repository), real transactions from a UK-based online gift retailer, December 2009 to December 2011.
Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

## Tools
Python (Pandas, NumPy), SQL (SQLite), Power BI

## Progress
- [x] Data cleaning (`01_data_cleaning.ipynb`)
- [x] SQL analysis(`02_sql_analysis.ipynb`)
- [x] RFM segmentation(`03_rfm_segmentation.ipynb`)
- [x] Cancellation rate analysis
- [x] Revenue-at-risk quantification(`03_rfm_segmentation.ipynb`)
- [ ] Power BI dashboard

## Key Findings So Far
-Started with 525,461 raw transaction rows. After removing cancelled orders, internal adjustment entries, transactions with no customer ID attached, and duplicate rows, I was left with 400,526 genuine customer purchases to actually work with.

-A couple of things worth flagging along the way: some of the "negative quantity" rows turned out to be internal warehouse notes damaged stock, lost items  rather than customer returns, with no customer ID attached to any of them. Separately, a batch of unusually
high prices (up to £10,953 for a single line item) all turned out to be tagged under a special "Manual" stock code  internal adjustment charges, not real product sales. Both were investigated before being excluded, rather than assumed to be errors and dropped outright.

-Layered a cancellation rate on top of the RFM segments and found something counter-intuitive: Champions have the *highest* cancellation rate of all 5 segments (14.8%), not the lowest. It turns out cancellation rate tracks almost exactly with purchase frequency, not customer value — customers who order 10+ times just have more chances to cancel something along the way. Flagged 37% of Champions (407 of 1,105) as less reliable than their segment alone suggests, using a `true_champion` flag (cancellation rate under 20%).

