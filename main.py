import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set Streamlit page configuration
st.set_page_config(
    page_title="UMK Data Anak 2022 FSN Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Use the URL for robust deployment
CLEANED_CSV_URL = 'https://raw.githubusercontent.com/s22a0058-ai/FYP/refs/heads/main/cleaned_UMK_DATA_ANAK_2022.csv'

# ==========================================
# 1. DATA LOADING AND PREPARATION
# ==========================================

@st.cache_data
def load_and_prepare_data(file_url):
    """Loads, processes, and prepares the dataset."""
    try:
        # Load Dataset from URL
        df = pd.read_csv(file_url)
        
        # Ensure key columns are numeric
        for col in ["Berat_KG", "Tinggi_CM", "Umur_Bulan", "Gaji_Bapa", "Gaji_Ibu", "Gaji_Penjaga", "BMI"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate Average Parental Income
        df["Avg_Parental_Income"] = df[["Gaji_Bapa", "Gaji_Ibu"]].mean(axis=1)

        return df

    except Exception as e:
        st.error(f"Error loading data from URL. Please check the path. Details: {e}")
        return pd.DataFrame()

# --- Load Data ---
df = load_and_prepare_data(CLEANED_CSV_URL)

if df.empty:
    st.stop()

# ==========================================
# 2. SIDEBAR FILTERS AND DOWNLOAD
# ==========================================
st.sidebar.title("🔍 Filter Data")
st.sidebar.markdown("Adjust filters below to interact with the charts.")

# Filter inputs
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

# Apply filters
df_filtered = df[
    (df["JANTINA"].isin(gender_filter)) &
    (df["BANGSA"].isin(race_filter)) &
    (df["DAERAH"].isin(district_filter))
]

# Sidebar metrics and download
st.sidebar.markdown("---")
st.sidebar.header("Data Summary")
st.sidebar.metric("Records Filtered", len(df_filtered))
st.sidebar.metric("Average BMI (Filtered)", f"{df_filtered['BMI'].mean():.2f}")

st.sidebar.markdown("---")
csv = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="⬇️ Download Cleaned Data CSV",
    data=csv,
    file_name='cleaned_UMK_DATA_ANAK_2022_filtered.csv',
    mime='text/csv',
)

# ==========================================
# 3. MAIN DASHBOARD CONTENT
# ==========================================

st.title("📊 Food Security & Nutrition (FSN) Analysis")
st.subheader("UMK Data Anak 2022")
st.markdown(f"**Total Children in Filter:** **{len(df_filtered)}**")

if df_filtered.empty:
    st.warning("No data matches the current filters. Please adjust the sidebar selections.")
    st.stop()

# --- KPI Metrics Row ---
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Children", len(df_filtered))
col2.metric("Unique Districts", df_filtered["DAERAH"].nunique())
col3.metric("Average BMI", f"{df_filtered['BMI'].mean():.2f}")
col4.metric("Avg. Parental Income (RM)", f"{df_filtered['Avg_Parental_Income'].mean():.0f}")

st.markdown("---")

# --- TAB LAYOUT ---
tab1, tab2, tab3, tab4 = st.tabs(["🧒 Demographics", "🥗 Nutrition & Health", "💰 Income Analysis", "📍 Regional Insights"])

# ------------------------------------------
# TAB 1: DEMOGRAPHICS
# ------------------------------------------
with tab1:
    st.subheader("Demographic Distributions")
    
    col_g, col_r = st.columns(2)

    with col_g:
        st.caption("Gender Distribution")
        # Gender distribution
        fig_gender = px.pie(
            df_filtered,
            names="JANTINA",
            color="JANTINA",
            title="Gender Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        fig_gender.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_gender, use_container_width=True)

    with col_r:
        st.caption("Top Race Distribution")
        # Race distribution (Fixed column naming)
        race_count = df_filtered["BANGSA"].value_counts().reset_index(name="Count").rename(columns={'index': 'Race', 'BANGSA': 'Race'})
        fig_race = px.bar(
            race_count.head(10),
            x="Race",
            y="Count",
            color="Race",
            title="Top 10 Race Distribution",
            template="plotly_white"
        )
        st.plotly_chart(fig_race, use_container_width=True)

    st.caption("Religion Distribution")
    # Religion distribution (Fixed column naming)
    religion_count = df_filtered["AGAMA"].value_counts().reset_index(name="Count").rename(columns={'index': 'Religion', 'AGAMA': 'Religion'})
    fig_religion = px.pie(
        religion_count,
        names="Religion",
        values="Count",
        title="Religion Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_religion, use_container_width=True)


# ------------------------------------------
# TAB 2: NUTRITION & HEALTH
# ------------------------------------------
with tab2:
    st.subheader("Health and Anthropometric Analysis")
    
    col_n, col_a = st.columns(2)
    
    with col_n:
        st.caption("Nutrition Status Distribution")
        # Nutrition Status Distribution (Fixed column naming)
        nutrition_count = df_filtered["Status_Pemakanan"].value_counts().reset_index(name="Count").rename(columns={'index': 'Status', 'Status_Pemakanan': 'Status'})
        fig_nutrition = px.bar(
            nutrition_count,
            x="Status",
            y="Count",
            color="Status",
            title="Nutrition Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Bold,
            template="plotly_white"
        )
        st.plotly_chart(fig_nutrition, use_container_width=True)

    with col_a:
        st.caption("BMI vs Age (Months) by Gender")
        # BMI vs Age (Scatter with Trendline)
        fig_bmi_age = px.scatter(
            df_filtered,
            x="Umur_Bulan",
            y="BMI",
            color="JANTINA",
            trendline="ols",
            title="BMI vs Age (Months)",
            hover_data=["BANGSA", "Status_Pemakanan"],
            template="plotly_white"
        )
        st.plotly_chart(fig_bmi_age, use_container_width=True)

# ------------------------------------------
# TAB 3: INCOME ANALYSIS
# ------------------------------------------
with tab3:
    st.subheader("Socio-Economic Factors")
    
    col_inc_nut, col_inc_bmi = st.columns(2)

    with col_inc_nut:
        st.caption("Household Income vs Nutrition Status")
        # Income vs Nutrition Status (Stacked Bar)
        income_nutrition = df_filtered.groupby(["Pendapatan_Keluarga", "Status_Pemakanan"]).size().reset_index(name="Count")
        fig_income = px.bar(
            income_nutrition,
            x="Pendapatan_Keluarga",
            y="Count",
            color="Status_Pemakanan",
            title="Household Income vs Nutrition Status",
            barmode="stack",
            template="plotly_white"
        )
        st.plotly_chart(fig_income, use_container_width=True)

    with col_inc_bmi:
        st.caption("Average Parental Income vs BMI")
        # Parents' income vs BMI (Scatter)
        # Note: Avg_Parental_Income is calculated on the main df, but df_filtered is a copy.
        # This chart relies on the column being present in df_filtered, which it is, 
        # but the use of df_filtered.groupby/plot is correct.
        fig_income_bmi = px.scatter(
            df_filtered,
            x="Avg_Parental_Income",
            y="BMI",
            color="JANTINA",
            title="Average Parental Income (RM) vs BMI",
            hover_data=["DAERAH", "Status_Pemakanan"],
            template="plotly_white"
        )
        st.plotly_chart(fig_income_bmi, use_container_width=True)


# ------------------------------------------
# TAB 4: REGIONAL INSIGHTS
# ------------------------------------------
with tab4:
    st.subheader("Geographical Distribution and Metrics")

    # Recalculate BMI by District on filtered data for consistent ordering
    bmi_district_filtered = df_filtered.groupby("DAERAH")["BMI"].mean().sort_values(ascending=False).reset_index()

    col_bmi_dist, col_nut_dist = st.columns(2)

    with col_bmi_dist:
        st.caption("Average BMI by District")
        # BMI by District (Bar - Top 15)
        fig_bmi_district = px.bar(
            bmi_district_filtered.head(15),
            x="DAERAH",
            y="BMI",
            color="DAERAH",
            title="Average BMI by District (Top 15)",
            template="plotly_white"
        )
        st.plotly_chart(fig_bmi_district, use_container_width=True)

    with col_nut_dist:
        st.caption("Nutrition Status by District (Stacked)")
        # Nutrition by district (Stacked Bar)
        nutrition_district = df_filtered.groupby(["DAERAH", "Status_Pemakanan"]).size().reset_index(name="Count")
        fig_nutrition_district = px.bar(
            nutrition_district,
            x="DAERAH",
            y="Count",
            color="Status_Pemakanan",
            title="Nutrition Status Counts by District",
            barmode="stack",
            template="plotly_white",
            # Order districts by BMI for a slightly more structured look
            category_orders={"DAERAH": bmi_district_filtered['DAERAH'].tolist()} 
        )
        st.plotly_chart(fig_nutrition_district, use_container_width=True)

st.markdown("---")
st.success("✅ Dashboard loaded successfully! Use the sidebar filters to explore the data.")
