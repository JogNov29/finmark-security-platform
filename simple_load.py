#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Super simple data loading that matches the exact model fields
"""

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

def simple_data_load():
    """Load data with only the fields that exist in models"""
    print("Ì∫Ä Loading data with correct model fields...")
    print("=" * 50)
    
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
        print("‚úÖ Created admin user: admin / admin123")
    
    # Clear old data
    print("Ì∑π Clearing old data...")
    SecurityEvent.objects.all().delete()
    SystemMetrics.objects.all().delete()
    UserActivity.objects.all().delete()
    
    # Load network devices from CSV
    print("Ì≥° Loading network devices...")
    try:
        df = pd.read_csv('network_inventory.csv')
        
        for _, row in df.iterrows():
            device_type = 'server'
            role = str(row.get('Role', '')).lower()
            
            if 'router' in role:
                device_type = 'router'
            elif 'printer' in role:
                device_type = 'printer'
            else:
                device_type = 'server'
            
            # Check notes for status
            notes = str(row.get('Notes', '')).lower()
            status = 'critical' if ('no antivirus' in notes or 'outdated' in notes or 'no firewall' in notes) else 'active'
            
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
        
        device_count = Device.objects.count()
        print(f"‚úÖ Loaded {device_count} network devices from CSV")
        
    except Exception as e:
        print(f"‚ö†Ô∏è Could not load network_inventory.csv: {e}")
        device_count = 0
    
    # Load security events from CSV
    print("Ì¥í Loading security events...")
    events_created = 0
    
    try:
        # Try both filenames
        for filename in ['event_logs.csv', 'event_logs .csv']:
            try:
                df = pd.read_csv(filename)
                print(f"‚úÖ Successfully read {filename}")
                
                # Process first 50 events
                for _, row in df.head(50).iterrows():
                    event_type = str(row.get('event_type', 'unknown')).lower()
                    
                    # Map to security event types
                    if 'login' in event_type:
                        sec_type = 'login_failure'
                        severity = 'critical'
                        is_threat = True
                    elif 'checkout' in event_type:
                        sec_type = 'suspicious_traffic'
                        severity = 'warning'
                        is_threat = False
                    else:
                        sec_type = 'suspicious_traffic'
                        severity = 'info'
                        is_threat = False
                    
                    # Create with only existing fields
                    SecurityEvent.objects.create(
                        event_type=sec_type,
                        severity=severity,
                        source_ip=f"192.168.1.{random.randint(1, 254)}",
                        details=f"CSV Event: {event_type}",
                        is_threat=is_threat
                    )
                    events_created += 1
                
                break  # Stop after successfully reading one file
                
            except Exception as e:
                print(f"‚ö†Ô∏è Could not read {filename}: {e}")
                continue
                
    except Exception as e:
        print(f"‚ö†Ô∏è Error with CSV loading: {e}")
    
    # Create critical security events for demo
    print("Ì∫® Creating demo security events...")
    
    demo_events = [
        {
            'event_type': 'login_failure',
            'severity': 'critical',
            'source_ip': '203.0.113.1',
            'details': 'Ì∫® CRITICAL: Brute force attack detected - 50+ failed logins',
            'is_threat': True
        },
        {
            'event_type': 'malware_detected',
            'severity': 'critical',
            'source_ip': '10.0.0.102',
            'details': 'Ì∫® CRITICAL: Malware found on PC-Client-02',
            'is_threat': True
        },
        {
            'event_type': 'ddos_attack',
            'severity': 'critical',
            'source_ip': '198.51.100.1',
            'details': 'Ì∫® CRITICAL: DDoS attack in progress',
            'is_threat': True
        }
    ]
    
    for event in demo_events:
        SecurityEvent.objects.create(**event)
        events_created += 1
    
    print(f"‚úÖ Created {events_created} security events")
    
    # Create system metrics (without device field)
    print("Ì≥ä Generating system metrics...")
    
    now = datetime.now()
    metrics_created = 0
    
    # Generate 24 hours of metrics
    for hours_ago in range(24):
        timestamp = now - timedelta(hours=hours_ago)
        
        # Create realistic metrics
        cpu_usage = random.uniform(20, 90)
        memory_usage = random.uniform(30, 85)
        response_time = random.randint(100, 1000)
        
        # Create with only the fields that exist
        SystemMetrics.objects.create(
            timestamp=timestamp,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=response_time
        )
        metrics_created += 1
    
    print(f"‚úÖ Generated {metrics_created} system metrics")
    
    # Create sample products
    print("ÌªçÔ∏è Creating products...")
    
    products = [
        {'name': 'FinMark Security Pro', 'price': 299.99},
        {'name': 'Analytics Dashboard', 'price': 199.99},
        {'name': 'Network Monitor', 'price': 149.99},
    ]
    
    for product_data in products:
        Product.objects.get_or_create(
            name=product_data['name'],
            defaults={'price': product_data['price']}
        )
    
    print("‚úÖ Created sample products")
    
    # Create user activities
    print("Ì±§ Creating user activities...")
    
    activities = ['login', 'page_view', 'checkout']
    
    for i in range(100):
        timestamp = now - timedelta(hours=random.randint(0, 24))
        
        UserActivity.objects.create(
            user=user,
            event_type=random.choice(activities),
            timestamp=timestamp,
            ip_address=f"192.168.1.{random.randint(1, 254)}",
            details={'session': f"session_{i}"}
        )
    
    print("‚úÖ Created 100 user activities")
    
    # Final summary
    print("\n" + "=" * 50)
    print("‚úÖ DATA LOADING SUCCESSFUL!")
    print("Ì≥ä Your database now has:")
    
    device_count = Device.objects.count()
    event_count = SecurityEvent.objects.count()
    metric_count = SystemMetrics.objects.count()
    product_count = Product.objects.count()
    activity_count = UserActivity.objects.count()
    
    print(f"   ‚Ä¢ {device_count} network devices")
    print(f"   ‚Ä¢ {event_count} security events")
    print(f"   ‚Ä¢ {metric_count} system metrics")
    print(f"   ‚Ä¢ {product_count} products")
    print(f"   ‚Ä¢ {activity_count} user activities")
    
    # Show critical stats
    critical_count = SecurityEvent.objects.filter(severity='critical').count()
    threat_count = SecurityEvent.objects.filter(is_threat=True).count()
    critical_devices = Device.objects.filter(status='critical').count()
    
    print(f"\nÌ∫® SECURITY DASHBOARD WILL SHOW:")
    print(f"   ‚Ä¢ {critical_count} Critical Alerts")
    print(f"   ‚Ä¢ {threat_count} Active Threats") 
    print(f"   ‚Ä¢ {device_count} Total Devices")
    print(f"   ‚Ä¢ {critical_devices} Devices Need Attention")
    
    print("\nÌºê Network Devices:")
    for device in Device.objects.all():
        status_icon = "Ì¥¥" if device.status == 'critical' else "ÔøΩÔøΩ"
        print(f"   {status_icon} {device.hostname} - {device.status}")
    
    print("\nÌ¥í Critical Security Events:")
    for event in SecurityEvent.objects.filter(severity='critical'):
        print(f"   Ì∫® {event.event_type} from {event.source_ip}")
    
    print("\nÌæØ PERFECT! Now restart your system:")
    print("   ./run.sh")
    print("\nÌºê Then visit: http://localhost:8501")
    print("Ì¥ê Login: admin / admin123")

if __name__ == '__main__':
    simple_data_load()
