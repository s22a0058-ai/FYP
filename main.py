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

# ==========================================
# DATA LOADING, CLEANING, AND SUMMARY GENERATION
# ==========================================

# Use st.cache_data to load and process the data efficiently
@st.cache_data
def load_and_clean_data(file_url):
    """
    Loads, cleans, and processes the dataset from the URL.
    This function combines the cleaning steps for robustness, 
    but relies on the public CSV which is already cleaned and available.
    """
    try:
        # Step 1: Load Dataset (using the already cleaned CSV from the URL)
        df = pd.read_csv(file_url)
        st.success(f"Loaded {len(df)} records from the cleaned dataset.")

    except Exception as e:
        st.error(f"Error loading data from URL: {e}")
        st.info("The original cleaning logic is applied here for completeness, but it assumes the CSV is the final cleaned output.")
        return pd.DataFrame()

    # Apply additional derived calculations from the original script
    # Calculate Average Parental Income
    # Note: These columns (Gaji_Bapa, Gaji_Ibu) are numeric in the cleaned data.
    df["Avg_Parental_Income"] = df[["Gaji_Bapa", "Gaji_Ibu"]].mean(axis=1)

    # --- Summary Tables Generation (Re-run for display consistency) ---
    summary = {}
    summary["gender"] = df["JANTINA"].value_counts().reset_index().rename(columns={'JANTINA': 'Category', 'count': 'Count'})
    summary["race"] = df["BANGSA"].value_counts().reset_index().rename(columns={'BANGSA': 'Category', 'count': 'Count'})
    summary["religion"] = df["AGAMA"].value_counts().reset_index().rename(columns={'AGAMA': 'Category', 'count': 'Count'})
    summary["nutrition_status"] = df["Status_Pemakanan"].value_counts().reset_index().rename(columns={'Status_Pemakanan': 'Category', 'count': 'Count'})

    return df, summary

# --- Main Application ---
st.title("UMK Data Anak 2022 Dashboard 📊")
st.markdown("A consolidated view of children's demographic, health, and economic data.")
st.markdown("---")

# Use the URL of the cleaned CSV file provided in the prompt
CLEANED_CSV_URL = 'https://raw.githubusercontent.com/s22a0058-ai/FYP/refs/heads/main/cleaned_UMK_DATA_ANAK_2022.csv'

df, summary = load_and_clean_data(CLEANED_CSV_URL)

if df.empty:
    st.stop()

# ==========================================
# STREAMLIT SIDEBAR
# ==========================================
with st.sidebar:
    st.header("About the Data")
    st.write(f"Total Records: **{len(df)}**")
    st.write(f"Number of Districts: **{df['DAERAH'].nunique()}**")
    st.write(f"Mean BMI: **{df['BMI'].mean():.2f}**")
    st.markdown("---")
    st.header("Download Data")
    # Provide download link for the cleaned dataset
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Cleaned Data as CSV",
        data=csv,
        file_name='cleaned_UMK_DATA_ANAK_2022_dashboard.csv',
        mime='text/csv',
    )


# ==========================================
# VISUALIZATIONS (Based on Step 2 - Step 9 of the Plotly script)
# ==========================================

st.header("1. Demographic Distributions")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Gender Distribution 🧒")
    # Step 2: Gender Distribution
    fig_gender = px.pie(
        df,
        names="JANTINA",
        title="Gender Distribution of Children",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.4
    )
    fig_gender.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    st.subheader("Race Distribution 👩‍👩‍👧")
    # Step 3: Race Distribution (Top 10)
    df_race = df["BANGSA"].value_counts().head(10).reset_index()
    fig_race = px.bar(
        df_race,
        x="BANGSA",
        y="count",
        color="BANGSA",
        title="Top 10 Race Distribution",
        template="plotly_white"
    )
    fig_race.update_layout(xaxis_title="Race", yaxis_title="Count")
    st.plotly_chart(fig_race, use_container_width=True)

st.markdown("---")
st.header("2. Health and Income Analysis")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Nutrition Status Distribution")
    # Step 4: Nutrition Status Distribution
    df_nutrition = df["Status_Pemakanan"].value_counts().reset_index()
    fig_nutrition = px.bar(
        df_nutrition,
        x="Status_Pemakanan",
        y="count",
        title="Overall Nutrition Status Distribution",
        color="Status_Pemakanan",
        template="plotly_white"
    )
    st.plotly_chart(fig_nutrition, use_container_width=True)

with col4:
    st.subheader("BMI vs Age (Months) by Gender 📈")
    # Step 6: BMI vs Age by Gender
    fig_bmi_age = px.scatter(
        df,
        x="Umur_Bulan",
        y="BMI",
        color="JANTINA",
        trendline="ols",
        title="BMI vs Age (Months) by Gender",
        hover_data=["BANGSA", "Status_Pemakanan"],
        template="plotly_white"
    )
    fig_bmi_age.update_layout(xaxis_title="Age (Months)", yaxis_title="BMI")
    st.plotly_chart(fig_bmi_age, use_container_width=True)

st.subheader("Household Income vs Nutrition Status 💰")
# Step 5: Household Income vs Nutrition Status
income_nutrition = df.groupby(["Pendapatan_Keluarga", "Status_Pemakanan"]).size().reset_index(name="Count")
fig_income = px.bar(
    income_nutrition,
    x="Pendapatan_Keluarga",
    y="Count",
    color="Status_Pemakanan",
    title="Household Income vs Nutrition Status (Stacked)",
    barmode="stack",
    template="plotly_white"
)
fig_income.update_layout(xaxis_title="Pendapatan Keluarga", yaxis_title="Number of Children")
st.plotly_chart(fig_income, use_container_width=True)


st.subheader("Average Parental Income vs BMI 💵")
# Step 9: Correlation between Parents’ Income and BMI
# df["Avg_Parental_Income"] calculated in load_and_clean_data
fig_income_bmi = px.scatter(
    df,
    x="Avg_Parental_Income",
    y="BMI",
    color="JANTINA",
    title="Average Parental Income vs BMI",
    hover_data=["DAERAH", "Status_Pemakanan"],
    template="plotly_white"
)
fig_income_bmi.update_layout(xaxis_title="Average Monthly Income (RM)", yaxis_title="BMI")
st.plotly_chart(fig_income_bmi, use_container_width=True)

st.markdown("---")
st.header("3. Geographical Insights")

col5, col6 = st.columns(2)

with col5:
    st.subheader("Average BMI by District 🏙️")
    # Step 7: Average BMI by District (Top 15)
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
    # Step 8: Nutrition Status by District
    nutrition_district = df.groupby(["DAERAH", "Status_Pemakanan"]).size().reset_index(name="Count")
    fig_nutrition_district = px.bar(
        nutrition_district,
        x="DAERAH",
        y="Count",
        color="Status_Pemakanan",
        title="Nutrition Status Counts by District (Stacked)",
        barmode="stack",
        template="plotly_white"
    )
    fig_nutrition_district.update_layout(xaxis_title="District", yaxis_title="Number of Children")
    st.plotly_chart(fig_nutrition_district, use_container_width=True)
