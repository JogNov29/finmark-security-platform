#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FinMark ETL Pipeline - Data Extraction, Transformation, and Loading
=====================================================================

This script demonstrates the complete ETL process for FinMark's data pipeline,
including data cleaning, validation, transformation, and loading into the database.

Author: FinMark Data Team
Date: June 2025
Version: 1.0
"""

import os
import sys
import django
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import logging
from typing import Dict, List, Tuple
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.security.models import Device, SecurityEvent
from apps.analytics.models import UserActivity, SystemMetrics
from apps.core.models import Product
from django.contrib.auth import get_user_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class FinMarkETLPipeline:
    """
    FinMark ETL Pipeline for processing security and business data
    
    This class handles the complete ETL process:
    1. Extract: Read data from CSV files and external sources
    2. Transform: Clean, validate, and process data
    3. Load: Insert processed data into Django models/database
    """
    
    def __init__(self):
        self.User = get_user_model()
        self.processed_records = {
            'devices': 0,
            'security_events': 0,
            'user_activities': 0,
            'system_metrics': 0,
            'products': 0
        }
        self.errors = []
        
        logger.info("FinMark ETL Pipeline initialized")
    
    # ==================== EXTRACTION PHASE ====================
    
    def extract_network_inventory(self) -> pd.DataFrame:
        """
        Extract network device data from CSV file
        
        Returns:
            pd.DataFrame: Raw network inventory data
        """
        logger.info("Phase 1: EXTRACTING network inventory data...")
        
        try:
            # Try multiple encodings for robust file reading
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv('network_inventory.csv', encoding=encoding)
                    logger.info(f"✅ Successfully extracted network_inventory.csv with {encoding} encoding")
                    logger.info(f"��� Raw data shape: {df.shape}")
                    return df
                except UnicodeDecodeError:
                    continue
            
            raise FileNotFoundError("Could not read network_inventory.csv with any encoding")
            
        except Exception as e:
            logger.error(f"❌ Failed to extract network inventory: {e}")
            self.errors.append(f"Network inventory extraction: {e}")
            return pd.DataFrame()
    
    def extract_event_logs(self) -> pd.DataFrame:
        """
        Extract user activity/event data from CSV file
        
        Returns:
            pd.DataFrame: Raw event logs data
        """
        logger.info("Phase 1: EXTRACTING event logs data...")
        
        # Try multiple possible filenames
        filenames = ['event_logs.csv', 'event_logs .csv']
        
        for filename in filenames:
            try:
                # Try multiple encodings
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(filename, encoding=encoding)
                        logger.info(f"✅ Successfully extracted {filename} with {encoding} encoding")
                        logger.info(f"��� Raw data shape: {df.shape}")
                        return df
                    except UnicodeDecodeError:
                        continue
            except FileNotFoundError:
                continue
        
        logger.error("❌ Failed to extract event logs from any file")
        self.errors.append("Event logs extraction: No valid file found")
        return pd.DataFrame()
    
    def extract_marketing_data(self) -> pd.DataFrame:
        """
        Extract marketing/sales data from CSV file
        
        Returns:
            pd.DataFrame: Raw marketing data
        """
        logger.info("Phase 1: EXTRACTING marketing data...")
        
        try:
            df = pd.read_csv('marketing_summary.csv')
            logger.info(f"✅ Successfully extracted marketing_summary.csv")
            logger.info(f"��� Raw data shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"❌ Failed to extract marketing data: {e}")
            self.errors.append(f"Marketing data extraction: {e}")
            return pd.DataFrame()
    
    # ==================== TRANSFORMATION PHASE ====================
    
    def clean_network_inventory(self, df: pd.DataFrame) -> List[Dict]:
        """
        Transform and clean network inventory data
        
        Args:
            df: Raw network inventory DataFrame
            
        Returns:
            List[Dict]: Cleaned device records
        """
        logger.info("Phase 2: TRANSFORMING network inventory data...")
        
        if df.empty:
            return []
        
        cleaned_devices = []
        
        for index, row in df.iterrows():
            try:
                # Data cleaning and validation
                device_name = str(row.get('Device', '')).strip()
                ip_address = str(row.get('IP_Address', '')).strip()
                role = str(row.get('Role', '')).strip()
                os_info = str(row.get('OS', '')).strip()
                notes = str(row.get('Notes', '')).strip()
                
                # Validate IP address format
                if not self._validate_ip_address(ip_address):
                    logger.warning(f"⚠️ Invalid IP address for device {device_name}: {ip_address}")
                    continue
                
                # Determine device type from role
                device_type = self._categorize_device_type(role)
                
                # Determine device status from notes
                status = self._determine_device_status(notes)
                
                # Create cleaned record
                cleaned_device = {
                    'hostname': device_name,
                    'ip_address': ip_address,
                    'device_type': device_type,
                    'os': os_info,
                    'status': status,
                    'notes': notes
                }
                
                cleaned_devices.append(cleaned_device)
                logger.debug(f"✅ Cleaned device: {device_name} ({ip_address})")
                
            except Exception as e:
                logger.error(f"❌ Error cleaning device record {index}: {e}")
                self.errors.append(f"Device cleaning error at row {index}: {e}")
                continue
        
        logger.info(f"✅ Network inventory transformation complete: {len(cleaned_devices)} valid records")
        return cleaned_devices
    
    def clean_event_logs(self, df: pd.DataFrame) -> List[Dict]:
        """
        Transform and clean event logs data
        
        Args:
            df: Raw event logs DataFrame
            
        Returns:
            List[Dict]: Cleaned security event records
        """
        logger.info("Phase 2: TRANSFORMING event logs data...")
        
        if df.empty:
            return []
        
        cleaned_events = []
        
        # Process only a reasonable number of events for demo
        sample_size = min(100, len(df))
        df_sample = df.head(sample_size)
        
        for index, row in df_sample.iterrows():
            try:
                event_type = str(row.get('event_type', 'unknown')).lower().strip()
                user_id = str(row.get('user_id', 'unknown')).strip()
                timestamp_str = str(row.get('event_time', ''))
                product_id = str(row.get('product_id', ''))
                amount = row.get('amount', 0)
                
                # Clean and categorize event type
                security_event_type, severity, is_threat = self._categorize_security_event(event_type)
                
                # Generate realistic source IP
                source_ip = self._generate_source_ip(event_type)
                
                # Create event details
                details = self._create_event_details(event_type, user_id, product_id, amount)
                
                cleaned_event = {
                    'event_type': security_event_type,
                    'severity': severity,
                    'source_ip': source_ip,
                    'details': details,
                    'is_threat': is_threat
                }
                
                cleaned_events.append(cleaned_event)
                
            except Exception as e:
                logger.error(f"❌ Error cleaning event record {index}: {e}")
                continue
        
        logger.info(f"✅ Event logs transformation complete: {len(cleaned_events)} security events")
        return cleaned_events
    
    def generate_system_metrics(self, devices: List[Dict]) -> List[Dict]:
        """
        Generate realistic system metrics for devices
        
        Args:
            devices: List of device records
            
        Returns:
            List[Dict]: System metrics records
        """
        logger.info("Phase 2: GENERATING system metrics data...")
        
        metrics = []
        now = datetime.now()
        
        # Generate 24 hours of metrics
        for hours_ago in range(24):
            timestamp = now - timedelta(hours=hours_ago)
            
            # Create metrics based on time of day and device status
            hour_of_day = timestamp.hour
            is_business_hours = 8 <= hour_of_day <= 18
            
            # Business hours have higher activity
            base_cpu = 60 if is_business_hours else 30
            base_memory = 70 if is_business_hours else 40
            base_response = 200 if is_business_hours else 100
            
            # Add some realistic variance
            cpu_usage = max(10, min(95, base_cpu + np.random.normal(0, 15)))
            memory_usage = max(20, min(90, base_memory + np.random.normal(0, 10)))
            response_time = max(50, int(base_response + np.random.normal(0, 50)))
            
            metric = {
                'timestamp': timestamp,
                'cpu_usage': round(cpu_usage, 2),
                'memory_usage': round(memory_usage, 2),
                'response_time': response_time
            }
            
            metrics.append(metric)
        
        logger.info(f"✅ Generated {len(metrics)} system metrics records")
        return metrics
    
    # ==================== LOADING PHASE ====================
    
    def load_devices(self, devices: List[Dict]) -> int:
        """
        Load cleaned device data into database
        
        Args:
            devices: List of cleaned device records
            
        Returns:
            int: Number of records loaded
        """
        logger.info("Phase 3: LOADING devices into database...")
        
        loaded_count = 0
        
        for device_data in devices:
            try:
                device, created = Device.objects.get_or_create(
                    hostname=device_data['hostname'],
                    defaults=device_data
                )
                
                if created:
                    loaded_count += 1
                    logger.debug(f"✅ Loaded device: {device.hostname}")
                else:
                    logger.debug(f"⚠️ Device already exists: {device.hostname}")
                
            except Exception as e:
                logger.error(f"❌ Error loading device {device_data.get('hostname')}: {e}")
                self.errors.append(f"Device loading error: {e}")
        
        logger.info(f"✅ Devices loading complete: {loaded_count} new records")
        return loaded_count
    
    def load_security_events(self, events: List[Dict]) -> int:
        """
        Load cleaned security events into database
        
        Args:
            events: List of cleaned security event records
            
        Returns:
            int: Number of records loaded
        """
        logger.info("Phase 3: LOADING security events into database...")
        
        loaded_count = 0
        
        for event_data in events:
            try:
                SecurityEvent.objects.create(**event_data)
                loaded_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error loading security event: {e}")
                self.errors.append(f"Security event loading error: {e}")
        
        logger.info(f"✅ Security events loading complete: {loaded_count} records")
        return loaded_count
    
    def load_system_metrics(self, metrics: List[Dict]) -> int:
        """
        Load system metrics into database
        
        Args:
            metrics: List of system metrics records
            
        Returns:
            int: Number of records loaded
        """
        logger.info("Phase 3: LOADING system metrics into database...")
        
        loaded_count = 0
        
        for metric_data in metrics:
            try:
                SystemMetrics.objects.create(**metric_data)
                loaded_count += 1
                
            except Exception as e:
                logger.error(f"❌ Error loading system metric: {e}")
                self.errors.append(f"System metric loading error: {e}")
        
        logger.info(f"✅ System metrics loading complete: {loaded_count} records")
        return loaded_count
    
    # ==================== UTILITY METHODS ====================
    
    def _validate_ip_address(self, ip: str) -> bool:
        """Validate IP address format"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(pattern, ip):
            parts = ip.split('.')
            return all(0 <= int(part) <= 255 for part in parts)
        return False
    
    def _categorize_device_type(self, role: str) -> str:
        """Categorize device type from role description"""
        role_lower = role.lower()
        
        if 'router' in role_lower:
            return 'router'
        elif 'server' in role_lower:
            return 'server'
        elif 'printer' in role_lower:
            return 'printer'
        elif 'pc' in role_lower or 'client' in role_lower:
            return 'workstation'
        else:
            return 'workstation'  # default
    
    def _determine_device_status(self, notes: str) -> str:
        """Determine device status from notes"""
        notes_lower = notes.lower()
        
        critical_keywords = ['no antivirus', 'outdated', 'no firewall', 'vulnerable']
        warning_keywords = ['ssl', 'tls', 'update', 'patch']
        
        if any(keyword in notes_lower for keyword in critical_keywords):
            return 'critical'
        elif any(keyword in notes_lower for keyword in warning_keywords):
            return 'warning'
        else:
            return 'active'
    
    def _categorize_security_event(self, event_type: str) -> Tuple[str, str, bool]:
        """Categorize event into security event type, severity, and threat level"""
        event_lower = event_type.lower()
        
        if 'login' in event_lower:
            return 'login_failure', 'critical', True
        elif 'checkout' in event_lower:
            return 'suspicious_traffic', 'warning', False
        elif 'wishlist' in event_lower:
            return 'unauthorized_access', 'warning', True
        elif 'profile' in event_lower:
            return 'suspicious_traffic', 'info', False
        else:
            return 'suspicious_traffic', 'info', False
    
    def _generate_source_ip(self, event_type: str) -> str:
        """Generate realistic source IP based on event type"""
        if 'login' in event_type.lower():
            # Login failures often come from external IPs
            return f"203.0.113.{np.random.randint(1, 254)}"
        else:
            # Internal activities from local network
            return f"192.168.1.{np.random.randint(1, 254)}"
    
    def _create_event_details(self, event_type: str, user_id: str, product_id: str, amount: float) -> str:
        """Create detailed event description"""
        details = f"Event Type: {event_type}"
        
        if user_id != 'unknown':
            details += f" | User: {user_id}"
        
        if product_id:
            details += f" | Product: {product_id}"
        
        if amount and amount > 0:
            details += f" | Amount: ${amount:.2f}"
        
        # Add security context
        if 'login' in event_type.lower():
            details += " | SECURITY: Multiple failed authentication attempts"
        elif 'checkout' in event_type.lower():
            details += " | BUSINESS: Transaction completed"
        
        return details
    
    def create_admin_user(self):
        """Create admin user for the system"""
        user, created = self.User.objects.get_or_create(
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
            logger.info("✅ Created admin user: admin / admin123")
        
        return user
    
    # ==================== MAIN ETL PROCESS ====================
    
    def run_pipeline(self) -> Dict:
        """
        Execute the complete ETL pipeline
        
        Returns:
            Dict: Pipeline execution summary
        """
        start_time = datetime.now()
        logger.info("��� Starting FinMark ETL Pipeline...")
        logger.info("=" * 70)
        
        # Clear existing data for fresh run
        logger.info("��� Clearing existing data...")
        SecurityEvent.objects.all().delete()
        SystemMetrics.objects.all().delete()
        UserActivity.objects.all().delete()
        
        # Create admin user
        admin_user = self.create_admin_user()
        
        # ============ EXTRACTION PHASE ============
        logger.info("\n��� PHASE 1: DATA EXTRACTION")
        logger.info("-" * 40)
        
        raw_devices_df = self.extract_network_inventory()
        raw_events_df = self.extract_event_logs()
        raw_marketing_df = self.extract_marketing_data()
        
        # ============ TRANSFORMATION PHASE ============
        logger.info("\n��� PHASE 2: DATA TRANSFORMATION")
        logger.info("-" * 40)
        
        cleaned_devices = self.clean_network_inventory(raw_devices_df)
        cleaned_events = self.clean_event_logs(raw_events_df)
        system_metrics = self.generate_system_metrics(cleaned_devices)
        
        # ============ LOADING PHASE ============
        logger.info("\n��� PHASE 3: DATA LOADING")
        logger.info("-" * 40)
        
        self.processed_records['devices'] = self.load_devices(cleaned_devices)
        self.processed_records['security_events'] = self.load_security_events(cleaned_events)
        self.processed_records['system_metrics'] = self.load_system_metrics(system_metrics)
        
        # ============ PIPELINE SUMMARY ============
        end_time = datetime.now()
        duration = end_time - start_time
        
        summary = {
            'pipeline_status': 'SUCCESS' if not self.errors else 'COMPLETED_WITH_WARNINGS',
            'execution_time': str(duration),
            'records_processed': self.processed_records,
            'total_records': sum(self.processed_records.values()),
            'errors_count': len(self.errors),
            'errors': self.errors[:5],  # Show first 5 errors
            'timestamp': end_time.isoformat()
        }
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ FINMARK ETL PIPELINE COMPLETED!")
        logger.info(f"⏱️ Execution Time: {duration}")
        logger.info(f"��� Total Records Processed: {summary['total_records']}")
        logger.info(f"❌ Errors: {len(self.errors)}")
        
        # Log detailed results
        for record_type, count in self.processed_records.items():
            logger.info(f"   • {record_type.replace('_', ' ').title()}: {count} records")
        
        # Save pipeline report
        self._save_pipeline_report(summary)
        
        return summary
    
    def _save_pipeline_report(self, summary: Dict):
        """Save pipeline execution report to file"""
        report_filename = f"etl_pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"��� Pipeline report saved: {report_filename}")


def main():
    """Main function to run the ETL pipeline"""
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    FinMark ETL Pipeline                      ║
    ║              Data Extraction, Transformation & Loading       ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize and run pipeline
    pipeline = FinMarkETLPipeline()
    
    try:
        summary = pipeline.run_pipeline()
        
        print(f"\n��� ETL PIPELINE SUMMARY:")
        print(f"   Status: {summary['pipeline_status']}")
        print(f"   Duration: {summary['execution_time']}")
        print(f"   Records: {summary['total_records']}")
        print(f"   Errors: {summary['errors_count']}")
        
        if summary['pipeline_status'] == 'SUCCESS':
            print("\n✅ Pipeline completed successfully!")
            print("��� You can now start the dashboard with: ./run.sh")
            print("��� Access dashboard at: http://localhost:8501")
            
        return 0
        
    except Exception as e:
        logger.error(f"��� Pipeline failed with critical error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
