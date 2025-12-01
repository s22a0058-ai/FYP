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
st.markdown(f"Total Children in Filter: {len(df_filtered)}")

if df_filtered.empty:
    st.warning("No data matches the current filters. Please adjust the sidebar selections.")
    st.stop()

# --- KPI Metrics Row ---
# --- KPI METRICS SECTION (Enhanced) ---
# Calculate key summary values
total_children = len(df_filtered)
unique_districts = df_filtered["DAERAH"].nunique()
average_bmi = round(df_filtered["BMI"].mean(), 2)

# Calculate average parental income (if available)
df_filtered["Avg_Parental_Income"] = df_filtered[["Gaji_Bapa", "Gaji_Ibu"]].mean(axis=1)
average_income = round(df_filtered["Avg_Parental_Income"].mean(), 2)

# Most common nutrition status
most_common_nutrition = df_filtered["Status_Pemakanan"].mode()[0] if not df_filtered["Status_Pemakanan"].mode().empty else "N/A"

# Display KPI cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Children", total_children)
col2.metric("Unique Districts", unique_districts)
col3.metric("Average BMI", average_bmi)
col4.metric("Average Parental Income (RM)", f"{average_income:,.2f}")

# ==========================================
# 4. FSN INSIGHT SECTION (NEW FOR FYP)
# ==========================================

st.markdown("### 🧠 Food Security & Nutrition Insights")

# --- Calculate Nutrition Summary Metrics ---
if "Status_Pemakanan" in df_filtered.columns:
    total_children = len(df_filtered)
    nutrition_counts = df_filtered["Status_Pemakanan"].value_counts()
    normal_count = nutrition_counts.get("Normal", 0)
    underweight_count = nutrition_counts.get("Kurus", 0)
    overweight_count = nutrition_counts.get("Gemuk", 0)

    normal_pct = (normal_count / total_children) * 100 if total_children > 0 else 0
    underweight_pct = (underweight_count / total_children) * 100 if total_children > 0 else 0
    overweight_pct = (overweight_count / total_children) * 100 if total_children > 0 else 0

    # Display KPI cards for Nutrition
    colA, colB, colC = st.columns(3)
    colA.metric("Normal Nutrition (%)", f"{normal_pct:.1f}%")
    colB.metric("Underweight (%)", f"{underweight_pct:.1f}%")
    colC.metric("Overweight (%)", f"{overweight_pct:.1f}%")

# --- Correlation between Income and BMI ---
if "Avg_Parental_Income" in df_filtered.columns:
    correlation = df_filtered["Avg_Parental_Income"].corr(df_filtered["BMI"])
    st.metric("Correlation (Income vs BMI)", f"{correlation:.2f}")

# --- Short Insight Summary ---
st.markdown("#### 📋 Key Interpretations")

if total_children > 0:
    insight_text = f"""
    - The dataset currently contains **{total_children} valid children records** after filtering.
    - Approximately **{normal_pct:.1f}%** of children have *normal* nutritional status, while **{underweight_pct:.1f}%** are *underweight* and **{overweight_pct:.1f}%** are *overweight*.
    - The correlation between **parental income** and **BMI** is **{correlation:.2f}**, 
      suggesting {'a positive' if correlation > 0 else 'a negative' if correlation < 0 else 'no clear'} relationship between socio-economic background and child nutrition.
    - These findings highlight the link between **economic conditions** and **nutritional outcomes**, supporting the aim of the FSN Dashboard for descriptive analysis.
    """
    st.info(insight_text)
else:
    st.warning("No data available for generating insights based on current filters.")


st.markdown("---")

# --- TAB LAYOUT ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🧒 Demographics", "🥗 Nutrition & Health", "💰 Income Analysis", "📍 Regional Insights",  "🧩 Usability Evaluation"])

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

# ------------------------------------------
# TAB 5: USABILITY EVALUATION (ADVANCED ANALYTICS)
# ------------------------------------------
with tab5:
    st.subheader("🧩 Dashboard Usability Feedback")
    st.markdown("Please rate and comment on the usability of this dashboard:")

    # --- User Input Section ---
    rating = st.slider(
        "How would you rate the dashboard’s usability? (1 = Poor, 5 = Excellent)", 
        1, 5, 3
    )
    feedback = st.text_area("Your feedback or suggestions:")

    if st.button("Submit Feedback"):
        timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        new_feedback = pd.DataFrame({
            "Timestamp": [timestamp],
            "Rating": [rating],
            "Feedback": [feedback]
        })

        try:
            existing = pd.read_csv("usability_feedback.csv")
            updated = pd.concat([existing, new_feedback], ignore_index=True)
        except FileNotFoundError:
            updated = new_feedback

        updated.to_csv("usability_feedback.csv", index=False)
        st.success("✅ Thank you! Your feedback has been recorded successfully.")
        st.write("**Your Rating:**", rating)
        st.write("**Your Comment:**", feedback)

    st.markdown("---")

    # ============================
    # ADMIN SECTION (Enhanced)
    # ============================
    st.subheader("👩‍💻 Admin Panel (Private)")

    show_admin = st.checkbox("I am the admin (show collected feedback)")

    if show_admin:
        admin_password = st.text_input("Enter admin password:", type="password")

        if admin_password == "fsn2025":  
            try:
                feedback_df = pd.read_csv("usability_feedback.csv")

                st.markdown("### 📋 Collected Feedback")
                st.dataframe(feedback_df, use_container_width=True)

                # --- Summary Metrics ---
                st.markdown("### 📊 Feedback Summary")
                avg_rating = feedback_df["Rating"].mean()
                total_feedback = len(feedback_df)
                st.metric("Average Usability Rating", f"{avg_rating:.2f} / 5")
                st.metric("Total Feedback Collected", total_feedback)

                # --- Rating Distribution Chart ---
                st.markdown("#### ⭐ Rating Distribution")
                fig_rating_dist = px.bar(
                    feedback_df["Rating"].value_counts().sort_index(),
                    title="Rating Distribution",
                    labels={"index": "Rating", "value": "Count"},
                    template="plotly_white"
                )
                st.plotly_chart(fig_rating_dist, use_container_width=True)

                # --- Rating Trend Over Time ---
                st.markdown("#### 📈 Rating Trend Over Time")
                feedback_df["Timestamp"] = pd.to_datetime(feedback_df["Timestamp"])
                fig_trend = px.line(
                    feedback_df.sort_values("Timestamp"),
                    x="Timestamp",
                    y="Rating",
                    title="Usability Rating Trend",
                    markers=True,
                    template="plotly_white"
                )
                st.plotly_chart(fig_trend, use_container_width=True)

                # --- Simple Sentiment Analysis ---
                st.markdown("#### 😊 Sentiment Analysis on Comments")

                def classify_sentiment(text):
                    text = text.lower()
                    positive_words = ["good", "nice", "easy", "helpful", "clear", "great"]
                    negative_words = ["bad", "difficult", "confusing", "slow", "not good"]

                    if any(word in text for word in positive_words):
                        return "Positive"
                    elif any(word in text for word in negative_words):
                        return "Negative"
                    else:
                        return "Neutral"

                feedback_df["Sentiment"] = feedback_df["Feedback"].fillna("").apply(classify_sentiment)

                fig_sentiment = px.pie(
                    feedback_df,
                    names="Sentiment",
                    title="Feedback Sentiment Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)

                # --- Extract Most Frequent Words ---
                st.markdown("#### 🔍 Most Common Keywords in Feedback")
                all_words = " ".join(feedback_df["Feedback"].dropna().tolist()).lower().split()
                stopwords = ["the", "and", "is", "to", "a", "of", "for", "it", "this"]
                words = [w for w in all_words if w not in stopwords and len(w) > 3]

                if words:
                    word_freq = pd.Series(words).value_counts().head(10)
                    st.bar_chart(word_freq)
                else:
                    st.info("No keywords available yet.")

                # --- Download Feedback CSV ---
                csv_data = feedback_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Download All Feedback (CSV)",
                    data=csv_data,
                    file_name="usability_feedback_collected.csv",
                    mime="text/csv"
                )

            except FileNotFoundError:
                st.warning("⚠️ No feedback data available yet.")

        elif admin_password != "":
            st.error("❌ Incorrect password. Please try again.")

    st.info("""
    This section supports **Objective 3** by allowing both data collection and 
    analysis of user feedback, helping evaluate the dashboard’s usability and effectiveness.
    """)


st.success("✅ Dashboard loaded successfully! Use the sidebar filters to explore the data.")
