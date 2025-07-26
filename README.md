# 🛡️ FinMark Security Operations Center

## Academic Project for MO-IT151 - Platform Technologies

### 📚 Course Information
- **Course:** MO-IT151 - Platform Technologies
- **Project:** Security Analytics Dashboard & API System
- **Purpose:** Academic requirement demonstrating platform technology integration
- **Team:** Caluya, Clemente, Eduria, Hachero, Novillas

---

## 🚀 Project Overview

The FinMark Security Operations Center is a comprehensive security analytics dashboard and API system designed to address FinMark Corporation's critical business challenge of scaling from 500 to 3,000+ daily orders while maintaining robust security monitoring.

### 🎯 Business Problem
FinMark Corporation faces system limitations with:
- Current capacity: **500 orders/day**
- Target capacity: **3,000+ orders/day** (6x growth requirement)
- Frequent system crashes during peak usage
- No real-time security monitoring capabilities
- Reactive incident response approach

### 💡 Solution Architecture
A comprehensive security analytics platform featuring:
- **Real-time threat detection and alerting**
- **Network traffic analysis and monitoring**
- **System health and performance metrics**
- **Security incident management**
- **Comprehensive audit logging**

---

<img width="1920" height="1080" alt="login-homepage" src="https://github.com/user-attachments/assets/3849cc9b-76b5-44e7-96ef-fb18b2c2bbdf" />

<img width="1920" height="1080" alt="dashboard-landing page" src="https://github.com/user-attachments/assets/cbd373fd-f212-4f8b-aafd-6a838f9fb2fd" />

<img width="1920" height="1080" alt="network traffic and alert details" src="https://github.com/user-attachments/assets/25031bad-96e7-420e-a9e9-1626e956d327" />

<img width="1920" height="1080" alt="system status" src="https://github.com/user-attachments/assets/c6f3bafe-47bb-4e63-ba16-f9d47b360c3a" />

---

## 🏗️ Architecture Overview

### System Components
```
┌─────────────────────┐
│   Client Frontend   │  ← Streamlit Dashboard
│ (Postman, PowerBI,  │
│     Grafana)        │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│     API Layer       │  ← Django + Django REST Framework
│  Django + DRF +     │    + JWT Authentication
│    JWT Auth         │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Database Layer     │  ← PostgreSQL
│   (PostgreSQL)      │
└─────────────────────┘
```

### Data Pipeline
- **Current:** 10 logs/day → **Proposed:** 10,000+ events/min
- **Security:** Manual monitoring → **24/7 automated monitoring**
- **APIs:** Internal only → **Complete API ecosystem**
- **Analytics:** Manual reports → **Real-time insights**

---

## 🛠️ Technology Stack

### Backend
- **Framework:** Django 4.2+
- **API:** Django REST Framework
- **Authentication:** JWT (JSON Web Tokens)
- **Database:** PostgreSQL (Production) / SQLite (Development)
- **Security:** CORS middleware, Rate limiting

### Frontend
- **Dashboard:** Streamlit
- **Charts:** Plotly
- **Data Processing:** Pandas, NumPy
- **Styling:** Custom CSS with dark theme

### Integration
- **API Testing:** Postman
- **Business Intelligence:** PowerBI ready
- **Monitoring:** Grafana compatible

---

## 📋 Features

### 🔐 Security Features
- **JWT Authentication** with role-based access control
- **Real-time threat detection** and automated alerting
- **Network traffic monitoring** with anomaly detection
- **Security incident management** and response workflows
- **Comprehensive audit logging** for compliance

### 📊 Analytics & Monitoring
- **Real-time dashboards** with live data updates
- **Interactive charts** for network traffic analysis
- **System health metrics** and performance monitoring
- **Predictive analytics** for demand forecasting
- **Custom reporting** and data exports

### 🚀 Scalability
- **6x capacity increase** (500 to 3,000+ orders/day)
- **High-performance API** with rate limiting (1000 req/min)
- **Scalable architecture** ready for future growth
- **Load balancing** and auto-scaling capabilities

---

## 🔧 Installation & Setup

### Prerequisites
```bash
Python 3.8+
Node.js (for additional tooling)
Git
```

### Backend Setup (Django API)
```bash
# Clone the repository
git clone <repository-url>
cd finmark-security-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Django server
python manage.py runserver
```

### Frontend Setup (Streamlit Dashboard)
```bash
# Navigate to dashboard directory
cd dashboard

# Install Streamlit dependencies
pip install streamlit plotly pandas numpy requests

# Run the dashboard
streamlit run finmark_dashboard.py
```

### Access Points
- **API Server:** http://localhost:8000/api/
- **Dashboard:** http://localhost:8501
- **Admin Panel:** http://localhost:8000/admin/

---

## 🔑 Authentication

### Dashboard Access
- **Username:** `admin`
- **Password:** `admin123`

### API Endpoints
```bash
# Get authentication token
POST /api/auth/token/
{
    "username": "admin",
    "password": "admin123"
}

# Use token in subsequent requests
Authorization: Bearer <your-jwt-token>
```

---

## 📊 API Documentation

### Core Endpoints
```bash
GET  /api/status/          # System status
GET  /api/metrics/         # Security metrics
GET  /api/database/        # Database information
POST /api/auth/token/      # Authentication
GET  /api/events/          # Security events
GET  /api/alerts/          # Security alerts
```

### Example Response
```json
{
    "status": "operational",
    "metrics": {
        "critical_alerts": 3,
        "active_threats": 12,
        "system_health": 98.2,
        "daily_orders": 1847
    },
    "timestamp": "2025-07-27T14:30:00Z"
}
```

---

## 📈 Dashboard Features

### Main Dashboard
- **Real-time metrics** display
- **Network traffic analysis** with interactive charts
- **Security alerts** management
- **System status** monitoring
- **User session** management

### Security Alerts
- 🔴 **Critical:** Multiple failed login attempts
- 🟡 **Warning:** Unusual traffic patterns
- 🟢 **Info:** System updates and maintenance

### Network Traffic Analysis
- **24-hour traffic patterns**
- **Inbound/Outbound data flows**
- **Threat detection** and blocking statistics
- **Peak usage** identification

---

## 🗂️ Project Structure

```
finmark-security-platform/
├── dashboard/
│   ├── finmark_dashboard.py     # Main Streamlit dashboard
│   └── requirements.txt         # Dashboard dependencies
├── backend/
│   ├── finmark_api/            # Django project
│   ├── security/               # Security app
│   ├── analytics/              # Analytics app
│   └── requirements.txt        # Backend dependencies
├── docs/
│   ├── architecture/           # Architecture diagrams
│   ├── api/                   # API documentation
│   └── deployment/            # Deployment guides
├── data/
│   ├── sample_data/           # Sample datasets
│   └── mock_data/             # Mock data for testing
└── README.md                  # This file
```

---

## 📋 Academic Requirements Fulfilled

### Platform Technologies Demonstrated
1. **Web Application Framework** - Django with REST API
2. **Database Integration** - PostgreSQL with ORM
3. **Authentication & Security** - JWT implementation
4. **Frontend Integration** - Streamlit dashboard
5. **Data Visualization** - Plotly charts and analytics
6. **API Development** - RESTful services
7. **Real-time Processing** - Live data updates

### Technical Concepts Covered
- **MVC Architecture** pattern implementation
- **Database design** and normalization
- **API design** and documentation
- **Security best practices**
- **Data pipeline** architecture
- **Real-time analytics**
- **Scalable system design**

---

## 🎓 Learning Outcomes

### Skills Developed
- **Full-stack development** with Django and Streamlit
- **API design** and RESTful services
- **Database modeling** and optimization
- **Security implementation** with JWT
- **Data visualization** and analytics
- **System architecture** design
- **Documentation** and project management

### Platform Technologies Mastered
- **Backend Frameworks:** Django, Django REST Framework
- **Frontend Technologies:** Streamlit, HTML/CSS
- **Database Systems:** PostgreSQL, SQLite
- **Authentication:** JWT tokens
- **Data Processing:** Pandas, NumPy
- **Visualization:** Plotly, Charts
- **Development Tools:** Git, Postman, VS Code


## 📄 License

This project is developed for academic purposes as part of MO-IT151 - Platform Technologies course requirements.

---

**© 2025 FinMark Security Operations Center - Academic Project**  
**MO-IT151 - Platform Technologies**
