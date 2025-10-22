import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set Streamlit page configuration
st.set_page_config(
    page_title="UMK Data Anak 2022 Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Use the URL of the cleaned CSV file from your GitHub repository
CLEANED_CSV_URL = 'https://raw.githubusercontent.com/s22a0058-ai/FYP/refs/heads/main/cleaned_UMK_DATA_ANAK_2022.csv'

# ==========================================
# DATA LOADING AND PREPARATION
# ==========================================

# Use st.cache_data to load and process the data efficiently
@st.cache_data
def load_and_prepare_data(file_url):
    """
    Loads the cleaned dataset and performs final preparation steps 
    like calculating average income.
    """
    try:
        # Step 1: Load Dataset (using the already cleaned CSV from the URL)
        df = pd.read_csv(file_url)
        
        # Ensure key columns are numeric after loading (if needed)
        for col in ["Berat_KG", "Tinggi_CM", "Umur_Bulan", "Gaji_Bapa", "Gaji_Ibu", "Gaji_Penjaga", "BMI"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Final Step: Calculate Average Parental Income (for Step 9 visualization)
        df["Avg_Parental_Income"] = df[["Gaji_Bapa", "Gaji_Ibu"]].mean(axis=1)

        # Generate simple summaries for key metrics
        summary = {}
        summary["gender"] = df["JANTINA"].value_counts().reset_index().rename(columns={'JANTINA': 'Category', 'count': 'Count'})
        summary["nutrition_status"] = df["Status_Pemakanan"].value_counts().reset_index().rename(columns={'Status_Pemakanan': 'Category', 'count': 'Count'})
        
        return df, summary

    except Exception as e:
        st.error(f"Error loading or preparing data from URL: {e}")
        st.info("Please verify the GitHub URL is correct and accessible as a raw CSV file.")
        return pd.DataFrame(), {}

# --- Load Data ---
df, summary = load_and_prepare_data(CLEANED_CSV_URL)

if df.empty:
    st.stop()

# =========================================================
# DASHBOARD FOR FOOD SECURITY & NUTRITION (FSN) ANALYSIS
# Dataset: UMK DATA ANAK 2022 (CLEANED)
# =========================================================

import pandas as pd
import streamlit as st
import plotly.express as px

# ==========================================
# CONSTANT & DATA LOADING
# ==========================================
CLEANED_CSV_URL = 'https://raw.githubusercontent.com/s22a0058-ai/FYP/refs/heads/main/cleaned_UMK_DATA_ANAK_2022.csv'

@st.cache_data
def load_data(file_url):
    """Loads the cleaned dataset from a public URL."""
    try:
        df = pd.read_csv(file_url)
        
        # Ensure 'Avg_Parental_Income' exists before filtering
        df["Avg_Parental_Income"] = df[["Gaji_Bapa", "Gaji_Ibu"]].mean(axis=1)

        # Standardize 'index' column names for value_counts() to 'Category' and 'Count'
        # This prevents the need to hardcode 'index' later.
        
        return df
    except Exception as e:
        st.error(f"Failed to load data from URL: {e}")
        st.stop()
        
df = load_data(CLEANED_CSV_URL)

# ------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------
st.sidebar.title("🔍 Filters")

# Dropdown filters
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
    "Select District",
    options=df["DAERAH"].dropna().unique(),
    default=df["DAERAH"].dropna().unique()
)

# Apply filters
df_filtered = df[
    (df["JANTINA"].isin(gender_filter)) &
    (df["BANGSA"].isin(race_filter)) &
    (df["DAERAH"].isin(district_filter))
]

# ------------------------------------------
# DASHBOARD TITLE
# ------------------------------------------
st.title("📊 Dashboard for Food Security & Nutrition (FSN) Analysis")
st.markdown("""
This interactive dashboard presents demographic and nutrition data from **UMK Anak 2022**.
You can explore relationships between **income, BMI, and nutrition status** by gender, race, and district.
""")

# ------------------------------------------
# KPI METRICS SECTION
# ------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Total Children", len(df_filtered))
col2.metric("Unique Districts", df_filtered["DAERAH"].nunique())
col3.metric("Average BMI", round(df_filtered["BMI"].mean(), 2))

st.divider()

# ------------------------------------------
# TAB LAYOUT (EASY NAVIGATION)
# ------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["🧒 Demographics", "🥗 Nutrition", "💰 Income Analysis", "📍 Regional Insights"])

# ------------------------------------------
# TAB 1: DEMOGRAPHICS
# ------------------------------------------
with tab1:
    st.subheader("🧒 Demographic Overview")

    # Gender distribution
    fig_gender = px.pie(
        df_filtered,
        names="JANTINA",
        title="Gender Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    fig_gender.update_traces(textinfo="percent+label")

    # Race distribution
    race_count = df_filtered["BANGSA"].value_counts().reset_index()
    fig_race = px.bar(
        race_count,
        x="index",
        y="BANGSA",
        color="index",
        title="Race Distribution"
    )

    # Religion distribution
    religion_count = df_filtered["AGAMA"].value_counts().reset_index()
    fig_religion = px.pie(
        religion_count,
        names="index",
        values="AGAMA",
        title="Religion Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    st.plotly_chart(fig_gender, use_container_width=True)
    st.plotly_chart(fig_race, use_container_width=True)
    st.plotly_chart(fig_religion, use_container_width=True)

# ------------------------------------------
# TAB 2: NUTRITION
# ------------------------------------------
with tab2:
    st.subheader("🥗 Nutrition Analysis")

    # Nutrition Status Distribution
    fig_nutrition = px.bar(
        df_filtered["Status_Pemakanan"].value_counts().reset_index(),
        x="index",
        y="Status_Pemakanan",
        color="index",
        title="Nutrition Status Distribution",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    # BMI vs Age
    fig_bmi_age = px.scatter(
        df_filtered,
        x="Umur_Bulan",
        y="BMI",
        color="JANTINA",
        trendline="ols",
        title="BMI vs Age (Months) by Gender",
        hover_data=["BANGSA", "Status_Pemakanan"]
    )

    # BMI by District
    bmi_district = df_filtered.groupby("DAERAH")["BMI"].mean().sort_values(ascending=False).reset_index()
    fig_bmi_district = px.bar(
        bmi_district.head(15),
        x="DAERAH",
        y="BMI",
        color="DAERAH",
        title="Average BMI by District (Top 15)"
    )

    st.plotly_chart(fig_nutrition, use_container_width=True)
    st.plotly_chart(fig_bmi_age, use_container_width=True)
    st.plotly_chart(fig_bmi_district, use_container_width=True)

# ------------------------------------------
# TAB 3: INCOME ANALYSIS
# ------------------------------------------
with tab3:
    st.subheader("💰 Income and Nutrition Relationship")

    # Income vs Nutrition Status
    income_nutrition = df_filtered.groupby(["Pendapatan_Keluarga", "Status_Pemakanan"]).size().reset_index(name="Count")
    fig_income = px.bar(
        income_nutrition,
        x="Pendapatan_Keluarga",
        y="Count",
        color="Status_Pemakanan",
        title="Household Income vs Nutrition Status",
        barmode="stack"
    )

    # Parents' income vs BMI
    df_filtered["Avg_Parental_Income"] = df_filtered[["Gaji_Bapa", "Gaji_Ibu"]].mean(axis=1)
    fig_income_bmi = px.scatter(
        df_filtered,
        x="Avg_Parental_Income",
        y="BMI",
        color="JANTINA",
        title="Average Parental Income vs BMI",
        hover_data=["DAERAH", "Status_Pemakanan"]
    )

    st.plotly_chart(fig_income, use_container_width=True)
    st.plotly_chart(fig_income_bmi, use_container_width=True)

# ------------------------------------------
# TAB 4: REGIONAL INSIGHTS
# ------------------------------------------
with tab4:
    st.subheader("📍 Regional Insights")

    # Nutrition by district
    nutrition_district = df_filtered.groupby(["DAERAH", "Status_Pemakanan"]).size().reset_index(name="Count")
    fig_nutrition_district = px.bar(
        nutrition_district,
        x="DAERAH",
        y="Count",
        color="Status_Pemakanan",
        title="Nutrition Status by District",
        barmode="stack"
    )

    # District comparison
    district_count = df_filtered["DAERAH"].value_counts().reset_index()
    fig_district = px.bar(
        district_count,
        x="index",
        y="DAERAH",
        color="index",
        title="Number of Children by District"
    )

    st.plotly_chart(fig_nutrition_district, use_container_width=True)
    st.plotly_chart(fig_district, use_container_width=True)

# ------------------------------------------
# FOOTER SUMMARY
# ------------------------------------------
st.divider()
st.subheader("🧠 Summary Insights")
st.markdown("""
- Most children belong to middle-income families (RM 1,000–RM 3,999).
- Normal nutrition status dominates, though malnutrition exists in certain regions.
- Average BMI varies slightly by district.
- Dashboard helps visualize relationships among gender, income, and nutrition effectively.
""")

st.success("✅ Dashboard loaded successfully! Use the sidebar to filter by gender, race, and district.")


# ==========================================
# DASHBOARD LAYOUT AND VISUALIZATIONS
# ==========================================

st.title("UMK Data Anak 2022 Health & Socio-Economic Dashboard 📊")
st.markdown("---")

## 1. Demographic & Nutrition Overview

col1, col2 = st.columns(2)

with col1:
    st.subheader("Gender Distribution 🧒")
    # Step 2: Gender Distribution (Pie)
    fig_gender = px.pie(
        df,
        names="JANTINA",
        title="Gender Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )
    fig_gender.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    st.subheader("Overall Nutrition Status")
    # Step 4: Nutrition Status Distribution (Bar)
    fig_nutrition = px.bar(
        summary["nutrition_status"],
        x="Category",
        y="Count",
        title="Distribution of Nutrition Status",
        color="Category",
        template="plotly_white",
        labels={'Category': 'Status Pemakanan'}
    )
    st.plotly_chart(fig_nutrition, use_container_width=True)

st.subheader("Race Distribution 👩‍👩‍👧")
# Step 3: Race Distribution (Bar - Top 10)
df_race = df["BANGSA"].value_counts().head(10).reset_index(name="Count")
fig_race = px.bar(
    df_race,
    x="BANGSA",
    y="Count",
    color="BANGSA",
    title="Top 10 Race Distribution",
    template="plotly_white"
)
fig_race.update_layout(xaxis_title="Race", yaxis_title="Count")
st.plotly_chart(fig_race, use_container_width=True)

st.markdown("---")

## 2. Health vs. Age & Income Analysis

st.subheader("BMI, Age, and Income Relationship")

col3, col4 = st.columns(2)

with col3:
    st.caption("BMI vs Age (Months) by Gender 📈")
    # Step 6: BMI vs Age by Gender (Scatter with Trendline)
    fig_bmi_age = px.scatter(
        df,
        x="Umur_Bulan",
        y="BMI",
        color="JANTINA",
        trendline="ols",
        title="BMI vs Age (Months)",
        hover_data=["BANGSA", "Status_Pemakanan"],
        template="plotly_white"
    )
    fig_bmi_age.update_layout(xaxis_title="Age (Months)", yaxis_title="BMI")
    st.plotly_chart(fig_bmi_age, use_container_width=True)

with col4:
    st.caption("Average Parental Income vs BMI 💵")
    # Step 9: Correlation between Parents’ Income and BMI (Scatter)
    fig_income_bmi = px.scatter(
        df,
        x="Avg_Parental_Income",
        y="BMI",
        color="JANTINA",
        title="Income vs BMI",
        hover_data=["DAERAH", "Status_Pemakanan"],
        template="plotly_white"
    )
    fig_income_bmi.update_layout(xaxis_title="Avg Monthly Income (RM)", yaxis_title="BMI")
    st.plotly_chart(fig_income_bmi, use_container_width=True)


st.subheader("Household Income vs Nutrition Status 💰")
# Step 5: Household Income vs Nutrition Status (Stacked Bar)
income_nutrition = df.groupby(["Pendapatan_Keluarga", "Status_Pemakanan"]).size().reset_index(name="Count")
fig_income = px.bar(
    income_nutrition,
    x="Pendapatan_Keluarga",
    y="Count",
    color="Status_Pemakanan",
    title="Household Income vs Nutrition Status",
    barmode="stack",
    template="plotly_white"
)
fig_income.update_layout(xaxis_title="Pendapatan Keluarga", yaxis_title="Number of Children")
st.plotly_chart(fig_income, use_container_width=True)

st.markdown("---")

## 3. Geographical Insights

col5, col6 = st.columns(2)

with col5:
    st.subheader("Average BMI by District 🏙️")
    # Step 7: Average BMI by District (Bar - Top 15)
    bmi_district = df.groupby("DAERAH")["BMI"].mean().sort_values(ascending=False).reset_index()
    fig_bmi_district = px.bar(
        bmi_district.head(15),
        x="DAERAH",
        y="BMI",
        color="DAERAH",
        title="Average BMI by District (Top 15)",
        template="plotly_white"
    )
    fig_bmi_district.update_layout(xaxis_title="District", yaxis_title="Average BMI")
    st.plotly_chart(fig_bmi_district, use_container_width=True)

with col6:
    st.subheader("Nutrition Status by District 📍")
    # Step 8: Nutrition Status by District (Stacked Bar)
    nutrition_district = df.groupby(["DAERAH", "Status_Pemakanan"]).size().reset_index(name="Count")
    fig_nutrition_district = px.bar(
        nutrition_district,
        x="DAERAH",
        y="Count",
        color="Status_Pemakanan",
        title="Nutrition Status Counts by District",
        barmode="stack",
        template="plotly_white",
        category_orders={"DAERAH": bmi_district['DAERAH'].tolist()} # Order districts by BMI for consistency
    )
    fig_nutrition_district.update_layout(xaxis_title="District", yaxis_title="Number of Children")
    st.plotly_chart(fig_nutrition_district, use_container_width=True)
