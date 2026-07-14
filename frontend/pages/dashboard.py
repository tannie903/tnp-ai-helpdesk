import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="TNP Analytics Dashboard", layout="wide")
st.title("📊 TNP Helpdesk Analytics")

LOG_FILE = "data/query_log.csv"

if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
    st.info("No query logs available yet. Data will appear once students start using the app!")
else:
    df = pd.read_csv(LOG_FILE)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    col1, col2 = st.columns(2)
    col1.metric("Total Student Inquiries", len(df))
    col2.metric("Unique Intent Categories Traced", df['Category'].nunique())

    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Queries by Category")
        fig, ax = plt.subplots()
        df['Category'].value_counts().plot(kind='barh', ax=ax, color='#4e73df')
        st.pyplot(fig)

    with chart_col2:
        st.subheader("Query Traffic Over Time")
        df['Date'] = df['Timestamp'].dt.date
        fig, ax = plt.subplots()
        df.groupby('Date').size().plot(kind='line', marker='o', color='#1cc88a', ax=ax)
        st.pyplot(fig)

    st.markdown("---")
    st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)