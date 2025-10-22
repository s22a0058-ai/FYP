import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set Streamlit page configuration
st.set_page_config(
    page_title="UMK Data Anak 2022 Analysis",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# DATA LOADING, CLEANING, AND SUMMARY GENERATION
# ==========================================

# Use st.cache_data to load and process the data efficiently
@st.cache_data
def load_and_clean_data(file_path):
    """
    Loads, cleans, and processes the dataset.
    """
    try:
        # Step 1: Load Dataset
        df = pd.read_excel(file_path, sheet_name="Sheet1")
    except FileNotFoundError:
        st.error(f"File not found at: {file_path}")
        return pd.DataFrame(), {}
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), {}

    # Step 2: Basic Cleaning
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        "UMUR (BULAN)": "Umur_Bulan",
        "PENDAPATAN KELUARGA": "Pendapatan_Keluarga",
        "GAJI BAPA": "Gaji_Bapa",
        "GAJI IBU": "Gaji_Ibu",
        "GAJI PENJAGA": "Gaji_Penjaga",
        "STATUS PEMAKANAN": "Status_Pemakanan",
        "BERAT (KG)": "Berat_KG",
        "TINGGI (CM)": "Tinggi_CM"
    })

    # Replace invalid or error values
    replace_vals = ["MAKLUMAT SALAH", "Error/Tiada Data", "Error", "-", " "]
    df.replace(replace_vals, np.nan, inplace=True)

    # Fill missing or unknown text values
    df["Pendapatan_Keluarga"] = df["Pendapatan_Keluarga"].fillna("Tiada Maklumat")
    df["Status_Pemakanan"] = df["Status_Pemakanan"].fillna("Tiada Data")

    # Step 3: Convert numeric values
    df["Berat_KG"] = pd.to_numeric(df["Berat_KG"], errors="coerce")
    df["Tinggi_CM"] = pd.to_numeric(df["Tinggi_CM"], errors="coerce")
    df["Umur_Bulan"] = pd.to_numeric(df["Umur_Bulan"], errors="coerce")


    # Convert salary range to approximate numeric
    def clean_salary(val):
        if pd.isnull(val): return np.nan
        val = str(val).replace("RM", "").replace(",", "").strip()
        if "-" in val:
            try:
                a, b = val.split("-")
                return (float(a) + float(b)) / 2
            except:
                return np.nan
        try:
            return float(val)
        except:
            return np.nan

    for col in ["Gaji_Bapa", "Gaji_Ibu", "Gaji_Penjaga"]:
        df[col] = df[col].apply(clean_salary)

    # Step 4: Calculate BMI (if possible)
    def calculate_bmi(row):
        if pd.notnull(row["Berat_KG"]) and pd.notnull(row["Tinggi_CM"]) and row["Tinggi_CM"] > 0:
            height_m = row["Tinggi_CM"] / 100
            return round(row["Berat_KG"] / (height_m**2), 2)
        else:
            return np.nan

    df["BMI"] = df.apply(calculate_bmi, axis=1)

    # Step 5: Standardize location text
    df["DAERAH"] = df["DAERAH"].astype(str).str.title().str.strip()
    df["PARLIMEN"] = df["PARLIMEN"].astype(str).str.upper().str.strip()
    df["DUN"] = df["DUN"].astype(str).str.upper().str.strip()

    # Step 6: Summary Tables
    summary = {}

    # 1. Gender distribution
    summary["gender"] = df["JANTINA"].value_counts().reset_index()
    summary["gender"].columns = ['JANTINA', 'Count']

    # 2. Race distribution
    summary["race"] = df["BANGSA"].value_counts().reset_index()
    summary["race"].columns = ['BANGSA', 'Count']

    # 3. Religion distribution
    summary["religion"] = df["AGAMA"].value_counts().reset_index()
    summary["religion"].columns = ['AGAMA', 'Count']

    # 4. Nutrition status
    summary["nutrition_status"] = df["Status_Pemakanan"].value_counts().reset_index()
    summary["nutrition_status"].columns = ['Status_Pemakanan', 'Count']

    # 5. Income category
    summary["income"] = df["Pendapatan_Keluarga"].value_counts().reset_index()
    summary["income"].columns = ['Pendapatan_Keluarga', 'Count']

    # 6. Average BMI by gender
    summary["bmi_by_gender"] = df.groupby("JANTINA")["BMI"].mean().round(2).reset_index()
    summary["bmi_by_gender"].columns = ['JANTINA', 'Average_BMI']

    # 7. Average BMI by district
    summary["bmi_by_district"] = df.groupby("DAERAH")["BMI"].mean().sort_values(ascending=False).round(2).reset_index()
    summary["bmi_by_district"].columns = ['DAERAH', 'Average_BMI']

    # 8. Nutrition status by district
    summary["nutrition_by_district"] = df.groupby(["DAERAH", "Status_Pemakanan"]).size().unstack(fill_value=0)

    return df, summary

# --- Main Application ---
st.title("UMK Data Anak 2022 Dashboard 📊")
st.markdown("---")

# **IMPORTANT**: Replace this with the actual path to your file.
# Since Streamlit runs on a server, local paths like '/content/drive/MyDrive/'
# won't work unless the file is uploaded or accessible via URL/path on the server.
# For local testing, ensure the file is in the same directory or adjust the path.
FILE_PATH = "UMK_DATA_ANAK_2022.xlsx" # ASSUMING FILE IS IN THE SAME DIRECTORY

st.info(f"Attempting to load data from: `{FILE_PATH}`. Please ensure the file is accessible.")
df, summary = load_and_clean_data(FILE_PATH)

if df.empty:
    st.stop()

# ==========================================
# STREAMLIT SIDEBAR
# ==========================================
with st.sidebar:
    st.header("About the Data")
    st.write(f"Total Records: **{len(df)}**")
    st.write(f"Number of Districts: **{df['DAERAH'].nunique()}**")
    st.write(f"Missing BMI values: **{df['BMI'].isnull().sum()}**")
    st.markdown("---")
    st.header("Download Data")
    # Provide download link for the cleaned dataset (simulate the saving step)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Cleaned Data as CSV",
        data=csv,
        file_name='cleaned_UMK_DATA_ANAK_2022.csv',
        mime='text/csv',
    )


# ==========================================
# VISUALIZATIONS
# ==========================================

st.header("Key Distributions")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Gender Distribution")
    # Plotly Bar Chart for Gender
    fig_gender = px.bar(
        summary["gender"],
        x="JANTINA",
        y="Count",
        title="Gender Distribution",
        color="JANTINA",
        template="plotly_white"
    )
    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    st.subheader("Race Distribution")
    # Plotly Pie Chart for Race
    # Show only top 5 races for clarity in the pie chart
    top_races = summary["race"].head(5)
    fig_race = px.pie(
        top_races,
        names="BANGSA",
        values="Count",
        title="Top 5 Race Distribution",
        hole=.3,
    )
    st.plotly_chart(fig_race, use_container_width=True)

with col3:
    st.subheader("Religion Distribution")
    # Plotly Bar Chart for Religion
    fig_religion = px.bar(
        summary["religion"],
        x="AGAMA",
        y="Count",
        title="Religion Distribution",
        color="AGAMA",
        template="plotly_white"
    )
    st.plotly_chart(fig_religion, use_container_width=True)

st.markdown("---")
st.header("Health and Nutrition Metrics")

col4, col5 = st.columns(2)

with col4:
    st.subheader("Nutrition Status")
    # Plotly Bar Chart for Nutrition Status
    fig_nutrition = px.bar(
        summary["nutrition_status"],
        x="Status_Pemakanan",
        y="Count",
        title="Overall Nutrition Status of Children",
        color="Status_Pemakanan",
        template="plotly_white"
    )
    st.plotly_chart(fig_nutrition, use_container_width=True)

with col5:
    st.subheader("Average BMI")
    # Plotly Bar Chart for Average BMI by Gender
    fig_bmi_gender = px.bar(
        summary["bmi_by_gender"],
        x="JANTINA",
        y="Average_BMI",
        title="Average BMI by Gender",
        color="JANTINA",
        text="Average_BMI",
        template="plotly_white"
    )
    fig_bmi_gender.update_traces(texttemplate='%{text}', textposition='outside')
    fig_bmi_gender.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig_bmi_gender, use_container_width=True)

st.markdown("---")
st.header("Geographical Insights")

# Plotly Bar Chart for Average BMI by District
st.subheader("Average BMI by District (Top 10)")
fig_bmi_district = px.bar(
    summary["bmi_by_district"].head(10),
    x="DAERAH",
    y="Average_BMI",
    title="Average BMI by District (Top 10)",
    color="DAERAH",
    template="plotly_white"
)
st.plotly_chart(fig_bmi_district, use_container_width=True)

st.subheader("Nutrition Status by District")
# Plotly Stacked Bar Chart for Nutrition Status by District
# Convert wide table to long format for easier plotting in Plotly
nutrition_long = summary["nutrition_by_district"].reset_index().melt(
    id_vars="DAERAH",
    var_name="Status_Pemakanan",
    value_name="Count"
)

# Filter out 'Tiada Data' for clearer visualization if desired, or keep it.
# nutrition_long = nutrition_long[nutrition_long['Status_Pemakanan'] != 'Tiada Data']

fig_nutrition_district = px.bar(
    nutrition_long,
    x="DAERAH",
    y="Count",
    color="Status_Pemakanan",
    title="Nutrition Status Counts by District",
    template="plotly_white",
)
st.plotly_chart(fig_nutrition_district, use_container_width=True)


# ==========================================
# SUMMARY DATA TABLES
# ==========================================
st.markdown("---")
st.header("Summary Tables")

tab1, tab2, tab3 = st.tabs(["Distributions", "Average BMI", "Nutrition by District"])

with tab1:
    st.subheader("Gender, Race, Religion, and Income Distribution")
    colA, colB, colC, colD = st.columns(4)
    with colA:
        st.caption("Gender")
        st.dataframe(summary["gender"], use_container_width=True)
    with colB:
        st.caption("Race")
        st.dataframe(summary["race"].head(10), use_container_width=True)
    with colC:
        st.caption("Religion")
        st.dataframe(summary["religion"], use_container_width=True)
    with colD:
        st.caption("Income Category")
        st.dataframe(summary["income"], use_container_width=True)

with tab2:
    st.subheader("Average BMI by Gender and District")
    colE, colF = st.columns(2)
    with colE:
        st.caption("Average BMI by Gender")
        st.dataframe(summary["bmi_by_gender"], use_container_width=True)
    with colF:
        st.caption("Average BMI by District")
        st.dataframe(summary["bmi_by_district"], use_container_width=True)

with tab3:
    st.subheader("Nutrition Status Counts by District")
    st.dataframe(summary["nutrition_by_district"], use_container_width=True)
