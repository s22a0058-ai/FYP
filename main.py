# ==========================================
# FSN DASHBOARD — FINAL FYP VERSION
# ==========================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------
# PAGE CONFIG
# ------------------------------------------
st.set_page_config(
    page_title="FSN Dashboard (UMK FYP)",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------
# LOAD CLEANED DATA
# ------------------------------------------
CLEANED_CSV_URL = 'https://raw.githubusercontent.com/s22a0058-ai/FYP/refs/heads/main/cleaned_UMK_DATA_ANAK_2022.csv'

@st.cache_data
def load_data(file_url):
    df = pd.read_csv(file_url)
    # Ensure numeric conversion
    for col in ["Berat_KG", "Tinggi_CM", "Umur_Bulan", "Gaji_Bapa", "Gaji_Ibu", "Gaji_Penjaga", "BMI"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df["Avg_Parental_Income"] = df[["Gaji_Bapa", "Gaji_Ibu"]].mean(axis=1)
    return df

df = load_data(CLEANED_CSV_URL)

if df.empty:
    st.error("⚠️ Data not loaded. Please check the dataset URL.")
    st.stop()

# ------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------
st.sidebar.title("🔍 Filter Data")

gender_filter = st.sidebar.multiselect(
    "Select Gender",
    options=df["JANTINA"].dropna().unique(),
    default=df["JANTINA"].dropna().unique()
)
race_filter = st.sidebar.multiselect(
    "Select Race",
    options=df["BANGSA"].dropna().unique(),
    default=df["BANGSA"].dropna().unique()
)
district_filter = st.sidebar.multiselect(
    "Select District (DAERAH)",
    options=df["DAERAH"].dropna().unique(),
    default=df["DAERAH"].dropna().unique()
)

df_filtered = df[
    (df["JANTINA"].isin(gender_filter)) &
    (df["BANGSA"].isin(race_filter)) &
    (df["DAERAH"].isin(district_filter))
]

st.sidebar.markdown("---")
st.sidebar.metric("Filtered Records", len(df_filtered))
st.sidebar.metric("Average BMI", f"{df_filtered['BMI'].mean():.2f}")
st.sidebar.info(f"Dataset loaded: {df.shape[0]} rows")

# ------------------------------------------
# DASHBOARD TITLE
# ------------------------------------------
st.title("📊 Food Security & Nutrition (FSN) Dashboard")
st.caption("Developed by Fatin Nuraina — UMK Final Year Project 2025")

# ------------------------------------------
# KPI METRICS SECTION
# ------------------------------------------
st.markdown("### 📈 Key Dataset Indicators")

df_filtered["Avg_Parental_Income"] = df_filtered[["Gaji_Bapa", "Gaji_Ibu"]].mean(axis=1)
total_children = len(df_filtered)
unique_districts = df_filtered["DAERAH"].nunique()
average_bmi = round(df_filtered["BMI"].mean(), 2)
average_income = round(df_filtered["Avg_Parental_Income"].mean(), 2)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Children", total_children)
col2.metric("Unique Districts", unique_districts)
col3.metric("Average BMI", average_bmi)
col4.metric("Average Parental Income (RM)", f"{average_income:,.2f}")

# ==========================================
# OBJECTIVE 1: FSN INSIGHTS SECTION
# ==========================================
st.markdown("### 🧠 Food Security & Nutrition Insights")

if "Status_Pemakanan" in df_filtered.columns:
    nutrition_counts = df_filtered["Status_Pemakanan"].value_counts()
    normal = nutrition_counts.get("Normal", 0)
    under = nutrition_counts.get("Kurus", 0)
    over = nutrition_counts.get("Gemuk", 0)

    normal_pct = (normal / total_children * 100) if total_children > 0 else 0
    under_pct = (under / total_children * 100) if total_children > 0 else 0
    over_pct = (over / total_children * 100) if total_children > 0 else 0

    colA, colB, colC = st.columns(3)
    colA.metric("Normal Nutrition (%)", f"{normal_pct:.1f}%")
    colB.metric("Underweight (%)", f"{under_pct:.1f}%")
    colC.metric("Overweight (%)", f"{over_pct:.1f}%")

if "Avg_Parental_Income" in df_filtered.columns:
    correlation = df_filtered["Avg_Parental_Income"].corr(df_filtered["BMI"])
    st.metric("Correlation (Income vs BMI)", f"{correlation:.2f}")

st.info(f"""
**Summary:**
- Total records: {total_children}
- {normal_pct:.1f}% normal, {under_pct:.1f}% underweight, {over_pct:.1f}% overweight.
- Correlation between parental income and BMI: {correlation:.2f}
""")

# ==========================================
# OBJECTIVE 2: VISUALIZATIONS OVER SPACE
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧒 Demographics", "🥗 Nutrition & Health",
    "💰 Income & Correlation", "📍 Regional Insights", "🧩 Usability Evaluation"
])

# --- TAB 1 ---
with tab1:
    st.subheader("Demographic Overview")
    col_g, col_r = st.columns(2)

    with col_g:
        fig_gender = px.pie(df_filtered, names="JANTINA", hole=0.4, title="Gender Distribution")
        st.plotly_chart(fig_gender, use_container_width=True)

    with col_r:
        race_count = df_filtered["BANGSA"].value_counts().reset_index(name="Count").rename(columns={'index': 'Race'})
        fig_race = px.bar(race_count, x="Race", y="Count", title="Race Distribution", template="plotly_white")
        st.plotly_chart(fig_race, use_container_width=True)

# --- TAB 2 ---
with tab2:
    st.subheader("Nutrition & Health Overview")
    nutrition_count = df_filtered["Status_Pemakanan"].value_counts().reset_index(name="Count")
    fig_nutrition = px.bar(
        nutrition_count, x="Status_Pemakanan", y="Count", color="Status_Pemakanan",
        title="Nutrition Status Distribution", template="plotly_white"
    )
    st.plotly_chart(fig_nutrition, use_container_width=True)

    st.caption("BMI vs Age (Trendline by Gender)")
    fig_bmi_age = px.scatter(
        df_filtered, x="Umur_Bulan", y="BMI", color="JANTINA",
        trendline="ols", template="plotly_white"
    )
    st.plotly_chart(fig_bmi_age, use_container_width=True)

# --- TAB 3 ---
with tab3:
    st.subheader("Income and Correlation Analysis")

    fig_income_bmi = px.scatter(
        df_filtered, x="Avg_Parental_Income", y="BMI", color="JANTINA",
        trendline="ols", title="Average Parental Income vs BMI", template="plotly_white"
    )
    st.plotly_chart(fig_income_bmi, use_container_width=True)

    st.caption("Average Parental Income by Nutrition Status")
    income_by_status = df_filtered.groupby("Status_Pemakanan")["Avg_Parental_Income"].mean().reset_index()
    fig_income_status = px.bar(
        income_by_status, x="Status_Pemakanan", y="Avg_Parental_Income",
        title="Income vs Nutrition Status", template="plotly_white"
    )
    st.plotly_chart(fig_income_status, use_container_width=True)

# --- TAB 4 ---
with tab4:
    st.subheader("Regional Insights (Spatial FSN Indicators)")
    bmi_district = df_filtered.groupby("DAERAH")["BMI"].mean().reset_index().sort_values(by="BMI", ascending=False)
    fig_bmi_district = px.bar(
        bmi_district, x="DAERAH", y="BMI", color="DAERAH",
        title="Average BMI by District", template="plotly_white"
    )
    st.plotly_chart(fig_bmi_district, use_container_width=True)

    nutrition_district = df_filtered.groupby(["DAERAH", "Status_Pemakanan"]).size().reset_index(name="Count")
    fig_nutrition_district = px.bar(
        nutrition_district, x="DAERAH", y="Count", color="Status_Pemakanan",
        title="Nutrition Status by District", barmode="stack", template="plotly_white"
    )
    st.plotly_chart(fig_nutrition_district, use_container_width=True)

# --- TAB 5 ---
with tab5:
    st.subheader("Dashboard Usability Feedback (Objective 3)")
    st.markdown("Please provide your feedback on dashboard usability:")

    rating = st.slider("Rate the dashboard usability (1 = Poor, 5 = Excellent)", 1, 5, 3)
    feedback = st.text_area("Your feedback:")

    if st.button("Submit Feedback"):
        st.success("✅ Thank you for your feedback!")
        st.write("**Your Rating:**", rating)
        st.write("**Your Comment:**", feedback)

    st.info("""
    This section supports **Objective 3**, evaluating the dashboard’s usability and user perception of its data insight quality.
    """)

st.success("✅ Dashboard Loaded Successfully — Explore Each Tab to View FSN Insights.")
