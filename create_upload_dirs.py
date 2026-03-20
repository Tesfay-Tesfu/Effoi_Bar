# create_upload_dirs.py - SAFE VERSION (creates only missing directories)
import os

def create_upload_directories():
    """Safely create only missing upload directories"""
    
    upload_folders = [
        'frontend/static/uploads/blog',
        'frontend/static/uploads/sliders',
        'frontend/static/uploads/events',
        'frontend/static/uploads/events/gallery',
        'frontend/static/uploads/gallery',
        'frontend/static/uploads/menu',
        'frontend/static/uploads/about',
        'frontend/static/uploads/about/gallery',
        'frontend/static/uploads/temp'
    ]
    
    created_count = 0
    existing_count = 0
    
    for folder in upload_folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"✅ Created: {folder}")
            created_count += 1
        else:
            print(f"⏭️  Already exists: {folder}")
            existing_count += 1
        
        # Create .gitkeep file if it doesn't exist
        gitkeep_path = os.path.join(folder, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                f.write('# This directory is preserved for uploads\n')
            print(f"   📝 Added .gitkeep to: {folder}")
    
    print(f"\n✨ Summary: Created {created_count} directories, {existing_count} already existed")

if __name__ == '__main__':
    create_upload_directories()
