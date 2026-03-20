"""
Backup existing SQLite data if it exists
"""

import os
import json
import sqlite3
from datetime import datetime

def backup_existing_data():
    """Backup existing SQLite database to JSON"""
    
    # Check multiple possible SQLite locations
    possible_paths = [
        'instance/effoi.db',
        'effoi.db',
        'backend/instance/effoi.db'
    ]
    
    sqlite_path = None
    for path in possible_paths:
        if os.path.exists(path):
            sqlite_path = path
            break
    
    if not sqlite_path:
        print("ℹ️  No existing SQLite database found. Starting fresh.")
        return
    
    print(f"✅ Found SQLite database at {sqlite_path}")
    
    try:
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        data = {}
        for table in tables:
            table_name = table['name']
            if not table_name.startswith('sqlite_'):
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                data[table_name] = [dict(row) for row in rows]
                print(f"  ✓ Exported {len(rows)} rows from {table_name}")
        
        conn.close()
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backup_data_{timestamp}.json'
        
        with open(backup_file, 'w') as f:
            json.dump(data, f, default=str)
        
        print(f"✅ Data backed up to {backup_file}")
        print("⚠️  This backup can be imported to PostgreSQL later using migrate_data.py")
        
    except Exception as e:
        print(f"❌ Error backing up data: {e}")

if __name__ == '__main__':
    backup_existing_data()
