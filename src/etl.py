"""
Reproducible ETL Pipeline for Customer RFM & Cancellation Analysis

Extracts raw Online Retail II dataset, applies exact data cleaning,
computes RFM metrics, scoring & customer segmentation, calculates
cancellation rates, and saves optimized processed datasets for Streamlit.
"""

import os
import pandas as pd
import numpy as np

def run_etl(raw_data_path: str, output_dir: str):
    print("=" * 60)
    print("1. EXTRACT: Loading raw Online Retail II dataset...")
    print("=" * 60)
    
    if not os.path.exists(raw_data_path):
        raise FileNotFoundError(f"Raw data file not found at: {raw_data_path}")

    # Read raw Excel file
    df_raw = pd.read_excel(raw_data_path, engine='openpyxl')
    print(f"Raw dataset loaded. Total rows: {len(df_raw):,}")

    print("\n" + "=" * 60)
    print("2. TRANSFORM: Executing data cleaning and RFM processing...")
    print("=" * 60)

    # --- A. Data Cleaning (01_data_cleaning.ipynb) ---
    # 1. Separate cancelled and adjustment orders (Invoice starts with 'C' or 'A')
    is_cancelled_or_adj = df_raw['Invoice'].astype(str).str.startswith(('C', 'A'))
    df_clean = df_raw[~is_cancelled_or_adj].copy()
    print(f"Rows after removing 'C' and 'A' invoices: {len(df_clean):,}")

    # 2. Remove missing Customer ID
    df_clean = df_clean.dropna(subset=['Customer ID']).copy()
    print(f"Rows after removing missing Customer ID: {len(df_clean):,}")

    # 3. Remove duplicate rows
    df_clean = df_clean.drop_duplicates().copy()
    print(f"Rows after dropping duplicates: {len(df_clean):,}")

    # 4. Format Customer ID as string label
    df_clean['Customer ID'] = df_clean['Customer ID'].astype(int).astype(str)

    # 5. Calculate Order Value
    df_clean['order_value'] = df_clean['Quantity'] * df_clean['Price']

    # 6. Remove Manual adjustment stock code outliers ('M')
    manual_mask = df_clean['StockCode'].astype(str).str.upper() == 'M'
    manual_count = manual_mask.sum()
    df_clean = df_clean[~manual_mask].copy()
    print(f"Removed Manual ('M') stock code rows: {manual_count}")
    print(f"Final Cleaned Transactions count: {len(df_clean):,} rows")

    # --- B. Cancellation Analysis (04_cancellation_analysis.ipynb) ---
    df_cancelled = df_raw[df_raw['Invoice'].astype(str).str.startswith('C')].copy()
    df_cancelled = df_cancelled.dropna(subset=['Customer ID']).copy()
    df_cancelled = df_cancelled[~df_cancelled['StockCode'].astype(str).str.upper().eq('M')].copy()
    df_cancelled['Customer ID'] = df_cancelled['Customer ID'].astype(int).astype(str)

    purchase_counts = df_clean.groupby('Customer ID')['Invoice'].nunique().rename('purchase_orders')
    cancel_counts = df_cancelled.groupby('Customer ID')['Invoice'].nunique().rename('cancelled_orders')

    customer_behavior = pd.concat([purchase_counts, cancel_counts], axis=1).fillna(0)
    customer_behavior['cancellation_rate'] = (
        customer_behavior['cancelled_orders'] / (customer_behavior['purchase_orders'] + customer_behavior['cancelled_orders'])
    )

    # --- C. RFM Ingredients & Scoring (02_sql_analysis.ipynb & 03_rfm_segmentation.ipynb) ---
    max_invoice_date = df_clean['InvoiceDate'].max()

    rfm = df_clean.groupby('Customer ID').agg(
        recency=('InvoiceDate', lambda date: (max_invoice_date - date.max()).days),
        frequency=('Invoice', 'nunique'),
        monetary=('order_value', 'sum')
    ).reset_index()

    print(f"Total Unique Customers: {len(rfm):,}")

    # RFM Scoring (1 to 5 scale)
    rfm['R_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['F_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['M_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Customer Segmentation Mapping
    def segment_customer(row):
        r = row['R_score']
        f = row['F_score']
        if r >= 4 and f >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2:
            return 'Lost'
        else:
            return 'Potential'

    rfm['segment'] = rfm.apply(segment_customer, axis=1)

    # Layer Cancellation Rate & True Champion Flag
    rfm = rfm.merge(customer_behavior[['cancellation_rate', 'purchase_orders', 'cancelled_orders']], on='Customer ID', how='left')
    rfm['cancellation_rate'] = rfm['cancellation_rate'].fillna(0)
    rfm['purchase_orders'] = rfm['purchase_orders'].fillna(0).astype(int)
    rfm['cancelled_orders'] = rfm['cancelled_orders'].fillna(0).astype(int)

    rfm['true_champion'] = (rfm['segment'] == 'Champions') & (rfm['cancellation_rate'] < 0.20)

    # Aggregations for fast loading in Streamlit
    df_clean['yr'] = df_clean['InvoiceDate'].dt.year
    df_clean['mo'] = df_clean['InvoiceDate'].dt.month
    df_clean['yr_mo'] = df_clean['InvoiceDate'].dt.to_period('M').astype(str)

    monthly_trends = df_clean.groupby(['yr', 'mo', 'yr_mo']).agg(
        total_revenue=('order_value', 'sum'),
        total_orders=('Invoice', 'nunique'),
        total_items=('Quantity', 'sum')
    ).reset_index()

    country_revenue = df_clean.groupby('Country').agg(
        total_revenue=('order_value', 'sum'),
        customer_count=('Customer ID', 'nunique'),
        order_count=('Invoice', 'nunique')
    ).reset_index().sort_values('total_revenue', ascending=False)

    print("\n" + "=" * 60)
    print("3. LOAD: Saving processed Parquet & CSV files...")
    print("=" * 60)

    os.makedirs(output_dir, exist_ok=True)

    rfm_parquet_path = os.path.join(output_dir, 'rfm_processed.parquet')
    rfm_csv_path = os.path.join(output_dir, 'rfm_processed.csv')
    try:
        rfm.to_parquet(rfm_parquet_path, index=False)
        print(f"Saved: {rfm_parquet_path}")
    except Exception as e:
        print(f"Warning: Could not save Parquet ({e}). Falling back to CSV.")
    rfm.to_csv(rfm_csv_path, index=False)
    print(f"Saved: {rfm_csv_path}")

    transactions_parquet_path = os.path.join(output_dir, 'transactions_summary.parquet')
    transactions_csv_path = os.path.join(output_dir, 'transactions_summary.csv')
    tx_summary = df_clean[['Invoice', 'StockCode', 'Description', 'Quantity', 'InvoiceDate', 'Price', 'Customer ID', 'Country', 'order_value', 'yr_mo']].copy()
    tx_summary['StockCode'] = tx_summary['StockCode'].astype(str)
    tx_summary['Invoice'] = tx_summary['Invoice'].astype(str)
    tx_summary['Description'] = tx_summary['Description'].fillna('').astype(str)
    try:
        tx_summary.to_parquet(transactions_parquet_path, index=False)
        print(f"Saved: {transactions_parquet_path}")
    except Exception as e:
        print(f"Warning: Could not save Parquet ({e}). Falling back to CSV.")
    tx_summary.to_csv(transactions_csv_path, index=False)
    print(f"Saved: {transactions_csv_path}")

    monthly_csv_path = os.path.join(output_dir, 'monthly_trends.csv')
    country_csv_path = os.path.join(output_dir, 'country_revenue.csv')
    monthly_trends.to_csv(monthly_csv_path, index=False)
    country_revenue.to_csv(country_csv_path, index=False)

    print(f"Saved: {rfm_parquet_path}")
    print(f"Saved: {transactions_parquet_path}")
    print(f"Saved: {monthly_csv_path}")
    print(f"Saved: {country_csv_path}")

    # --- Validation Verification Output ---
    print("\n" + "=" * 60)
    print("ETL PIPELINE VALIDATION BENCHMARKS")
    print("=" * 60)
    print(f"• Total Clean Transactions: {len(df_clean):,} (Expected: 400,526)")
    print(f"• Total Customers: {len(rfm):,} (Expected: 4,300)")
    total_rev = rfm['monetary'].sum()
    print(f"• Total Revenue: £{total_rev:,.2f} (Expected: £8,699,701.75)")
    print("\nCustomer Counts by Segment:")
    seg_counts = rfm['segment'].value_counts()
    for seg, count in seg_counts.items():
        rev = rfm[rfm['segment'] == seg]['monetary'].sum()
        print(f"  - {seg:<12}: {count:>5} customers | Revenue: £{rev:,.2f}")
    
    at_risk_rev = rfm[rfm['segment'] == 'At Risk']['monetary'].sum()
    at_risk_pct = (at_risk_rev / total_rev) * 100
    print(f"\n• At-Risk Revenue: £{at_risk_rev:,.2f} ({at_risk_pct:.1f}% of total)")
    print(f"• True Champions (Cancellation < 20%): {rfm['true_champion'].sum()} out of {rfm[rfm['segment'] == 'Champions'].shape[0]}")
    print("=" * 60)

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, 'data', 'raw', 'online_retail_II.xlsx')
    if not os.path.exists(raw_path):
        raw_path = '/Users/piyushkalra/Downloads/online_retail_II.xlsx'
    out_dir = os.path.join(base_dir, 'data', 'processed')
    run_etl(raw_path, out_dir)
