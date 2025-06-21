#!/usr/bin/env python3

import os
import sys
import django
import pandas as pd
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.security.models import Device, SecurityEvent
from apps.analytics.models import UserActivity, SystemMetrics
from apps.core.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

def load_data():
    print("Loading data into FinMark database...")
    
    # Create admin user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@finmark.local',
            'is_staff': True,
            'is_superuser': True,
            'role': 'admin'
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print("Created admin user: admin / admin123")
    
    # Clear old data
    SecurityEvent.objects.all().delete()
    SystemMetrics.objects.all().delete()
    UserActivity.objects.all().delete()
    
    # Load network devices
    try:
        df = pd.read_csv('network_inventory.csv')
        
        for _, row in df.iterrows():
            device_type = 'server'
            role = str(row.get('Role', '')).lower()
            
            if 'router' in role:
                device_type = 'router'
            elif 'printer' in role:
                device_type = 'printer'
            
            notes = str(row.get('Notes', '')).lower()
            status = 'critical' if ('no antivirus' in notes or 'outdated' in notes) else 'active'
            
            Device.objects.get_or_create(
                hostname=row['Device'],
                defaults={
                    'ip_address': row['IP_Address'],
                    'device_type': device_type,
                    'status': status,
                    'os': str(row.get('OS', '')),
                    'notes': str(row.get('Notes', ''))
                }
            )
        
        print(f"Loaded {Device.objects.count()} devices")
        
    except Exception as e:
        print(f"Could not load devices: {e}")
    
    # Load security events from CSV
    events_created = 0
    
    try:
        for filename in ['event_logs.csv', 'event_logs .csv']:
            try:
                df = pd.read_csv(filename)
                print(f"Reading {filename}")
                
                for _, row in df.head(50).iterrows():
                    event_type = str(row.get('event_type', 'unknown')).lower()
                    
                    if 'login' in event_type:
                        sec_type = 'login_failure'
                        severity = 'critical'
                        is_threat = True
                    else:
                        sec_type = 'suspicious_traffic'
                        severity = 'info'
                        is_threat = False
                    
                    SecurityEvent.objects.create(
                        event_type=sec_type,
                        severity=severity,
                        source_ip=f"192.168.1.{random.randint(1, 254)}",
                        details=f"CSV: {event_type}",
                        is_threat=is_threat
                    )
                    events_created += 1
                
                break
                
            except:
                continue
                
    except:
        pass
    
    # Create demo events
    demo_events = [
        {
            'event_type': 'login_failure',
            'severity': 'critical',
            'source_ip': '203.0.113.1',
            'details': 'Multiple failed login attempts',
            'is_threat': True
        },
        {
            'event_type': 'malware_detected',
            'severity': 'critical',
            'source_ip': '10.0.0.102',
            'details': 'Malware detected on PC-Client-02',
            'is_threat': True
        }
    ]
    
    for event in demo_events:
        SecurityEvent.objects.create(**event)
        events_created += 1
    
    print(f"Created {events_created} security events")
    
    # Create metrics
    now = datetime.now()
    for hours_ago in range(24):
        timestamp = now - timedelta(hours=hours_ago)
        
        SystemMetrics.objects.create(
            timestamp=timestamp,
            cpu_usage=random.uniform(20, 90),
            memory_usage=random.uniform(30, 85),
            response_time=random.randint(100, 1000)
        )
    
    print("Generated 24 hours of metrics")
    
    # Create products
    products = [
        {'name': 'Security Pro', 'price': 299.99},
        {'name': 'Analytics Dashboard', 'price': 199.99},
    ]
    
    for product_data in products:
        Product.objects.get_or_create(
            name=product_data['name'],
            defaults={'price': product_data['price']}
        )
    
    # Create activities
    activities = ['login', 'page_view', 'checkout']
    
    for i in range(50):
        timestamp = now - timedelta(hours=random.randint(0, 24))
        
        UserActivity.objects.create(
            user=user,
            event_type=random.choice(activities),
            timestamp=timestamp,
            ip_address=f"192.168.1.{random.randint(1, 254)}",
            details={'session': f"session_{i}"}
        )
    
    print("COMPLETE!")
    print(f"Devices: {Device.objects.count()}")
    print(f"Events: {SecurityEvent.objects.count()}")
    print(f"Metrics: {SystemMetrics.objects.count()}")
    
    critical_count = SecurityEvent.objects.filter(severity='critical').count()
    print(f"Critical Alerts: {critical_count}")
    
    print("\nRestart with: ./run.sh")

if __name__ == '__main__':
    load_data()
