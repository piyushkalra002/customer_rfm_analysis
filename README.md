# Customer Retention & RFM Analysis

## Overview
Analyzing real e-commerce transaction data to identify customer segments and quantify revenue at risk from customer churn. The goal is to answer a practical business question: which customers should the business prioritize retaining, and what's the financial case for doing so?

## Dataset
Online Retail II (UCI Machine Learning Repository) — real transactions from a UK-based online gift retailer, December 2009 to December 2011.
Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

## Tools
Python (Pandas, NumPy), SQL (SQLite), Power BI

## Progress
- [x] Data cleaning (`01_data_cleaning.ipynb`)
- [ ] SQL analysis
- [ ] RFM segmentation
- [ ] Cancellation rate analysis
- [ ] Revenue-at-risk quantification
- [ ] Power BI dashboard

## Key Findings So Far
-Started with 525,461 raw transaction rows. After removing cancelled orders, internal adjustment entries, transactions with no customer ID attached, and duplicate rows, I was left with 400,526 genuine customer purchases to actually work with.

-A couple of things worth flagging along the way: some of the "negative quantity" rows turned out to be internal warehouse notes damaged stock, lost items  rather than customer returns, with no customer ID attached to any of them. Separately, a batch of unusually high prices (up to £10,953 for a single line item) all turned out to be tagged under a special "Manual" stock code  internal adjustment charges, not real product sales. Both were investigated before being excluded, rather than assumed to be errors and dropped outright.

More to come as the SQL and RFM analysis phases are finished.

