import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random

st.set_page_config(page_title="FinMark Security Dashboard", page_icon="Ìª°Ô∏è", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
    }
    .critical-alert {
        background-color: #fff5f5;
        border-left: 4px solid #dc3545;
    }
    .success-metric {
        background-color: #f0f9ff;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

st.title("Ìª°Ô∏è FinMark Security Operations Center")
st.markdown("### Real-time Security Analytics & Monitoring Dashboard")

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def authenticate():
    with st.form("login"):
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="admin123")
        if st.form_submit_button("Login"):
            if username == "admin" and password == "admin123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")

if not st.session_state.authenticated:
    authenticate()
else:
    # Main Dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card critical-alert">
            <h3>Critical Alerts</h3>
            <h2 style="color: #dc3545;">3</h2>
            <p>Ì∫® Requiring attention</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Active Threats", "12", "-5")
    
    with col3:
        st.metric("System Health", "98.2%", "+0.3%")
    
    with col4:
        st.metric("Daily Orders", "1,847", "+124")
    
    # Charts
    st.subheader("Ì≥ä Security Events Timeline")
    
    hours = list(range(24))
    events = [random.randint(20, 100) for _ in hours]
    threats = [random.randint(0, 5) for _ in hours]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=events, name='Total Events', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=hours, y=threats, name='Threats', line=dict(color='red')))
    fig.update_layout(title="Security Events Over 24 Hours", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Network devices
    st.subheader("Ìºê Network Device Status")
    
    device_data = {
        'Device': ['Router1', 'WebServer1', 'DBServer1', 'PC-Client-01', 'PC-Client-02'],
        'IP': ['10.0.0.1', '10.0.0.20', '10.0.0.30', '10.0.0.101', '10.0.0.102'],
        'Status': ['Ìø¢ Online', 'Ìø¢ Online', 'Ìø° Warning', 'Ìø¢ Online', 'Ì¥¥ Critical'],
        'CPU %': [45, 78, 92, 34, 12],
        'Memory %': [67, 85, 95, 45, 23]
    }
    
    df = pd.DataFrame(device_data)
    st.dataframe(df, use_container_width=True)
    
    # CSV Data Section
    st.subheader("Ì≥à Your CSV Data Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Ì≥ä Event Logs", "Ìºê Network Inventory", "Ì≥à Marketing Data", "Ì¥ç Traffic Logs"])
    
    with tab1:
        try:
            # Note: file has space in name
            event_df = pd.read_csv('event_logs .csv')
            st.write(f"Ì≥ä Loaded {len(event_df)} events from event_logs.csv")
            st.dataframe(event_df.head(10))
            
            if 'event_type' in event_df.columns:
                event_counts = event_df['event_type'].value_counts().head(10)
                fig = px.bar(x=event_counts.index, y=event_counts.values, 
                           title="Top 10 Event Types")
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Could not load event_logs.csv: {e}")
    
    with tab2:
        try:
            network_df = pd.read_csv('network_inventory.csv')
            st.write(f"Ìºê Loaded {len(network_df)} devices from network_inventory.csv")
            st.dataframe(network_df)
            
        except Exception as e:
            st.error(f"Could not load network_inventory.csv: {e}")
    
    with tab3:
        try:
            marketing_df = pd.read_csv('marketing_summary.csv')
            st.write(f"Ì≥à Loaded {len(marketing_df)} records from marketing_summary.csv")
            st.dataframe(marketing_df.head(10))
            
            if 'total_sales' in marketing_df.columns:
                fig = px.line(marketing_df.head(30), y='total_sales', 
                            title="Sales Trend")
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Could not load marketing_summary.csv: {e}")
    
    with tab4:
        try:
            traffic_df = pd.read_csv('traffic_logs.csv')
            st.write(f"Ì¥ç Loaded {len(traffic_df)} traffic records")
            st.dataframe(traffic_df)
            
        except Exception as e:
            st.error(f"Could not load traffic_logs.csv: {e}")
    
    # Auto-refresh
    if st.button("Ì¥Ñ Refresh Data"):
        st.rerun()

    st.success("‚úÖ FinMark Security Dashboard is operational!")
