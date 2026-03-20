"""
Pre-deployment Validation Script for EFFOI Restaurant
Run this before pushing to GitHub to ensure everything is ready
"""

import os
import sys

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    if not exists and required:
        print(f"{status} {filepath} - MISSING (required)")
        return False
    elif exists:
        print(f"{status} {filepath}")
    return exists

def check_directory_exists(dirpath, required=True):
    """Check if a directory exists"""
    exists = os.path.isdir(dirpath)
    status = "✅" if exists else "❌"
    if not exists and required:
        print(f"{status} {dirpath} - MISSING (required)")
        return False
    elif exists:
        print(f"{status} {dirpath}")
    return exists

def validate():
    """Run all validation checks"""
    
    print("=" * 60)
    print("EFFOI Restaurant - Deployment Validation")
    print("=" * 60)
    
    all_valid = True
    
    # Check required files
    print("\n📁 Checking required files...")
    required_files = [
        'backend/effoi_app.py',
        'requirements.txt',
        'render.yaml',
        '.gitignore'
    ]
    
    for file in required_files:
        if not check_file_exists(file):
            all_valid = False
    
    # Check optional but important files
    print("\n📄 Checking optional files...")
    optional_files = [
        '.env.example',
        'README.md',
        'migrate_data.py'
    ]
    
    for file in optional_files:
        check_file_exists(file, required=False)
    
    # Check directories
    print("\n📁 Checking directories...")
    required_dirs = [
        'frontend',
        'frontend/templates',
        'frontend/templates/public',
        'frontend/templates/admin',
        'frontend/static',
        'frontend/static/uploads'
    ]
    
    for dirpath in required_dirs:
        if not check_directory_exists(dirpath):
            all_valid = False
    
    # Check upload subdirectories
    print("\n📁 Checking upload directories...")
    upload_dirs = [
        'frontend/static/uploads/blog',
        'frontend/static/uploads/sliders',
        'frontend/static/uploads/events',
        'frontend/static/uploads/gallery',
        'frontend/static/uploads/menu',
        'frontend/static/uploads/about'
    ]
    
    for dirpath in upload_dirs:
        check_directory_exists(dirpath, required=False)
    
    # Check for .gitkeep files
    print("\n📁 Checking .gitkeep files...")
    for dirpath in upload_dirs:
        gitkeep = os.path.join(dirpath, '.gitkeep')
        check_file_exists(gitkeep, required=False)
    
    # Validate Python syntax of main app
    print("\n🐍 Validating Python syntax...")
    try:
        import py_compile
        py_compile.compile('backend/effoi_app.py', doraise=True)
        print("✅ backend/effoi_app.py syntax is valid")
    except Exception as e:
        print(f"❌ Syntax error in effoi_app.py: {e}")
        all_valid = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_valid:
        print("✅ ALL VALIDATION CHECKS PASSED! Ready for deployment.")
        print("\nNext steps:")
        print("1. Run: git add .")
        print("2. Run: git commit -m 'Ready for deployment'")
        print("3. Run: git push origin main")
        print("4. Deploy on Render.com")
    else:
        print("❌ VALIDATION FAILED! Please fix the issues above before deploying.")
    
    print("=" * 60)
    
    return all_valid

if __name__ == '__main__':
    sys.exit(0 if validate() else 1)
