#!/usr/bin/env python3
"""
FinMark Database Setup & Data Loading Script
Loads your CSV data into SQLite database with proper date handling
"""

import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.security.models import Device, SecurityEvent
from apps.analytics.models import UserActivity, SystemMetrics
from apps.core.models import Product
from django.contrib.auth import get_user_model

def setup_database():
    """Setup database with your CSV data"""
    print("🚀 FinMark Database Setup Starting...")
    print("=" * 50)
    
    User = get_user_model()
    
    # Create admin user if not exists
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@finmark.local',
            'is_staff': True,
            'is_superuser': True,
            'role': 'admin'
        }
    )
    
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Created admin user: admin / admin123")
    
    # Create additional users for testing
    users_data = [
        {'username': 'security', 'password': 'security123', 'role': 'security', 'email': 'security@finmark.com'},
        {'username': 'analyst', 'password': 'analyst123', 'role': 'analyst', 'email': 'analyst@finmark.com'}
    ]
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'role': user_data['role'],
                'is_staff': True
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✅ Created {user_data['role']} user: {user_data['username']} / {user_data['password']}")
    
    # Clear existing data
    print("\n🧹 Clearing existing data...")
    SecurityEvent.objects.all().delete()
    SystemMetrics.objects.all().delete()
    UserActivity.objects.all().delete()
    Device.objects.all().delete()
    
    # Load network inventory
    print("\n📡 Loading network inventory...")
    load_network_inventory()
    
    # Load event logs
    print("\n🔒 Loading security events...")
    load_security_events()
    
    # Load system metrics
    print("\n📊 Loading system metrics...")
    load_system_metrics()
    
    # Load marketing data as user activities
    print("\n👥 Loading user activities...")
    load_user_activities(admin_user)
    
    print("\n✅ Database setup complete!")
    print_summary()

def load_network_inventory():
    """Load network devices from CSV"""
    try:
        df = pd.read_csv('network_inventory.csv')
        print(f"Found {len(df)} devices in network_inventory.csv")
        
        for _, row in df.iterrows():
            device_name = str(row.get('Device', 'Unknown')).strip()
            ip_address = str(row.get('IP_Address', '127.0.0.1')).strip()
            role = str(row.get('Role', 'unknown')).lower()
            os_info = str(row.get('OS', 'Unknown')).strip()
            notes = str(row.get('Notes', '')).strip()
            
            # Determine device type
            if 'router' in role:
                device_type = 'router'
            elif 'server' in role:
                device_type = 'server'
            elif 'printer' in role:
                device_type = 'printer'
            else:
                device_type = 'workstation'
            
            # Determine status from notes
            notes_lower = notes.lower()
            if any(keyword in notes_lower for keyword in ['no antivirus', 'outdated', 'no firewall']):
                status = 'critical'
            elif any(keyword in notes_lower for keyword in ['ssl', 'tls', 'update']):
                status = 'warning'
            else:
                status = 'active'
            
            Device.objects.create(
                hostname=device_name,
                ip_address=ip_address,
                device_type=device_type,
                os=os_info,
                status=status,
                notes=notes
            )
        
        print(f"✅ Loaded {Device.objects.count()} devices")
        
    except FileNotFoundError:
        print("⚠️ network_inventory.csv not found, creating sample devices")
        create_sample_devices()
    except Exception as e:
        print(f"❌ Error loading devices: {e}")
        create_sample_devices()

def create_sample_devices():
    """Create sample devices if CSV not found"""
    sample_devices = [
        {'hostname': 'Router1', 'ip_address': '10.0.0.1', 'device_type': 'router', 'os': 'Cisco IOS', 'status': 'critical', 'notes': 'Default password in use'},
        {'hostname': 'WebServer1', 'ip_address': '10.0.0.20', 'device_type': 'server', 'os': 'Ubuntu 18.04', 'status': 'warning', 'notes': 'Outdated SSL/TLS'},
        {'hostname': 'DBServer1', 'ip_address': '10.0.0.30', 'device_type': 'server', 'os': 'Windows 2012', 'status': 'critical', 'notes': 'No firewall'},
        {'hostname': 'PC-Client-01', 'ip_address': '10.0.0.101', 'device_type': 'workstation', 'os': 'Win 10 Pro', 'status': 'active', 'notes': ''},
        {'hostname': 'PC-Client-02', 'ip_address': '10.0.0.102', 'device_type': 'workstation', 'os': 'Win 10 Home', 'status': 'critical', 'notes': 'Outdated OS; no antivirus'},
        {'hostname': 'Printer-01', 'ip_address': '10.0.0.150', 'device_type': 'printer', 'os': '', 'status': 'warning', 'notes': 'Unsecured printing, no password'}
    ]
    
    for device_data in sample_devices:
        Device.objects.create(**device_data)
    
    print(f"✅ Created {len(sample_devices)} sample devices")

def load_security_events():
    """Load security events from CSV with date conversion"""
    events_created = 0
    
    # Try to load from event_logs.csv
    for filename in ['event_logs.csv', 'event_logs .csv']:
        try:
            df = pd.read_csv(filename)
            print(f"Found {len(df)} events in {filename}")
            
            # Process events in batches
            batch_size = 100
            for i in range(0, min(len(df), 500), batch_size):  # Limit to 500 events
                batch = df.iloc[i:i+batch_size]
                
                for _, row in batch.iterrows():
                    event_type = str(row.get('event_type', 'unknown')).lower()
                    user_id = str(row.get('user_id', ''))
                    product_id = str(row.get('product_id', ''))
                    amount = row.get('amount', 0)
                    
                    # Convert old dates to recent dates for better dashboard experience
                    base_time = datetime.now()
                    hours_ago = random.randint(0, 72)  # Last 3 days
                    event_time = base_time - timedelta(hours=hours_ago)
                    
                    # Categorize events
                    if 'login' in event_type:
                        sec_event_type = 'login_failure'
                        severity = 'critical'
                        is_threat = True
                    elif 'checkout' in event_type:
                        sec_event_type = 'transaction'
                        severity = 'info'
                        is_threat = False
                    elif 'wishlist' in event_type:
                        sec_event_type = 'suspicious_activity'
                        severity = 'warning'
                        is_threat = True
                    else:
                        sec_event_type = 'user_activity'
                        severity = 'info'
                        is_threat = False
                    
                    # Generate IP address
                    if is_threat:
                        source_ip = f"203.0.113.{random.randint(1, 254)}"
                    else:
                        source_ip = f"192.168.1.{random.randint(1, 254)}"
                    
                    # Create event details
                    details = f"Event: {event_type}"
                    if user_id:
                        details += f" | User: {user_id}"
                    if product_id:
                        details += f" | Product: {product_id}"
                    if amount and amount > 0:
                        details += f" | Amount: ${amount:.2f}"
                    
                    SecurityEvent.objects.create(
                        event_type=sec_event_type,
                        severity=severity,
                        source_ip=source_ip,
                        details=details,
                        is_threat=is_threat,
                        timestamp=event_time
                    )
                    events_created += 1
            
            break  # Success, exit loop
            
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            continue
    
    # Add some recent critical events
    critical_events = [
        {
            'event_type': 'login_failure',
            'severity': 'critical',
            'source_ip': '203.0.113.15',
            'details': 'Multiple failed login attempts detected (50+ attempts)',
            'is_threat': True,
            'timestamp': datetime.now() - timedelta(minutes=15)
        },
        {
            'event_type': 'malware_detected',
            'severity': 'critical',
            'source_ip': '10.0.0.102',
            'details': 'Malware signature detected on PC-Client-02',
            'is_threat': True,
            'timestamp': datetime.now() - timedelta(hours=2)
        },
        {
            'event_type': 'ddos_attack',
            'severity': 'critical',
            'source_ip': '198.51.100.1',
            'details': 'DDoS attack detected from external sources',
            'is_threat': True,
            'timestamp': datetime.now() - timedelta(hours=6)
        },
        {
            'event_type': 'unauthorized_access',
            'severity': 'warning',
            'source_ip': '192.168.1.45',
            'details': 'Unauthorized admin panel access attempt',
            'is_threat': True,
            'timestamp': datetime.now() - timedelta(minutes=45)
        }
    ]
    
    for event_data in critical_events:
        SecurityEvent.objects.create(**event_data)
        events_created += 1
    
    print(f"✅ Created {events_created} security events")

def load_system_metrics():
    """Load system metrics with recent dates"""
    now = datetime.now()
    metrics_created = 0
    
    # Generate metrics for last 7 days
    for days_ago in range(7):
        for hour in range(0, 24, 2):  # Every 2 hours
            timestamp = now - timedelta(days=days_ago, hours=hour)
            
            # Simulate realistic patterns
            is_business_hours = 8 <= hour <= 18
            is_weekday = timestamp.weekday() < 5
            
            base_cpu = 70 if (is_business_hours and is_weekday) else 30
            base_memory = 65 if (is_business_hours and is_weekday) else 40
            base_response = 150 if (is_business_hours and is_weekday) else 80
            
            # Add variance
            cpu_usage = max(10, min(95, base_cpu + random.gauss(0, 15)))
            memory_usage = max(20, min(90, base_memory + random.gauss(0, 12)))
            response_time = max(50, int(base_response + random.gauss(0, 40)))
            
            SystemMetrics.objects.create(
                timestamp=timestamp,
                cpu_usage=round(cpu_usage, 2),
                memory_usage=round(memory_usage, 2),
                response_time=response_time
            )
            metrics_created += 1
    
    print(f"✅ Created {metrics_created} system metrics")

def load_user_activities(admin_user):
    """Load user activities from marketing data"""
    try:
        df = pd.read_csv('marketing_summary.csv')
        print(f"Found {len(df)} records in marketing_summary.csv")
        
        activities_created = 0
        now = datetime.now()
        
        for i, row in df.head(50).iterrows():  # Limit to 50 records
            # Convert to recent dates
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            activity_time = now - timedelta(days=days_ago, hours=hours_ago)
            
            # Get data from CSV
            users_active = row.get('users_active', 0)
            total_sales = row.get('total_sales', 0)
            new_customers = row.get('new_customers', 0)
            
            # Create activity based on data
            event_types = ['page_view', 'login', 'logout', 'search', 'checkout']
            event_type = random.choice(event_types)
            
            UserActivity.objects.create(
                user=admin_user,
                event_type=event_type,
                timestamp=activity_time,
                ip_address=f"192.168.1.{random.randint(1, 254)}",
                details={
                    'daily_users': users_active,
                    'sales': float(total_sales) if total_sales else 0,
                    'new_customers': new_customers,
                    'session_id': f"session_{i}"
                }
            )
            activities_created += 1
        
        print(f"✅ Created {activities_created} user activities")
        
    except FileNotFoundError:
        print("⚠️ marketing_summary.csv not found, creating sample activities")
        
        # Create sample activities
        for i in range(20):
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            activity_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            UserActivity.objects.create(
                user=admin_user,
                event_type=random.choice(['page_view', 'login', 'search', 'checkout']),
                timestamp=activity_time,
                ip_address=f"192.168.1.{random.randint(1, 254)}",
                details={'session_id': f"session_{i}"}
            )
        
        print("✅ Created 20 sample user activities")

def print_summary():
    """Print database summary"""
    print("\n📊 DATABASE SUMMARY")
    print("-" * 30)
    print(f"👥 Users: {User.objects.count()}")
    print(f"🖥️ Devices: {Device.objects.count()}")
    print(f"🔒 Security Events: {SecurityEvent.objects.count()}")
    print(f"📈 System Metrics: {SystemMetrics.objects.count()}")
    print(f"👤 User Activities: {UserActivity.objects.count()}")
    
    # Security stats
    critical_events = SecurityEvent.objects.filter(severity='critical').count()
    threats = SecurityEvent.objects.filter(is_threat=True).count()
    critical_devices = Device.objects.filter(status='critical').count()
    
    print(f"\n🚨 SECURITY STATS")
    print(f"Critical Events: {critical_events}")
    print(f"Active Threats: {threats}")
    print(f"Critical Devices: {critical_devices}")
    
    # Recent events
    recent_events = SecurityEvent.objects.filter(
        timestamp__gte=datetime.now() - timedelta(hours=24)
    ).count()
    print(f"Events (24h): {recent_events}")
    
    print(f"\n✅ Database ready! Start dashboard with:")
    print(f"   python manage.py runserver &")
    print(f"   streamlit run dashboard/finmark_dashboard.py")

if __name__ == '__main__':
    setup_database()