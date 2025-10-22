streamlit run fsn_dashboard_app.py

# =========================================================
# DASHBOARD FOR FOOD SECURITY & NUTRITION (FSN) ANALYSIS
# Dataset: UMK DATA ANAK 2022 (CLEANED)
# =========================================================

import pandas as pd
import streamlit as st
import plotly.express as px

# ------------------------------------------
# LOAD DATA
# ------------------------------------------
st.set_page_config(page_title="FSN Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("cleaned_UMK_DATA_ANAK_2022.xlsx")
    return df

df = load_data()

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
