#!/usr/bin/env python3
"""
Fix for FinMark with Custom User Model (core.User)
This handles the custom User model properly
"""

import os
import sys
import django
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    print("🔧 Setting up Django environment...")
    
    # Try different settings modules
    settings_modules = [
        'backend.settings',
        'finmark_project.settings', 
        'finmark.settings'
    ]
    
    for module in settings_modules:
        try:
            module_path = module.replace('.', os.sep) + '.py'
            if os.path.exists(module_path):
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', module)
                django.setup()
                print(f"✅ Successfully set up Django with {module}")
                return True
        except Exception as e:
            print(f"⚠️ Failed to setup with {module}: {e}")
            continue
    
    print("❌ Could not setup Django environment")
    return False

def check_user_model():
    """Check what User model is being used"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        print(f"✅ User model: {User._meta.label}")
        return User
    except Exception as e:
        print(f"❌ Could not get user model: {e}")
        return None

def create_users_with_custom_model():
    """Create users using the correct User model"""
    print("\n👥 Creating users with custom User model...")
    
    try:
        from django.contrib.auth import get_user_model
        from django.db import transaction
        
        User = get_user_model()
        print(f"📋 Using User model: {User._meta.label}")
        
        # User data
        users_data = [
            {
                'username': 'admin', 
                'password': 'admin123', 
                'email': 'admin@finmark.local', 
                'is_superuser': True, 
                'is_staff': True,
                'first_name': 'Admin',
                'last_name': 'User'
            },
            {
                'username': 'security', 
                'password': 'security123', 
                'email': 'security@finmark.local', 
                'is_staff': True,
                'first_name': 'Security',
                'last_name': 'Manager'
            },
            {
                'username': 'analyst', 
                'password': 'analyst123', 
                'email': 'analyst@finmark.local', 
                'is_staff': True,
                'first_name': 'Data',
                'last_name': 'Analyst'
            },
            {
                'username': 'manager', 
                'password': 'manager123', 
                'email': 'manager@finmark.local', 
                'is_staff': True,
                'first_name': 'Project',
                'last_name': 'Manager'
            },
        ]
        
        with transaction.atomic():
            for user_data in users_data:
                try:
                    # Remove existing user
                    User.objects.filter(username=user_data['username']).delete()
                    print(f"🗑️ Removed existing user: {user_data['username']}")
                    
                    # Create new user
                    if user_data.get('is_superuser'):
                        # Create superuser
                        user = User.objects.create_user(
                            username=user_data['username'],
                            email=user_data['email'],
                            password=user_data['password']
                        )
                        user.is_superuser = True
                        user.is_staff = True
                        user.first_name = user_data.get('first_name', '')
                        user.last_name = user_data.get('last_name', '')
                        user.save()
                    else:
                        # Create regular user
                        user = User.objects.create_user(
                            username=user_data['username'],
                            email=user_data['email'],
                            password=user_data['password']
                        )
                        user.is_staff = user_data.get('is_staff', False)
                        user.first_name = user_data.get('first_name', '')
                        user.last_name = user_data.get('last_name', '')
                        user.save()
                    
                    print(f"✅ Created user: {user_data['username']} / {user_data['password']}")
                    
                except Exception as e:
                    print(f"❌ Error creating user {user_data['username']}: {e}")
        
        # Verify users
        total_users = User.objects.count()
        print(f"\n📊 Total users in database: {total_users}")
        
        print("\n👥 All users:")
        for user in User.objects.all():
            role = "Superuser" if user.is_superuser else "Staff" if user.is_staff else "User"
            print(f"   🔑 {user.username} ({user.email}) - {role}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in user creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_tables():
    """Check what tables exist in the database"""
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📋 Database tables ({len(tables)} total):")
        for table in tables:
            print(f"   - {table}")
        
        # Check specifically for user-related tables
        user_tables = [t for t in tables if 'user' in t.lower()]
        if user_tables:
            print(f"\n👤 User-related tables:")
            for table in user_tables:
                print(f"   - {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def run_migrations():
    """Run migrations to ensure database is up to date"""
    print("\n🔄 Running Django migrations...")
    
    try:
        from django.core.management import execute_from_command_line
        
        # Make migrations for all apps
        print("📝 Making migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # Apply migrations
        print("⚡ Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✅ Migrations completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def test_authentication():
    """Test if authentication works"""
    print("\n🧪 Testing authentication...")
    
    try:
        from django.contrib.auth import authenticate
        
        # Test admin user
        user = authenticate(username='admin', password='admin123')
        if user:
            print(f"✅ Admin authentication successful: {user.username}")
            print(f"   - Is superuser: {user.is_superuser}")
            print(f"   - Is staff: {user.is_staff}")
            print(f"   - Email: {user.email}")
        else:
            print("❌ Admin authentication failed")
        
        # Test other users
        test_users = ['security', 'analyst', 'manager']
        for username in test_users:
            user = authenticate(username=username, password=f'{username}123')
            if user:
                print(f"✅ {username} authentication successful")
            else:
                print(f"❌ {username} authentication failed")
        
        return user is not None
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def main():
    """Main execution function"""
    print("🛠️ FinMark Custom User Model Fix")
    print("=" * 40)
    
    # Setup Django
    if not setup_django():
        print("❌ Cannot continue without Django setup")
        return
    
    # Check user model
    User = check_user_model()
    if not User:
        print("❌ Cannot determine User model")
        return
    
    # Check current database state
    print("\n🔍 Checking current database state...")
    check_database_tables()
    
    # Run migrations to ensure everything is up to date
    if not run_migrations():
        print("⚠️ Migration issues, but continuing...")
    
    # Create users
    if create_users_with_custom_model():
        print("\n✅ User creation completed successfully")
    else:
        print("\n❌ User creation failed")
        return
    
    # Test authentication
    if test_authentication():
        print("\n✅ Authentication testing successful")
    else:
        print("\n❌ Authentication testing failed")
    
    print("\n🎉 Custom User Model Fix Complete!")
    print("=" * 45)
    print("\n🔑 Login Credentials:")
    print("   Admin:    admin / admin123 (Superuser)")
    print("   Security: security / security123 (Staff)")
    print("   Analyst:  analyst / analyst123 (Staff)")
    print("   Manager:  manager / manager123 (Staff)")
    print("\n🌐 Test your login at:")
    print("   📊 Dashboard: http://localhost:8501")
    print("   🔧 Django Admin: http://localhost:8000/admin")

if __name__ == "__main__":
    main()