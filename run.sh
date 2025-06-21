#!/bin/bash

echo "íº€ Starting your FinMark Project"
echo "==============================="

# Activate your existing virtual environment
source env/bin/activate

# Install any missing packages
pip install streamlit plotly

# Run migrations
echo "í´„ Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Load your CSV data
echo "í³Š Loading your CSV data..."
python load_your_data.py

# Start Django API server
echo "í¼ Starting Django API server..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Wait for Django
sleep 3

# Start Streamlit dashboard
echo "í³Š Starting Streamlit dashboard..."
cd dashboard
streamlit run main.py --server.port=8501 --server.address=0.0.0.0 &
STREAMLIT_PID=$!

cd ..

echo ""
echo "âœ… FinMark is running!"
echo "===================="
echo ""
echo "í»¡ï¸ Dashboard: http://localhost:8501"
echo "í´— API: http://localhost:8000/api/"
echo "âš™ï¸ Admin: http://localhost:8000/admin/"
echo ""
echo "í´ Login: admin / admin123"
echo ""
echo "í³Š Your CSV files have been loaded:"
echo "   â€¢ event_logs.csv (with space in name)"
echo "   â€¢ network_inventory.csv"
echo "   â€¢ marketing_summary.csv"
echo "   â€¢ traffic_logs.csv" 
echo "   â€¢ trend_report.csv"
echo ""
echo "í»‘ Press Ctrl+C to stop"

# Keep running
trap "echo 'í»‘ Stopping...'; kill $DJANGO_PID $STREAMLIT_PID 2>/dev/null; exit" INT
while true; do sleep 1; done
