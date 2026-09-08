"""
Utility functions for data loading, caching, formatting, and ROI calculations
in the Streamlit Customer RFM Analytics Application.
"""

import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

@st.cache_data(ttl=3600)
def load_rfm_data() -> pd.DataFrame:
    """Loads processed RFM dataset with Parquet preference and CSV fallback."""
    parquet_path = os.path.join(DATA_DIR, 'rfm_processed.parquet')
    csv_path = os.path.join(DATA_DIR, 'rfm_processed.csv')

    if os.path.exists(parquet_path):
        try:
            return pd.read_parquet(parquet_path)
        except Exception:
            pass
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df['Customer ID'] = df['Customer ID'].astype(str)
        return df
    raise FileNotFoundError("Processed RFM data not found in data/processed directory.")

@st.cache_data(ttl=3600)
def load_monthly_data() -> pd.DataFrame:
    """Loads monthly trend dataset."""
    csv_path = os.path.join(DATA_DIR, 'monthly_trends.csv')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_country_data() -> pd.DataFrame:
    """Loads country revenue dataset."""
    csv_path = os.path.join(DATA_DIR, 'country_revenue.csv')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_transaction_data() -> pd.DataFrame:
    """Loads cleaned transactions dataset with fallback."""
    parquet_path = os.path.join(DATA_DIR, 'transactions_summary.parquet')
    csv_path = os.path.join(DATA_DIR, 'transactions_summary.csv')

    if os.path.exists(parquet_path):
        try:
            return pd.read_parquet(parquet_path)
        except Exception:
            pass
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df['Customer ID'] = df['Customer ID'].astype(str)
        return df
    return pd.DataFrame()

def fmt_curr(val: float) -> str:
    """Format float as GBP currency (£)."""
    if abs(val) >= 1_000_000:
        return f"£{val / 1_000_000:,.2f}M"
    elif abs(val) >= 1_000:
        return f"£{val / 1_000:,.1f}K"
    else:
        return f"£{val:,.2f}"

def fmt_num(val: int) -> str:
    """Format integer with commas."""
    return f"{val:,}"

def fmt_pct(val: float) -> str:
    """Format decimal float as percentage."""
    return f"{val * 100:.1f}%"

def calculate_campaign_roi(
    rfm_df: pd.DataFrame,
    mode: str = 'targeted',
    target_top_pct: float = 0.30,
    reactivation_rate: float = 0.15,
    discount_pct: float = 0.10,
    cost_per_customer: float = 5.0
) -> dict:
    """
    Reproduces the ROI calculations from notebook 03_rfm_segmentation.ipynb.
    Mode: 'targeted' (top X% of At Risk customers by monetary spend) vs 'blanket' (all At Risk customers).
    """
    at_risk = rfm_df[rfm_df['segment'] == 'At Risk'].copy()
    n_total_at_risk = len(at_risk)
    total_at_risk_revenue = at_risk['monetary'].sum()

    if mode == 'targeted':
        target_count = int(n_total_at_risk * target_top_pct)
        target_group = at_risk.nlargest(target_count, 'monetary')
        target_revenue = target_group['monetary'].sum()
        cost = target_count * cost_per_customer
        recovered_revenue = target_revenue * reactivation_rate * (1 - discount_pct)
    else:
        target_count = n_total_at_risk
        cost = target_count * cost_per_customer
        recovered_revenue = total_at_risk_revenue * reactivation_rate * (1 - discount_pct)

    net_profit = recovered_revenue - cost
    roi_multiple = (recovered_revenue - cost) / cost if cost > 0 else 0.0

    return {
        'mode': mode.capitalize(),
        'customers_reached': target_count,
        'total_at_risk_customers': n_total_at_risk,
        'campaign_cost': cost,
        'recovered_revenue': recovered_revenue,
        'net_profit': net_profit,
        'roi_multiple': roi_multiple,
        'reactivation_rate': reactivation_rate,
        'discount_pct': discount_pct,
        'cost_per_customer': cost_per_customer
    }
