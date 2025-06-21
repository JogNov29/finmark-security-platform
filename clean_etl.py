#!/usr/bin/env python3

import os
import sys
import django
import pandas as pd
from datetime import datetime, timedelta
import random
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.security.models import Device, SecurityEvent
from apps.analytics.models import UserActivity, SystemMetrics
from apps.core.models import Product
from django.contrib.auth import get_user_model

def run_etl():
    print("FinMark ETL Pipeline Starting...")
    print("=" * 50)
    
    User = get_user_model()
    
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
    
    # Clear existing data
    print("Clearing existing data...")
    SecurityEvent.objects.all().delete()
    SystemMetrics.objects.all().delete()
    UserActivity.objects.all().delete()
    
    # PHASE 1: EXTRACT DATA
    print("\nPHASE 1: EXTRACTING DATA")
    print("-" * 30)
    
    devices_loaded = 0
    events_loaded = 0
    metrics_loaded = 0
    
    # Extract network devices
    try:
        df = pd.read_csv('network_inventory.csv')
        print(f"Extracted network devices: {len(df)} records")
        
        for _, row in df.iterrows():
            device_name = str(row.get('Device', '')).strip()
            ip_address = str(row.get('IP_Address', '')).strip()
            role = str(row.get('Role', '')).lower()
            notes = str(row.get('Notes', '')).lower()
            
            # Determine device type
            if 'router' in role:
                device_type = 'router'
            elif 'server' in role:
                device_type = 'server'
            elif 'printer' in role:
                device_type = 'printer'
            else:
                device_type = 'workstation'
            
            # Determine status
            if 'no antivirus' in notes or 'outdated' in notes:
                status = 'critical'
            else:
                status = 'active'
            
            Device.objects.get_or_create(
                hostname=device_name,
                defaults={
                    'ip_address': ip_address,
                    'device_type': device_type,
                    'status': status,
                    'os': str(row.get('OS', '')),
                    'notes': str(row.get('Notes', ''))
                }
            )
            devices_loaded += 1
            
    except Exception as e:
        print(f"Could not load devices: {e}")
    
    # Extract and transform events
    try:
        for filename in ['event_logs.csv', 'event_logs .csv']:
            try:
                df = pd.read_csv(filename)
                print(f"Extracted events from {filename}: {len(df)} records")
                
                # Process first 50 events
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
                        details=f"CSV Event: {event_type}",
                        is_threat=is_threat
                    )
                    events_loaded += 1
                
                break
                
            except:
                continue
                
    except Exception as e:
        print(f"Could not load events: {e}")
    
    # Create demo critical events
    print("\nPHASE 2: CREATING SECURITY EVENTS")
    print("-" * 30)
    
    critical_events = [
        {
            'event_type': 'login_failure',
            'severity': 'critical',
            'source_ip': '203.0.113.1',
            'details': 'Multiple failed login attempts detected',
            'is_threat': True
        },
        {
            'event_type': 'malware_detected',
            'severity': 'critical',
            'source_ip': '10.0.0.102',
            'details': 'Malware detected on PC-Client-02',
            'is_threat': True
        },
        {
            'event_type': 'ddos_attack',
            'severity': 'critical',
            'source_ip': '198.51.100.1',
            'details': 'DDoS attack in progress',
            'is_threat': True
        }
    ]
    
    for event in critical_events:
        SecurityEvent.objects.create(**event)
        events_loaded += 1
    
    # Generate system metrics
    print("\nPHASE 3: GENERATING METRICS")
    print("-" * 30)
    
    now = datetime.now()
    
    for hours_ago in range(24):
        timestamp = now - timedelta(hours=hours_ago)
        
        SystemMetrics.objects.create(
            timestamp=timestamp,
            cpu_usage=random.uniform(20, 90),
            memory_usage=random.uniform(30, 85),
            response_time=random.randint(100, 1000)
        )
        metrics_loaded += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("ETL PIPELINE COMPLETED!")
    print(f"Devices loaded: {devices_loaded}")
    print(f"Events loaded: {events_loaded}")
    print(f"Metrics loaded: {metrics_loaded}")
    
    # Database stats
    print(f"\nDatabase Summary:")
    print(f"  Total Devices: {Device.objects.count()}")
    print(f"  Total Events: {SecurityEvent.objects.count()}")
    print(f"  Total Metrics: {SystemMetrics.objects.count()}")
    
    critical_count = SecurityEvent.objects.filter(severity='critical').count()
    threat_count = SecurityEvent.objects.filter(is_threat=True).count()
    
    print(f"\nSecurity Stats:")
    print(f"  Critical Alerts: {critical_count}")
    print(f"  Active Threats: {threat_count}")
    
    # Save report
    report = {
        'status': 'SUCCESS',
        'timestamp': datetime.now().isoformat(),
        'devices': devices_loaded,
        'events': events_loaded,
        'metrics': metrics_loaded
    }
    
    with open('etl_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\nETL report saved: etl_report.json")
    print("SUCCESS! Start dashboard with: ./run.sh")

if __name__ == '__main__':
    run_etl()
