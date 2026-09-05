#!/usr/bin/env python
"""
Error Monitor Dashboard - Mendeteksi dan melacak semua error di aplikasi
"""

import os
import sys
import django
import json
import time
from datetime import datetime
from collections import defaultdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pulosarok_website.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.conf import settings

class ErrorMonitor:
    def __init__(self):
        self.client = Client()
        self.errors = defaultdict(list)
        self.test_results = []
        self.start_time = datetime.now()
        
    def setup_test_environment(self):
        """Setup environment untuk testing"""
        print("🔧 Setting up test environment...")
        
        # Create superuser for testing
        User = get_user_model()
        try:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@test.com',
                    password='admin123'
                )
                print("✅ Admin user created")
            
            # Login as admin
            self.client.login(username='admin', password='admin123')
            print("✅ Logged in as admin")
            
        except Exception as e:
            print(f"❌ Error setting up user: {e}")
            self.errors['setup'].append(str(e))
    
    def test_form_submissions(self):
        """Test form submission dengan data yang valid"""
        print("\n📝 Testing Form Submissions...")
        print("-" * 40)
        
        # Test Add Penduduk Form
        try:
            # Get form page first
            response = self.client.get('/pulosarok/references/admin/penduduk/add/')
            if response.status_code == 200:
                print("✅ Add Penduduk form loaded successfully")
                
                # Extract CSRF token
                csrf_token = None
                if 'csrfmiddlewaretoken' in response.content.decode():
                    # Try to extract token from form
                    content = response.content.decode()
                    import re
                    match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
                    if match:
                        csrf_token = match.group(1)
                        print("✅ CSRF token extracted successfully")
                
                # Test form submission
                form_data = {
                    'csrfmiddlewaretoken': csrf_token,
                    'nik': '1234567890123456',
                    'nama_lengkap': 'Test User',
                    'jenis_kelamin': 'L',
                    'tempat_lahir': 'Jakarta',
                    'tanggal_lahir': '1990-01-01',
                    'agama': 'Islam',
                    'pendidikan': 'SMA',
                    'pekerjaan': 'Swasta',
                    'status_perkawinan': 'Belum Kawin',
                    'hubungan_keluarga': 'Kepala Keluarga',
                    'kewarganegaraan': 'WNI',
                    'nomor_kk': '1234567890123456',
                    'alamat': 'Jl. Test No. 1',
                    'rt': '001',
                    'rw': '001',
                    'kode_pos': '12345',
                    'dusun': 1,  # Assuming dusun with ID 1 exists
                    'lorong': 1,  # Assuming lorong with ID 1 exists
                }
                
                # Submit form
                response = self.client.post('/pulosarok/references/admin/penduduk/add/', form_data)
                
                if response.status_code in [200, 302]:
                    print("✅ Form submission successful")
                else:
                    print(f"❌ Form submission failed: Status {response.status_code}")
                    self.errors['form_submission'].append(f"Add Penduduk failed: {response.status_code}")
                    
            else:
                print(f"❌ Failed to load Add Penduduk form: Status {response.status_code}")
                self.errors['form_load'].append(f"Add Penduduk form: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception in form submission test: {e}")
            self.errors['form_submission'].append(str(e))
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🔌 Testing API Endpoints...")
        print("-" * 40)
        
        api_endpoints = [
            '/pulosarok/references/api/penduduk/',
            '/pulosarok/references/api/dusun/',
            '/pulosarok/references/api/lorong/',
            '/api/references/api/penduduk/',
            '/api/references/api/dusun/',
        ]
        
        for endpoint in api_endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code == 200:
                    print(f"✅ {endpoint} - OK")
                    # Try to parse JSON
                    try:
                        data = response.json()
                        print(f"   📊 Returned {len(data) if isinstance(data, list) else 'object'} items")
                    except:
                        print("   ⚠️  Response is not JSON")
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
                    self.errors['api'].append(f"{endpoint}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {endpoint} - Exception: {e}")
                self.errors['api'].append(f"{endpoint}: {str(e)}")
    
    def test_database_connections(self):
        """Test database connections"""
        print("\n🗄️  Testing Database Connections...")
        print("-" * 40)
        
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                print(f"✅ Database connected - {table_count} tables found")
                
                # Test some key tables
                key_tables = ['references_penduduk', 'references_dusun', 'references_lorong']
                for table in key_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        print(f"✅ {table}: {count} records")
                    except Exception as e:
                        print(f"❌ {table}: {e}")
                        self.errors['database'].append(f"{table}: {str(e)}")
                        
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.errors['database'].append(str(e))
    
    def test_static_files(self):
        """Test static files loading"""
        print("\n📁 Testing Static Files...")
        print("-" * 40)
        
        static_files = [
            '/static/css/admin.css',
            '/static/js/admin.js',
        ]
        
        for static_file in static_files:
            try:
                response = self.client.get(static_file)
                if response.status_code == 200:
                    print(f"✅ {static_file} - OK")
                else:
                    print(f"❌ {static_file} - Status: {response.status_code}")
                    self.errors['static'].append(f"{static_file}: {response.status_code}")
            except Exception as e:
                print(f"❌ {static_file} - Exception: {e}")
                self.errors['static'].append(f"{static_file}: {str(e)}")
    
    def check_error_logs(self):
        """Check Django error logs"""
        print("\n📋 Checking Error Logs...")
        print("-" * 40)
        
        log_file = settings.BASE_DIR / 'django_errors.log'
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    logs = f.read()
                    if logs.strip():
                        print(f"⚠️  Found error logs ({len(logs)} characters)")
                        # Show last few lines
                        lines = logs.strip().split('\n')
                        for line in lines[-5:]:
                            print(f"   {line}")
                    else:
                        print("✅ No error logs found")
            except Exception as e:
                print(f"❌ Error reading log file: {e}")
        else:
            print("✅ No error log file exists")
    
    def generate_report(self):
        """Generate comprehensive error report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'total_errors': sum(len(errors) for errors in self.errors.values()),
            'error_categories': dict(self.errors),
            'summary': {
                'setup_errors': len(self.errors['setup']),
                'form_errors': len(self.errors['form_submission']) + len(self.errors['form_load']),
                'api_errors': len(self.errors['api']),
                'database_errors': len(self.errors['database']),
                'static_errors': len(self.errors['static']),
            }
        }
        
        # Save report
        with open('error_monitor_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_summary(self, report):
        """Print summary report"""
        print("\n" + "=" * 60)
        print("📊 ERROR MONITORING SUMMARY")
        print("=" * 60)
        print(f"⏱️  Duration: {report['duration_seconds']:.2f} seconds")
        print(f"🔍 Total Errors Found: {report['total_errors']}")
        print()
        
        for category, count in report['summary'].items():
            status = "✅" if count == 0 else "❌"
            print(f"{status} {category.replace('_', ' ').title()}: {count}")
        
        if report['total_errors'] > 0:
            print("\n🔍 Error Details:")
            print("-" * 40)
            for category, errors in report['error_categories'].items():
                if errors:
                    print(f"\n{category.upper()}:")
                    for i, error in enumerate(errors, 1):
                        print(f"  {i}. {error}")
        else:
            print("\n🎉 NO ERRORS FOUND! Application is working correctly.")
        
        print(f"\n💾 Full report saved to: error_monitor_report.json")
    
    def run_full_monitoring(self):
        """Run full error monitoring"""
        print("🚀 Starting Comprehensive Error Monitoring")
        print("=" * 60)
        
        self.setup_test_environment()
        self.test_database_connections()
        self.test_api_endpoints()
        self.test_form_submissions()
        self.test_static_files()
        self.check_error_logs()
        
        report = self.generate_report()
        self.print_summary(report)
        
        return report

if __name__ == '__main__':
    monitor = ErrorMonitor()
    monitor.run_full_monitoring()