#!/bin/bash
# FinMark System Startup Script

echo "🚀 Starting FinMark Security Operations Center..."

# Check if Django is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Django already running on port 8000"
else
    echo "🔧 Starting Django server..."
    python manage.py runserver 0.0.0.0:8000 &
    sleep 3
fi

# Check if Streamlit is already running
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Streamlit already running on port 8501"
else
    echo "🎨 Starting Streamlit dashboard..."
    streamlit run dashboard/finmark_dashboard.py --server.port 8501 &
    sleep 2
fi

echo ""
echo "🎉 FinMark System is ready!"
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "🔧 Django Admin: http://localhost:8000/admin"
echo "🔌 API: http://localhost:8000/api"
echo ""
echo "👤 Login credentials:"
echo "   Admin: admin/admin123"
echo "   Security: security/security123"
echo "   Analyst: analyst/analyst123"
echo ""
