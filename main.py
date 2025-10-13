import streamlit as st
import pandas as pd
import io

st.set_page_config(
    page_title="Scientific Visualization" # Changed title here
)

st.header("Scientific Visualization", divider="gray")

# --- Page Configuration (Retaining the title change from the previous step) ---
st.set_page_config(
    page_title="Scientific Visualization",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.header("Faculty Data Analysis", divider="gray")
st.markdown("Analyzing gender distribution from the Arts Faculty dataset using Plotly for interactive visualization.")

# --- Data Loading ---
@st.cache_data
def load_data():
    """Loads the dataset from the specified GitHub URL."""
    url = 'https://raw.githubusercontent.com/s22a0058-ai/SVisual25/refs/heads/main/arts_faculty_data.csv'
    try:
        # Load data directly into a DataFrame
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading data from URL: {e}")
        return pd.DataFrame()

df = load_data()

# Check if data loaded successfully
if df.empty:
    st.stop()

st.subheader("1. Raw Data Preview")
st.dataframe(df.head(), use_container_width=True)

# --- Data Processing ---
st.subheader("2. Gender Distribution Counts")

# Calculate gender counts. Using 'df' as the variable name instead of 'arts_df'
if 'Gender' in df.columns:
    gender_counts = df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    st.dataframe(gender_counts, use_container_width=True, hide_index=True)
else:
    st.error("The DataFrame must contain a column named 'Gender' for analysis.")
    st.stop()

# --- Plotly Visualization ---

st.subheader("3. Interactive Visualizations (Plotly)")

col1, col2 = st.columns(2)

# Plotly Pie Chart (in col1)
with col1:
    st.markdown("##### Pie Chart: Percentage Distribution")
    fig_pie = px.pie(
        gender_counts,
        values='Count',
        names='Gender',
        title='Distribution of Gender in Arts Faculty',
        color_discrete_sequence=['#3b82f6', '#f87171'] # Tailwind blue-500 and red-400
    )
    fig_pie.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#ffffff', width=1.5)))
    st.plotly_chart(fig_pie, use_container_width=True)

# Plotly Bar Chart (in col2)
with col2:
    st.markdown("##### Bar Chart: Absolute Counts")
    fig_bar = px.bar(
        gender_counts,
        x='Gender',
        y='Count',
        title='Distribution of Gender in Arts Faculty',
        color='Gender',
        color_discrete_sequence=['#3b82f6', '#f87171'],
        text='Count'
    )
    fig_bar.update_layout(xaxis_title='Gender', yaxis_title='Count')
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

# --- CSV Download (Streamlit style) ---
st.subheader("4. Download Data")

# Convert the DataFrame to CSV bytes in memory
csv_data = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Arts Faculty Data as CSV",
    data=csv_data,
    file_name='arts_faculty_data_analyzed.csv',
    mime='text/csv',
    help='Click here to download the original data file.'
)

st.markdown("""
<style>
/* Custom styling for better app aesthetics */
.stDownloadButton > button {
    background-color: #10b981; /* Emerald-500 */
    color: white;
    font-weight: bold;
    border-radius: 0.5rem;
    padding: 0.75rem 1.5rem;
    transition: all 0.2s;
}
.stDownloadButton > button:hover {
    background-color: #059669; /* Emerald-600 */
}
</style>
""", unsafe_allow_html=True)
