import streamlit as st
import pandas as pd
import os
import csv
from datetime import datetime

# Hamare existing engine se qualification logic import
from app import analyze_prospect, fetch_live_website, generate_infinite_target_candidates, get_already_processed_domains

st.set_page_config(
    page_title="Bright Tech - Lead Intelligence Engine",
    page_icon="⚡",
    layout="wide"
)

CSV_FILE = "bright_tech_qualified_leads.csv"

# Custom Styling
st.markdown("""
    <style>
    .main-header { font-size: 28px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-header { color: #64748B; font-size: 14px; margin-bottom: 20px; }
    .stMetric { background-color: #F8FAFC; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚡ Bright Tech International - Lead Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">B2B Prospect Discovery & Explainable Scoring Pipeline (UK & US Markets)</div>', unsafe_allow_html=True)

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.header("🎯 Discovery Controls")
batch_size = st.sidebar.slider("Leads to Discover per Batch", min_value=1, max_value=10, value=3)

if st.sidebar.button("🚀 Discover Fresh Leads", type="primary"):
    with st.spinner("Connecting to live websites and qualifying prospects..."):
        existing_domains = get_already_processed_domains(CSV_FILE)
        candidates = generate_infinite_target_candidates(existing_domains, count=batch_size)
        new_records = []

        for item in candidates:
            domain = item["domain"]
            url = item["url"]
            market = item["market"]
            live_content = fetch_live_website(url)
            rec = analyze_prospect(domain, live_content, url, market)
            new_records.append(rec)
            existing_domains.add(domain)

        if new_records:
            file_exists = os.path.exists(CSV_FILE)
            headers = list(new_records[0].keys())
            with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(new_records)
            st.sidebar.success(f"Added {len(new_records)} fresh leads!")
        else:
            st.sidebar.warning("No new targets found.")

# ----------------- DATA LOADING -----------------
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame()

# ----------------- TOP METRICS -----------------
col1, col2, col3, col4 = st.columns(4)

total_leads = len(df) if not df.empty else 0
high_priority = len(df[df["priority_band"].str.contains("High", na=False)]) if not df.empty else 0
uk_leads = len(df[df["country"] == "United Kingdom"]) if not df.empty else 0
us_leads = len(df[df["country"] == "United States"]) if not df.empty else 0

col1.metric("Total Qualified Leads", total_leads)
col2.metric("High Priority Fit (80-100)", high_priority)
col3.metric("UK Market Prospects", uk_leads)
col4.metric("US Market Prospects", us_leads)

st.write("---")

# ----------------- FILTERS & SEARCH -----------------
if not df.empty:
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        country_filter = st.multiselect("Filter by Country", options=df["country"].unique(), default=df["country"].unique())
    with f_col2:
        band_filter = st.multiselect("Filter by Priority Band", options=df["priority_band"].unique(), default=df["priority_band"].unique())
    with f_col3:
        service_filter = st.multiselect("Filter by Recommended Service", options=df["relevant_service"].unique(), default=df["relevant_service"].unique())

    filtered_df = df[
        (df["country"].isin(country_filter)) &
        (df["priority_band"].isin(band_filter)) &
        (df["relevant_service"].isin(service_filter))
    ]

    # ----------------- TABLE DISPLAY -----------------
    st.subheader(f"📋 Prospects View ({len(filtered_df)} Matching Records)")
    
    display_cols = [
        "company_name", "official_domain", "country", "industry", 
        "relevant_service", "total_score", "priority_band", 
        "review_status", "official_contact_route"
    ]
    
    # Highlight high scores
    def highlight_score(val):
        color = '#dcfce7' if val >= 80 else ('#fef9c3' if val >= 60 else '#fee2e2')
        return f'background-color: {color}'

    styled_table = filtered_df[display_cols].style.applymap(highlight_score, subset=['total_score'])
    st.dataframe(styled_table, use_container_width=True, height=350)

    # ----------------- LEAD DETAIL & ACTIONS -----------------
    st.write("---")
    st.subheader("🔍 Prospect Intelligence Details & Governance")
    
    selected_domain = st.selectbox("Select a company to view deep rationale & evidence:", options=filtered_df["official_domain"].tolist())
    
    if selected_domain:
        row = filtered_df[filtered_df["official_domain"] == selected_domain].iloc[0]
        
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.markdown(f"**Company:** {row['company_name']}")
            st.markdown(f"**Target Geography:** {row['city_region']}, {row['country']}")
            st.markdown(f"**Operational Rationale:** {row['fit_rationale']}")
            st.markdown(f"**Evidence Notes:** `{row['evidence_notes']}`")
        with d_col2:
            st.markdown(f"**Fit Score Breakdown:** {row['total_score']} / 100")
            st.markdown(f"**Industry Fit:** {row['industry_fit_score']} pts | **Service Fit:** {row['service_relevance_score']} pts")
            st.markdown(f"**Official Route:** `{row['official_contact_route']}`")
            st.markdown(f"**Governance Status:** `{row['review_status']}` (Outreach Disabled)")

    # ----------------- DOWNLOAD SECTION -----------------
    st.write("---")
    st.subheader("📥 Export Deliverables")
    
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Technical Raw Data (CSV)",
            data=csv_bytes,
            file_name="bright_tech_qualified_leads.csv",
            mime="text/csv"
        )
        
    with col_dl2:
        if os.path.exists("Bright_Tech_Clean_Leads.xlsx"):
            with open("Bright_Tech_Clean_Leads.xlsx", "rb") as f:
                excel_bytes = f.read()
            st.download_button(
                label="📊 Download Formatted Executive Report (Excel)",
                data=excel_bytes,
                file_name="Bright_Tech_Clean_Leads.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("No leads in database yet. Click 'Discover Fresh Leads' in the sidebar to start prospecting.")