import os
import shutil
import glob

def cleanup_project():
    """Remove unwanted files and directories"""
    
    # Directories to remove
    dirs_to_remove = [
        '__pycache__',
        'backend/__pycache__',
        'frontend/__pycache__',
        'instance',
        'backend/instance',
        '.pytest_cache',
        '.vscode',
        '.idea',
        'migrations',
    ]
    
    # Files to remove
    files_to_remove = [
        '*.pyc',
        '*.pyo',
        '*.db',
        '*.sqlite',
        '*.sqlite3',
        '*.ipynb',
        'animation1.html',
        'cleanup.sh',
        'create_upload_dir.py',
        'deploy.sh',
        'init_db.py',
        'init_production_db.py',
        'nginx_config.conf',
        'run_local.sh',
        'setup_all.py',
        'setup_media.py',
        'wsgi.py',
        '*.bak',
        '*.backup'
    ]
    
    removed_count = 0
    
    # Remove directories
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✅ Removed directory: {dir_path}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing {dir_path}: {e}")
    
    # Remove files
    for pattern in files_to_remove:
        for file_path in glob.glob(pattern, recursive=True):
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    print(f"✅ Removed file: {os.path.basename(file_path)}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Error removing {file_path}: {e}")
    
    print(f"\n✨ Cleanup complete! Removed {removed_count} items.")

if __name__ == '__main__':
    cleanup_project()
