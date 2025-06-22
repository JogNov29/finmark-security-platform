@echo off
echo 🚀 Starting FinMark Security Operations Center...

echo 🔧 Starting Django server...
start /B python manage.py runserver 0.0.0.0:8000

timeout /t 3 /nobreak > nul

echo 🎨 Starting Streamlit dashboard...
start /B streamlit run dashboard/finmark_dashboard.py --server.port 8501

timeout /t 2 /nobreak > nul

echo.
echo 🎉 FinMark System is ready!
echo.
echo 📊 Dashboard: http://localhost:8501
echo 🔧 Django Admin: http://localhost:8000/admin
echo 🔌 API: http://localhost:8000/api
echo.
echo 👤 Login credentials:
echo    Admin: admin/admin123
echo    Security: security/security123
echo    Analyst: analyst/analyst123
echo.
pause
