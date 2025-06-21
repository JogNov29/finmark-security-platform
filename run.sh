#!/bin/bash

echo "� Starting your FinMark Project"
echo "==============================="

# Activate your existing virtual environment
source env/bin/activate

# Install any missing packages
pip install streamlit plotly

# Run migrations
echo "� Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Load your CSV data
echo "� Loading your CSV data..."
python load_your_data.py

# Start Django API server
echo "� Starting Django API server..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Wait for Django
sleep 3

# Start Streamlit dashboard
echo "� Starting Streamlit dashboard..."
cd dashboard
streamlit run main.py --server.port=8501 --server.address=0.0.0.0 &
STREAMLIT_PID=$!

cd ..

echo ""
echo "✅ FinMark is running!"
echo "===================="
echo ""
echo "�️ Dashboard: http://localhost:8501"
echo "� API: http://localhost:8000/api/"
echo "⚙️ Admin: http://localhost:8000/admin/"
echo ""
echo "� Login: admin / admin123"
echo ""
echo "� Your CSV files have been loaded:"
echo "   • event_logs.csv (with space in name)"
echo "   • network_inventory.csv"
echo "   • marketing_summary.csv"
echo "   • traffic_logs.csv" 
echo "   • trend_report.csv"
echo ""
echo "� Press Ctrl+C to stop"

# Keep running
trap "echo '� Stopping...'; kill $DJANGO_PID $STREAMLIT_PID 2>/dev/null; exit" INT
while true; do sleep 1; done
