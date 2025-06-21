#!/usr/bin/env python3
import os
import sys
import django
import pandas as pd

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.security.models import Device, SecurityEvent
from django.contrib.auth import get_user_model

User = get_user_model()

def load_data():
    print("Ì¥Ñ Loading your CSV data...")
    
    # Create admin user
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@finmark.local', 'is_staff': True, 'is_superuser': True}
    )
    if created:
        user.set_password('admin123')
        user.save()
        print("‚úÖ Created admin user: admin / admin123")
    
    # Load network devices
    try:
        df = pd.read_csv('network_inventory.csv')
        for _, row in df.iterrows():
            device_type = 'server'
            if 'Router' in str(row.get('Role', '')):
                device_type = 'router'
            elif 'Printer' in str(row.get('Role', '')):
                device_type = 'printer'
                
            Device.objects.get_or_create(
                hostname=row['Device'],
                defaults={
                    'ip_address': row['IP_Address'],
                    'device_type': device_type,
                    'os': str(row.get('OS', '')),
                    'notes': str(row.get('Notes', ''))
                }
            )
        print(f"‚úÖ Loaded {len(df)} devices from network_inventory.csv")
    except Exception as e:
        print(f"‚ö†Ô∏è Could not load network_inventory.csv: {e}")
    
    # Load security events from event logs
    try:
        # Note: your file has a space in the name
        df = pd.read_csv('event_logs .csv')
        count = 0
        for _, row in df.iterrows():
            event_type = str(row.get('event_type', 'unknown'))
            if 'login' in event_type.lower():
                event_type = 'login_failure'
            elif 'checkout' in event_type.lower():
                event_type = 'suspicious_traffic'
            else:
                event_type = 'user_activity'
                
            SecurityEvent.objects.create(
                event_type=event_type,
                severity='info' if event_type == 'user_activity' else 'warning',
                source_ip='192.168.1.100',
                details=f"Event from CSV: {row.get('event_type', 'unknown')}"
            )
            count += 1
            if count >= 100:  # Limit to first 100 for demo
                break
                
        print(f"‚úÖ Loaded {count} security events from event_logs.csv")
    except Exception as e:
        print(f"‚ö†Ô∏è Could not load event_logs.csv: {e}")
    
    print("‚úÖ Data loading completed!")
    print("Ìºê Your CSV files are now loaded into the system!")

if __name__ == '__main__':
    load_data()
