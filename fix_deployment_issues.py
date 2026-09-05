#!/usr/bin/env python
"""
Script untuk memperbaiki masalah deployment
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def create_env_file():
    """Create .env file with secure defaults"""
    print("🔧 Creating .env file...")
    
    env_content = f"""# Django Environment Configuration
# Generated automatically - update as needed

# Security
SECRET_KEY={secrets.token_urlsafe(50)}

# Debug Mode (set to False in production)
DEBUG=True

# Allowed Hosts (comma-separated list)
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=sqlite:///db.sqlite3

# Static Files
STATIC_URL=/static/
STATIC_ROOT=staticfiles/

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=media/

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Logging
LOG_LEVEL=INFO

# Security Settings
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully")

def create_staticfiles_directory():
    """Create staticfiles directory"""
    print("🔧 Creating staticfiles directory...")
    
    staticfiles_dir = Path('staticfiles')
    staticfiles_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (staticfiles_dir / 'css').mkdir(exist_ok=True)
    (staticfiles_dir / 'js').mkdir(exist_ok=True)
    (staticfiles_dir / 'img').mkdir(exist_ok=True)
    
    print("✅ staticfiles directory created successfully")

def fix_dependencies():
    """Fix dependency conflicts"""
    print("🔧 Fixing dependency conflicts...")
    
    try:
        # Update cryptography
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            '--upgrade', 'cryptography>=43.0.3'
        ], check=True)
        
        # Update httpx to compatible version
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'httpx==0.25.2'
        ], check=True)
        
        print("✅ Dependencies updated successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update dependencies: {e}")
        return False
    
    return True

def collect_static_files():
    """Collect static files"""
    print("🔧 Collecting static files...")
    
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput'
        ], check=True)
        
        print("✅ Static files collected successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to collect static files: {e}")
        return False
    
    return True

def run_migrations():
    """Run database migrations"""
    print("🔧 Running migrations...")
    
    try:
        subprocess.run([
            sys.executable, 'manage.py', 'migrate'
        ], check=True)
        
        print("✅ Migrations completed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run migrations: {e}")
        return False
    
    return True

def create_deployment_checklist():
    """Create deployment checklist"""
    checklist = """# Deployment Checklist

## Pre-deployment
- [ ] Update SECRET_KEY in .env
- [ ] Set DEBUG=False in .env for production
- [ ] Update ALLOWED_HOSTS in .env
- [ ] Configure database settings
- [ ] Set up SSL certificates
- [ ] Configure static file serving
- [ ] Set up media file handling
- [ ] Configure email settings
- [ ] Set up logging
- [ ] Configure security headers

## Deployment
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Test all endpoints
- [ ] Check error monitoring
- [ ] Verify CSRF protection
- [ ] Test form submissions

## Post-deployment
- [ ] Monitor error logs
- [ ] Check performance
- [ ] Verify backup systems
- [ ] Test disaster recovery
- [ ] Update documentation

## Security Checklist
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] CSRF protection active
- [ ] SQL injection protection
- [ ] XSS protection enabled
- [ ] File upload security
- [ ] Authentication working
- [ ] Authorization properly configured
"""
    
    with open('DEPLOYMENT_CHECKLIST.md', 'w') as f:
        f.write(checklist)
    
    print("✅ Deployment checklist created")

def main():
    """Main function"""
    print("🚀 Starting deployment issue fixes...")
    print("="*50)
    
    # Create .env file
    create_env_file()
    
    # Create staticfiles directory
    create_staticfiles_directory()
    
    # Fix dependencies
    if fix_dependencies():
        print("✅ Dependencies fixed")
    else:
        print("⚠️  Some dependency issues may remain")
    
    # Run migrations
    if run_migrations():
        print("✅ Migrations completed")
    
    # Collect static files
    if collect_static_files():
        print("✅ Static files collected")
    
    # Create deployment checklist
    create_deployment_checklist()
    
    print("\n" + "="*50)
    print("🎉 Deployment fixes completed!")
    print("\nNext steps:")
    print("1. Review and update .env file")
    print("2. Run: python deployment_error_handler.py")
    print("3. Follow DEPLOYMENT_CHECKLIST.md")
    print("="*50)

if __name__ == '__main__':
    main()