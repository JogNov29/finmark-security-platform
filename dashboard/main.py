import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="FinMark Security Dashboard",
    page_icon="🛡️",
    layout="wide"
)

def main():
    st.title("🛡️ FinMark Security Operations Center")
    st.markdown("Welcome to your security dashboard!")
    
    # Test metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Alerts", "23", "+5")
    with col2:
        st.metric("Active Threats", "7", "-2")
    with col3:
        st.metric("System Health", "98.5%", "+0.3%")
    with col4:
        st.metric("Daily Orders", "1,247", "+124")
    
    # Sample chart
    st.subheader("Sample Security Events")
    
    # Create sample data
    data = {
        'Time': ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
        'Events': [45, 52, 78, 95, 87, 63]
    }
    df = pd.DataFrame(data)
    
    fig = px.line(df, x='Time', y='Events', title='Security Events Over Time')
    st.plotly_chart(fig, use_container_width=True)
    
    st.success("✅ Streamlit dashboard is working!")

if __name__ == "__main__":
    main()