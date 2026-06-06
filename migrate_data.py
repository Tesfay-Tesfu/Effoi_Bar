"""
Data Migration Helper for EFFOI Restaurant
Run this to export SQLite data to JSON, then import to PostgreSQL
"""

import os
import json
import sqlite3
from datetime import datetime
from backend.effoi_app import app, db
from backend.effoi_app import *
    

def export_sqlite_to_json(sqlite_db_path='instance/effoi.db', output_file='backup_data.json'):
    """Export all SQLite data to JSON file"""
    
    if not os.path.exists(sqlite_db_path):
        print(f"❌ SQLite database not found at {sqlite_db_path}")
        return False
    
    conn = sqlite3.connect(sqlite_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    data = {}
    for table in tables:
        table_name = table['name']
        if not table_name.startswith('sqlite_'):
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            data[table_name] = [dict(row) for row in rows]
            print(f"✅ Exported {len(rows)} rows from {table_name}")
    
    conn.close()
    
    with open(output_file, 'w') as f:
        json.dump(data, f, default=str)
    
    print(f"✅ Data exported to {output_file}")
    return True

def import_json_to_postgres(json_file='backup_data.json'):
    """Import JSON data to PostgreSQL (run in Render shell)"""
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    imported_count = 0
    
    with app.app_context():
        for table_name, rows in data.items():
            if rows:
                # Try to find model class
                model_name = ''.join(word.capitalize() for word in table_name.split('_'))
                model = globals().get(model_name)
                
                if model:
                    for row in rows:
                        # Convert date strings to datetime objects
                        for key, value in row.items():
                            if 'date' in key.lower() and isinstance(value, str):
                                try:
                                    row[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                except:
                                    pass
                        
                        # Check if record exists
                        exists = model.query.get(row.get('id'))
                        if not exists:
                            obj = model(**row)
                            db.session.add(obj)
                            imported_count += 1
                    print(f"✅ Imported {len(rows)} rows to {table_name}")
                else:
                    print(f"⚠️ No model found for table {table_name}")
        
        db.session.commit()
        print(f"✅ Total imported: {imported_count} records")
    
    return True

if __name__ == '__main__':
    print("Data Migration Helper")
    print("1. Export SQLite to JSON")
    print("2. Import JSON to PostgreSQL")
    choice = input("Choose option (1/2): ")
    
    if choice == '1':
        export_sqlite_to_json()
    elif choice == '2':
        import_json_to_postgres()
