import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="TNP Analytics Dashboard", layout="wide")
st.title("TNP Helpdesk Analytics")

LOG_FILE = "data/query_log.csv"

def has_data(file_path):
    if not os.path.exists(file_path):
        return False
    try:
        return not pd.read_csv(file_path).empty
    except:
        return False

if not has_data(LOG_FILE):
    col1, col2 = st.columns(2)
    col1.metric("Total Student Inquiries", 0)
    col2.metric("Unique Intent Categories Traced", 0)
    st.markdown("---")
    st.info("No query logs available yet. Data will appear once students start using the app!")
else:
    df = pd.read_csv(LOG_FILE)
    
    # FORCE ALL COLUMN NAMES TO LOWERCASE (Fixes any capitalization mismatch instantly)
    df.columns = df.columns.str.lower()

    # Safely parse the lowercase timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    col1, col2 = st.columns(2)
    col1.metric("Total Student Inquiries", len(df))
    col2.metric("Unique Intent Categories Traced", df['category'].nunique())

    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Queries by Category")
        fig, ax = plt.subplots()
        df['category'].value_counts().plot(kind='barh', ax=ax, color='#4e73df')
        st.pyplot(fig)

    with chart_col2:
        st.subheader("Query Traffic Over Time")
        df['Date'] = df['timestamp'].dt.date
        fig, ax = plt.subplots()
        df.groupby('Date').size().plot(kind='line', marker='o', color='#1cc88a', ax=ax)
        st.pyplot(fig)

    st.markdown("---")
    st.dataframe(df.sort_values(by="timestamp", ascending=False), use_container_width=True)