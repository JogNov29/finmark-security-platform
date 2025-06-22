#!/usr/bin/env python3
"""
Cleanup script for temporary Python files used during development
"""

import os
import glob
from pathlib import Path

def cleanup_temp_files():
    """Remove temporary development files"""
    
    print("🧹 Cleaning up temporary files...")
    
    # Common temporary file patterns
    temp_patterns = [
        '*.tmp',
        '*.temp', 
        '*_temp.py',
        '*_generator.py',
        '*_test.py',
        'temp_*.py',
        'test_*.py',
        'generate_*.py',
        'create_*.py',
        'setup_*.py',
        'load_*.py',  # But keep load_csv_data.py if it exists
        '__pycache__/*',
        '*.pyc',
        '*.pyo',
        '.pytest_cache/*',
        '.coverage',
        '*.log'
    ]
    
    # Files to keep (important ones)
    keep_files = [
        'manage.py',
        'load_csv_data.py',  # Keep this one as it's useful
        'finmark_auto_setup.py',  # The main setup script
        'start_finmark.sh',
        'start_finmark.bat'
    ]
    
    files_removed = 0
    
    for pattern in temp_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            filename = os.path.basename(file_path)
            
            # Don't remove important files
            if filename in keep_files:
                continue
                
            # Don't remove files in important directories
            if any(important in file_path for important in ['apps/', 'backend/', 'dashboard/']):
                continue
            
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"🗑️ Removed: {file_path}")
                    files_removed += 1
                elif os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                    print(f"🗑️ Removed directory: {file_path}")
                    files_removed += 1
            except Exception as e:
                print(f"⚠️ Could not remove {file_path}: {e}")
    
    # Remove empty directories
    for root, dirs, files in os.walk('.', topdown=False):
        for dirname in dirs:
            dir_path = os.path.join(root, dirname)
            try:
                if not os.listdir(dir_path):  # Empty directory
                    os.rmdir(dir_path)
                    print(f"🗑️ Removed empty directory: {dir_path}")
                    files_removed += 1
            except:
                pass
    
    print(f"\n✅ Cleanup complete! Removed {files_removed} temporary files/directories.")
    
    # Show what important files are kept
    print("\n📋 Important files kept:")
    important_files = [
        'manage.py',
        'apps/',
        'backend/',
        'dashboard/',
        'db.sqlite3',
        'requirements.txt',
        'start_finmark.sh',
        'start_finmark.bat'
    ]
    
    for item in important_files:
        if os.path.exists(item):
            print(f"   ✅ {item}")
        else:
            print(f"   ❌ {item} (not found)")

if __name__ == "__main__":
    print("🧹 Temporary File Cleanup Script")
    print("=" * 40)
    
    response = input("Are you sure you want to cleanup temporary files? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        cleanup_temp_files()
    else:
        print("❌ Cleanup cancelled.")