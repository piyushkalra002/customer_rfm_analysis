"""
Customer RFM Analytics Dashboard - Live Streamlit Application
Job Application for Xeno's AI Native Data Analyst Internship
"""

import sys
import os
user_site = os.path.expanduser('~/Library/Python/3.14/lib/python/site-packages')
if os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as gg

# Ensure src is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.utils import (
    load_rfm_data, load_monthly_data, load_country_data, load_transaction_data,
    fmt_curr, fmt_num, fmt_pct, calculate_campaign_roi
)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Customer RFM & Retention Analytics | Xeno AI Native Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #FFFFFF;
        padding: 1.2rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0.2rem 0;
    }
    .metric-sub {
        font-size: 0.85rem;
        color: #16A34A;
        font-weight: 500;
    }
    .badge-champion { background-color: #DCFCE7; color: #166534; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
    .badge-loyal { background-color: #DBEAFE; color: #1E40AF; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
    .badge-risk { background-color: #FEE2E2; color: #991B1B; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
    .badge-lost { background-color: #F3F4F6; color: #374151; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
    .badge-potential { background-color: #FEF3C7; color: #92400E; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Load Data
try:
    rfm_df = load_rfm_data()
    monthly_df = load_monthly_data()
    country_df = load_country_data()
except Exception as e:
    st.error(f"Error loading processed dataset: {e}")
    st.info("Please run `python src/etl.py` to generate the processed dataset first.")
    st.stop()

# Segment Color Mapping
SEGMENT_COLORS = {
    'Champions': '#10B981',
    'Loyal': '#3B82F6',
    'At Risk': '#EF4444',
    'Potential': '#F59E0B',
    'Lost': '#6B7280'
}

# Sidebar Navigation & Filters
st.sidebar.image("https://img.icons8.com/color/96/analytics.png", width=64)
st.sidebar.title("Navigation")
navigation = st.sidebar.radio(
    "Select Dashboard View:",
    [
        "📌 Executive Overview",
        "🎯 RFM Segmentation",
        "⚠️ Retention & Cancellation",
        "💡 Business Insights",
        "📈 Win-Back ROI Recommendation"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏆 Candidate Submission")
st.sidebar.info("**Role:** AI Native Data Analyst Intern\n\n**Company:** Xeno\n\n**Methodology:** Exact Notebook ETL Match")

# --- HEADER AREA ---
st.markdown('<div class="main-title">Customer RFM & Retention Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Live Reproducible Analytics Engine | Data-Driven Customer Segmentation & Win-Back Strategy</div>', unsafe_allow_html=True)

# ==============================================================================
# SECTION 1: EXECUTIVE OVERVIEW
# ==============================================================================
if navigation == "📌 Executive Overview":
    st.header("Executive Summary")
    st.caption("Headline KPIs, Customer Segment Distribution, and Revenue Metrics (Validated against original notebook calculations)")

    # Top KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    tot_cust = len(rfm_df)
    tot_rev = rfm_df['monetary'].sum()
    at_risk_df = rfm_df[rfm_df['segment'] == 'At Risk']
    at_risk_cust = len(at_risk_df)
    at_risk_rev = at_risk_df['monetary'].sum()
    at_risk_pct = (at_risk_rev / tot_rev) * 100

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Customers</div>
            <div class="metric-value">{fmt_num(tot_cust)}</div>
            <div class="metric-sub">Active Accounts</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">{fmt_curr(tot_rev)}</div>
            <div class="metric-sub">Across All Orders</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #EF4444;">
            <div class="metric-title">At-Risk Customers</div>
            <div class="metric-value">{fmt_num(at_risk_cust)}</div>
            <div class="metric-sub" style="color: #EF4444;">16.2% of Customer Base</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #EF4444;">
            <div class="metric-title">At-Risk Revenue</div>
            <div class="metric-value">{fmt_curr(at_risk_rev)}</div>
            <div class="metric-sub" style="color: #EF4444;">{at_risk_pct:.1f}% of Total Revenue</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        avg_spend = tot_rev / tot_cust
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Avg Spend / Customer</div>
            <div class="metric-value">£{avg_spend:,.0f}</div>
            <div class="metric-sub">Customer Lifetime Val</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Segment Revenue & Distribution Charts
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Customer Distribution by Segment")
        seg_summary = rfm_df.groupby('segment').agg(
            customer_count=('Customer ID', 'count'),
            total_revenue=('monetary', 'sum'),
            avg_revenue=('monetary', 'mean')
        ).reset_index()

        fig_pie = px.pie(
            seg_summary,
            names='segment',
            values='customer_count',
            color='segment',
            color_discrete_map=SEGMENT_COLORS,
            hole=0.4,
            title="Customer Count Share (%)"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label+value')
        fig_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("Revenue Contribution by Segment")
        fig_bar = px.bar(
            seg_summary.sort_values('total_revenue', ascending=True),
            x='total_revenue',
            y='segment',
            color='segment',
            color_discrete_map=SEGMENT_COLORS,
            orientation='h',
            text='total_revenue',
            title="Total Revenue (£ GBP) by Segment"
        )
        fig_bar.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
        fig_bar.update_layout(
            xaxis_title="Total Revenue (£)",
            yaxis_title="",
            showlegend=False,
            margin=dict(t=40, b=10, l=10, r=40),
            height=380
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # Monthly Trend Line Chart
    if not monthly_df.empty:
        st.subheader("Monthly Revenue & Order Volume Trend (Dec 2009 – Dec 2010)")
        fig_trend = px.line(
            monthly_df,
            x='yr_mo',
            y='total_revenue',
            markers=True,
            title="Monthly Revenue (£)",
            line_shape='spline'
        )
        fig_trend.update_traces(line_color='#2563EB', line_width=3, marker_size=8)
        fig_trend.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue (£)",
            height=350,
            margin=dict(t=40, b=20, l=10, r=10)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# ==============================================================================
# SECTION 2: RFM SEGMENTATION
# ==============================================================================
elif navigation == "🎯 RFM Segmentation":
    st.header("RFM Customer Segmentation Engine")
    st.caption("5-Quantile Scoring on Recency (R), Frequency (F), and Monetary (M) values")

    # Filter Sidebar / Controls
    st.sidebar.markdown("### 🎛️ RFM Segment Filters")
    selected_segments = st.sidebar.multiselect(
        "Filter by Customer Segment:",
        options=list(SEGMENT_COLORS.keys()),
        default=list(SEGMENT_COLORS.keys())
    )

    r_range = st.sidebar.slider("Recency Range (Days):", 0, int(rfm_df['recency'].max()), (0, int(rfm_df['recency'].max())))
    f_range = st.sidebar.slider("Frequency Range (Orders):", 1, int(rfm_df['frequency'].max()), (1, int(rfm_df['frequency'].max())))

    filtered_rfm = rfm_df[
        (rfm_df['segment'].isin(selected_segments)) &
        (rfm_df['recency'] >= r_range[0]) & (rfm_df['recency'] <= r_range[1]) &
        (rfm_df['frequency'] >= f_range[0]) & (rfm_df['frequency'] <= f_range[1])
    ]

    st.write(f"Showing **{len(filtered_rfm):,}** out of **{len(rfm_df):,}** customers based on selected filters.")

    # Segment Summary Table
    st.subheader("Segment Summary Statistics")
    seg_stats = filtered_rfm.groupby('segment').agg(
        Count=('Customer ID', 'count'),
        Total_Revenue=('monetary', 'sum'),
        Avg_Revenue=('monetary', 'mean'),
        Avg_Recency=('recency', 'mean'),
        Avg_Frequency=('frequency', 'mean')
    ).reset_index()

    seg_stats['Revenue_Share'] = (seg_stats['Total_Revenue'] / rfm_df['monetary'].sum()) * 100

    # Format Display
    display_stats = seg_stats.copy()
    display_stats['Total_Revenue'] = display_stats['Total_Revenue'].apply(lambda x: f"£{x:,.2f}")
    display_stats['Avg_Revenue'] = display_stats['Avg_Revenue'].apply(lambda x: f"£{x:,.2f}")
    display_stats['Avg_Recency'] = display_stats['Avg_Recency'].apply(lambda x: f"{x:.1f} days")
    display_stats['Avg_Frequency'] = display_stats['Avg_Frequency'].apply(lambda x: f"{x:.1f} orders")
    display_stats['Revenue_Share'] = display_stats['Revenue_Share'].apply(lambda x: f"{x:.1f}%")

    st.dataframe(display_stats, use_container_width=True)

    st.markdown("---")

    # Interactive 3D RFM Scatter Plot
    st.subheader("Interactive 3D RFM Customer Distribution")
    st.caption("Explore how customers cluster across Recency (X), Frequency (Y), and Monetary (Z)")

    fig_3d = px.scatter_3d(
        filtered_rfm.sample(min(2000, len(filtered_rfm)), random_state=42),
        x='recency',
        y='frequency',
        z='monetary',
        color='segment',
        color_discrete_map=SEGMENT_COLORS,
        hover_data=['Customer ID', 'R_score', 'F_score', 'M_score', 'cancellation_rate'],
        opacity=0.75,
        log_z=True,
        title="3D RFM Space (Z-axis in Log Scale)"
    )
    fig_3d.update_layout(height=600, margin=dict(t=30, b=10, l=10, r=10))
    st.plotly_chart(fig_3d, use_container_width=True)

# ==============================================================================
# SECTION 3: RETENTION & CANCELLATION ANALYSIS
# ==============================================================================
elif navigation == "⚠️ Retention & Cancellation":
    st.header("Customer Retention & Cancellation Risk Analysis")
    st.caption("Addressing the hidden churn & order cancellation behavior excluded in standard RFM")

    # Highlights
    k1, k2, k3 = st.columns(3)

    at_risk_df = rfm_df[rfm_df['segment'] == 'At Risk']
    champions_df = rfm_df[rfm_df['segment'] == 'Champions']
    true_champions_count = rfm_df['true_champion'].sum()

    with k1:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #EF4444;">
            <div class="metric-title">At-Risk Revenue Base</div>
            <div class="metric-value">£{at_risk_df['monetary'].sum():,.2f}</div>
            <div class="metric-sub">697 Customers at Immediate Churn Risk</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        avg_at_risk = at_risk_df['monetary'].mean()
        loyal_avg = rfm_df[rfm_df['segment'] == 'Loyal']['monetary'].mean()
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #3B82F6;">
            <div class="metric-title">At-Risk vs Loyal Avg Value</div>
            <div class="metric-value">£{avg_at_risk:,.0f} vs £{loyal_avg:,.0f}</div>
            <div class="metric-sub">Identical Average Spending Capacity</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="metric-card" style="border-left-color: #10B981;">
            <div class="metric-title">True Champions</div>
            <div class="metric-value">{true_champions_count} / {len(champions_df)}</div>
            <div class="metric-sub">Champions with <20% Cancellation Rate</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Segment Cancellation Rate Comparison
    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Average Cancellation Rate by Segment")
        cancel_seg = rfm_df.groupby('segment')['cancellation_rate'].mean().reset_index()
        cancel_seg['cancellation_pct'] = cancel_seg['cancellation_rate'] * 100

        fig_cancel = px.bar(
            cancel_seg.sort_values('cancellation_pct', ascending=False),
            x='segment',
            y='cancellation_pct',
            color='segment',
            color_discrete_map=SEGMENT_COLORS,
            text='cancellation_pct',
            title="Avg Order Cancellation Rate (%)"
        )
        fig_cancel.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_cancel.update_layout(showlegend=False, yaxis_title="Cancellation Rate (%)", height=380)
        st.plotly_chart(fig_cancel, use_container_width=True)

    with c2:
        st.subheader("True Champion Filtering")
        st.write("""
        Standard RFM labels **1,105 customers** as Champions based strictly on completed purchase frequency and value. 
        However, **407 of these Champions** have a cancellation rate >= 20%, indicating recurring inventory or fulfillment friction.
        
        Filtering for **True Champions** (cancellation rate < 20%) isolates **698 genuinely loyal accounts**.
        """)

        champion_breakdown = pd.DataFrame({
            'Status': ['True Champions (<20% Cancel Rate)', 'At-Risk Champions (>=20% Cancel Rate)'],
            'Count': [true_champions_count, len(champions_df) - true_champions_count]
        })

        fig_champ = px.pie(
            champion_breakdown,
            names='Status',
            values='Count',
            color_discrete_sequence=['#10B981', '#F59E0B'],
            hole=0.5,
            title="Champions Breakdown by Operational Reliability"
        )
        fig_champ.update_traces(textinfo='percent+value+label')
        fig_champ.update_layout(height=320, margin=dict(t=30, b=10, l=10, r=10))
        st.plotly_chart(fig_champ, use_container_width=True)

    st.markdown("---")

    # Contact List for At-Risk Customers
    st.subheader("🎯 Priority Contact List: At-Risk High-Value Customers")
    st.caption("Exportable customer list ranked by Monetary value to drive targeted retention outreach")

    search_id = st.text_input("🔍 Search by Customer ID:", "")

    at_risk_list = at_risk_df[['Customer ID', 'recency', 'frequency', 'monetary', 'cancellation_rate', 'R_score', 'F_score', 'M_score']].sort_values('monetary', ascending=False)
    
    if search_id:
        at_risk_list = at_risk_list[at_risk_list['Customer ID'].str.contains(search_id)]

    at_risk_list_disp = at_risk_list.copy()
    at_risk_list_disp['monetary'] = at_risk_list_disp['monetary'].apply(lambda x: f"£{x:,.2f}")
    at_risk_list_disp['cancellation_rate'] = at_risk_list_disp['cancellation_rate'].apply(lambda x: f"{x*100:.1f}%")

    st.dataframe(at_risk_list_disp.head(100), use_container_width=True)

    csv_data = at_risk_list.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export At-Risk Customer Contact List (CSV)",
        data=csv_data,
        file_name="at_risk_priority_customers.csv",
        mime="text/csv"
    )

# ==============================================================================
# SECTION 4: BUSINESS INSIGHTS
# ==============================================================================
elif navigation == "💡 Business Insights":
    st.header("Business Insights & Findings")
    st.caption("Empirical findings extracted directly from the Online Retail II analysis")

    st.markdown("""
    ### 1. Revenue Concentration (Pareto Principle)
    - **Top 25.7% of customers (Champions)** generate **66.7% (£5.80M)** of total company revenue.
    - Top 10 individual customers alone spend over **£1.34M**, led by Customer ID `18102` (£349.2K) and `14646` (£248.4K).
    
    ### 2. High-Value At-Risk Opportunity
    - **697 customers** are categorized as **At Risk** (inactive for 2+ quantiles despite high past purchasing).
    - These customers account for **£1.03M (11.8%)** of total revenue.
    - **Crucial Metric:** Their average historical spend (**£1,471.84**) is virtually identical to current **Loyal customers (£1,471.74)**. These are established, high-value clients who stopped ordering, not low-value shoppers.

    ### 3. Order Cancellation Masking Effect
    - RFM scoring evaluates *completed* transactions.
    - By integrating cancellation history, we found that **36.8% of Champions (407 customers)** have order cancellation rates exceeding **20%**.
    - This highlights an operational risk where high-value customers experience delivery/fulfillment frustration prior to churning.

    ### 4. Geographic Revenue Dominance
    - **United Kingdom** drives **84.2% (£7.33M)** of total revenue, followed by EIRE (£340K), Netherlands (£269K), Germany (£201K), and France (£141K).
    """)

    st.markdown("---")

    if not country_df.empty:
        st.subheader("Top 10 International Revenue Markets")
        fig_country = px.bar(
            country_df.head(10),
            x='Country',
            y='total_revenue',
            text='total_revenue',
            color='total_revenue',
            color_continuous_scale='Blues',
            title="Total Revenue (£) by Country"
        )
        fig_country.update_traces(texttemplate='£%{text:,.0f}', textposition='outside')
        fig_country.update_layout(yaxis_title="Revenue (£)", height=400)
        st.plotly_chart(fig_country, use_container_width=True)

# ==============================================================================
# SECTION 5: WIN-BACK ROI RECOMMENDATION
# ==============================================================================
elif navigation == "📈 Win-Back ROI Recommendation":
    st.header("Targeted Win-Back Campaign & ROI Analysis")
    st.caption("Financial simulation comparing Targeted Outreach vs Blanket Discounts")

    st.markdown("""
    > [!TIP]
    > **Strategic Takeaway**: Reaching out to the **top 30% of At-Risk customers by spend** achieves **89.9x ROI**, outperforming a blanket campaign (**30.8x ROI**) by **2.9x in capital efficiency** while capturing 86% of potential recovered revenue.
    """)

    # Interactive ROI Calculator Controls
    st.subheader("🧮 Interactive ROI Sensitivity Simulator")
    
    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)
    with col_ctrl1:
        cost_per_cust = st.number_input("Campaign Cost / Customer (£):", min_value=1.0, max_value=50.0, value=5.0, step=1.0)
    with col_ctrl2:
        react_rate = st.slider("Reactivation Rate (%):", min_value=5.0, max_value=40.0, value=15.0, step=1.0) / 100.0
    with col_ctrl3:
        disc_rate = st.slider("Discount Offed (%):", min_value=0.0, max_value=30.0, value=10.0, step=1.0) / 100.0
    with col_ctrl4:
        target_top_pct = st.slider("Target Top % At-Risk:", min_value=10.0, max_value=100.0, value=30.0, step=5.0) / 100.0

    # Calculate ROI for Targeted vs Blanket
    sim_targeted = calculate_campaign_roi(rfm_df, mode='targeted', target_top_pct=target_top_pct, reactivation_rate=react_rate, discount_pct=disc_rate, cost_per_customer=cost_per_cust)
    sim_blanket = calculate_campaign_roi(rfm_df, mode='blanket', target_top_pct=1.0, reactivation_rate=0.12, discount_pct=disc_rate, cost_per_customer=cost_per_cust)

    st.markdown("---")

    # Side-by-Side Comparison
    r1, r2 = st.columns(2)

    with r1:
        st.subheader("🎯 Targeted Campaign (Recommended)")
        st.write(f"Targets **top {int(target_top_pct*100)}% of At-Risk accounts** ({sim_targeted['customers_reached']} customers)")
        st.markdown(f"""
        - **Campaign Cost:** £{sim_targeted['campaign_cost']:,.2f}
        - **Recovered Revenue:** £{sim_targeted['recovered_revenue']:,.2f}
        - **Net Profit:** £{sim_targeted['net_profit']:,.2f}
        - <h3 style="color:#10B981; margin-top:10px;">Return on Investment: {sim_targeted['roi_multiple']:.1f}x</h3>
        """, unsafe_allow_html=True)

    with r2:
        st.subheader("📢 Blanket Campaign")
        st.write(f"Targets **all 100% of At-Risk accounts** ({sim_blanket['customers_reached']} customers)")
        st.markdown(f"""
        - **Campaign Cost:** £{sim_blanket['campaign_cost']:,.2f}
        - **Recovered Revenue:** £{sim_blanket['recovered_revenue']:,.2f}
        - **Net Profit:** £{sim_blanket['net_profit']:,.2f}
        - <h3 style="color:#2563EB; margin-top:10px;">Return on Investment: {sim_blanket['roi_multiple']:.1f}x</h3>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Project Notebook Baseline ROI Matrix
    st.subheader("Baseline Sensitivity Matrix (Project Notebook Benchmarks)")
    st.caption("Replicating the 9 cost/reactivation scenario matrix from notebook 03_rfm_segmentation.ipynb")

    matrix_rows = []
    at_risk_df = rfm_df[rfm_df['segment'] == 'At Risk']
    top_30_cnt = int(len(at_risk_df) * 0.30)
    top_30_sum = at_risk_df.nlargest(top_30_cnt, 'monetary')['monetary'].sum()
    all_sum = at_risk_df['monetary'].sum()

    for c in [5, 10, 20]:
        for r in [0.10, 0.15, 0.20]:
            rec_t = top_30_sum * r * 0.90
            cost_t = top_30_cnt * c
            roi_t = (rec_t - cost_t) / cost_t

            rec_b = all_sum * r * 0.90
            cost_b = len(at_risk_df) * c
            roi_b = (rec_b - cost_b) / cost_b

            matrix_rows.append({
                'Cost / Customer': f"£{c}",
                'Reactivation Rate': f"{int(r*100)}%",
                'Targeted ROI Multiple': f"{roi_t:.1f}x",
                'Blanket ROI Multiple': f"{roi_b:.1f}x",
                'Efficiency Gain': f"{(roi_t / roi_b):.1f}x higher"
            })

    matrix_df = pd.DataFrame(matrix_rows)
    st.dataframe(matrix_df, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.caption("⚡ Live Customer RFM Analytics Engine | Created for Xeno's AI Native Data Analyst Internship Application")
