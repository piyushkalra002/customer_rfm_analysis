# Customer RFM Analytics & Retention Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-ETL%20Engine-orange.svg)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Data%20Viz-brightgreen.svg)](https://plotly.com/)

An end-to-end, reproducible **Customer Analytics & Data Engineering Pipeline** powering a live **Streamlit Dashboard**. Built for **Xeno's AI Native Data Analyst Internship Application**.

---

## 📌 Executive Summary & Business Context

This project converts transaction data from the **Online Retail II** dataset (UK-based online gift retailer) into actionable customer retention strategies. Standard transactional reporting often ignores hidden customer churn and order cancellation behavior. This application builds a 5-quantile **RFM (Recency, Frequency, Monetary)** model coupled with an independent **Order Cancellation Engine** to identify high-value accounts at risk of churning and quantify the return on investment (ROI) of targeted retention campaigns.

### Key Business Highlights
- **Total Revenue**: **£8.70M** (£8,699,701.75) generated across **4,300 distinct customers** and **400,526 cleaned transactions**.
- **Pareto Concentration**: The top **25.7% of customers (Champions)** generate **66.7% (£5.80M)** of total revenue.
- **At-Risk Opportunity**: **697 customers (£1.03M / 11.8% of revenue)** are categorized as **At Risk**. Crucially, their average historical spend (**£1,471.84**) is virtually identical to current **Loyal customers (£1,471.74)**—proving these are high-value accounts experiencing friction rather than low-value shoppers drifting away.
- **Cancellation Masking Effect**: **36.8% of Champions (407 customers)** have order cancellation rates exceeding **20%**, masking operational dissatisfaction under high completed purchase metrics.
- **Targeted Campaign ROI**: Reaching out to the **top 30% of At-Risk accounts by spend** delivers an **89.9x ROI** (£95.0K recovered revenue vs £1.0K cost), outperforming a blanket campaign (**30.8x ROI**) by **2.9x in capital efficiency**.

---

## 🛠️ ETL Pipeline Architecture

The application relies on a modular, reproducible ETL pipeline (`src/etl.py`) that pre-processes raw data offline and outputs optimized Parquet datasets for instantaneous Streamlit page loads:

```
                  ┌───────────────────────────────┐
                  │   Raw Online Retail II Data   │
                  │   (online_retail_II.xlsx)     │
                  └──────────────┬────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────┐
│                     EXTRACT & TRANSFORM ENGINE                    │
│                                                                   │
│ 1. Data Cleaning:                                                 │
│    • Remove Invoices starting with 'C' (Cancelled) and 'A'        │
│    • Drop null Customer IDs & exact duplicates                    │
│    • Exclude Manual stock code outliers ('M')                     │
│    • Calculate order_value = Quantity * Price                     │
│                                                                   │
│ 2. Cancellation Analysis:                                         │
│    • Extract cancelled invoices, compute per-customer cancel rate  │
│                                                                   │
│ 3. RFM Engine & Quantile Scoring:                                 │
│    • Calculate Recency (days), Frequency (orders), Monetary (£)  │
│    • Apply 5-quantile qcut scoring for R, F, M                    │
│    • Map segments: Champions, Loyal, At Risk, Lost, Potential     │
│    • Flag True Champions (Champions with cancel rate < 20%)       │
└────────────────────────────────┬──────────────────────────────────┘
                                 │
                                 ▼
                  ┌───────────────────────────────┐
                  │      LOAD: PARQUET STORAGE    │
                  │  • rfm_processed.parquet      │
                  │  • transactions_summary.parquet│
                  └──────────────┬────────────────┘
                                 │
                                 ▼
                  ┌───────────────────────────────┐
                  │      STREAMLIT DASHBOARD      │
                  │   (app.py - cached @st.cache) │
                  └───────────────────────────────┘
```

---

## 📊 Validated Metric Benchmarks (Notebook Exact Match)

The ETL pipeline outputs were validated against the original exploratory notebooks (`01_data_cleaning.ipynb` through `04_cancellation_analysis.ipynb`):

| Metric | Notebook Value | Pipeline Output | Validation Status |
| :--- | :--- | :--- | :--- |
| **Clean Transactions** | 400,526 | 400,526 | ✅ Exact Match |
| **Unique Customers** | 4,300 | 4,300 | ✅ Exact Match |
| **Total Monetary Revenue** | £8,699,701.75 | £8,699,701.75 | ✅ Exact Match |
| **Champions Count / Revenue** | 1,105 / £5,804,350.51 | 1,105 / £5,804,350.51 | ✅ Exact Match |
| **Loyal Count / Revenue** | 778 / £1,145,016.01 | 778 / £1,145,016.01 | ✅ Exact Match |
| **At Risk Count / Revenue** | 697 / £1,025,870.13 | 697 / £1,025,870.13 | ✅ Exact Match |
| **Lost Count / Revenue** | 1,022 / £396,594.50 | 1,022 / £396,594.50 | ✅ Exact Match |
| **Potential Count / Revenue** | 698 / £327,870.60 | 698 / £327,870.60 | ✅ Exact Match |
| **True Champions Count** | 698 | 698 | ✅ Exact Match |
| **Targeted Campaign ROI** | 89.9x | 89.9x | ✅ Exact Match |

---

## 📁 Repository Structure

```
customer_rfm_analysis/
├── .streamlit/
│   └── config.toml             # Custom dashboard theme
├── data/
│   ├── raw/                    # Raw Online Retail II dataset
│   └── processed/              # Processed Parquet/CSV data
│       ├── rfm_processed.parquet
│       ├── transactions_summary.parquet
│       ├── monthly_trends.csv
│       └── country_revenue.csv
├── notebooks/                  # Preserved exploratory Jupyter Notebooks
│   ├── 01_data_cleaning.ipynb
│   ├── 02_sql_analysis.ipynb
│   ├── 03_rfm_segmentation.ipynb
│   └── 04_cancellation_analysis.ipynb
├── src/
│   ├── __init__.py
│   ├── etl.py                  # Standalone ETL Script
│   └── utils.py                # Data cached loaders & ROI calculation helpers
├── app.py                      # Main Streamlit Dashboard Application
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 💻 Local Setup & Execution Guide

Follow these steps to run the ETL pipeline and launch the Streamlit application locally:

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/YOUR_USERNAME/customer_rfm_analysis.git
cd customer_rfm_analysis

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the ETL Pipeline
To execute data extraction, transformation, RFM quantile scoring, and Parquet dataset generation:
```bash
python src/etl.py
```

### 4. Launch Streamlit Application
```bash
streamlit run app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Community Cloud

To deploy this project live on **Streamlit Community Cloud** (`streamlit.app`):

1. Push this repository to your GitHub account:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Customer RFM Analytics Live App"
   git remote add origin https://github.com/YOUR_USERNAME/customer_rfm_analysis.git
   git branch -M main
   git push -u origin main
   ```
2. Log into [share.streamlit.io](https://share.streamlit.io/) with your GitHub account.
3. Click **"New app"**.
4. Select your repository (`YOUR_USERNAME/customer_rfm_analysis`), branch (`main`), and set Main file path to `app.py`.
5. Click **"Deploy!"**. Your live dashboard link will be generated instantly.

---

## 👨‍💻 Candidate Information

- **Role Applied**: AI Native Data Analyst Intern
- **Company**: Xeno
- **Author**: Piyush Kalra
