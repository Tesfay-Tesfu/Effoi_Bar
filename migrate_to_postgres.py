import sqlite3
import psycopg2
import os
from psycopg2.extras import execute_values
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    
    # SQLite connection
    sqlite_db = 'instance/effoi.db'  # or wherever your SQLite DB is
    if not os.path.exists(sqlite_db):
        logger.warning(f"SQLite database {sqlite_db} not found. Skipping migration.")
        return
    
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # PostgreSQL connection from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return
    
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    pg_conn = psycopg2.connect(database_url)
    pg_cursor = pg_conn.cursor()
    
    # Get all tables from SQLite
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = sqlite_cursor.fetchall()
    
    for table in tables:
        table_name = table['name']
        if table_name.startswith('sqlite_'):
            continue
        
        logger.info(f"Migrating table: {table_name}")
        
        # Get column info
        sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in sqlite_cursor.fetchall()]
        
        if not columns:
            continue
        
        # Get data
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            continue
        
        # Insert into PostgreSQL
        placeholders = ','.join(['%s'] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        
        for row in rows:
            try:
                pg_cursor.execute(insert_query, tuple(row))
            except Exception as e:
                logger.error(f"Error inserting into {table_name}: {e}")
                pg_conn.rollback()
                continue
        
        pg_conn.commit()
        logger.info(f"Migrated {len(rows)} rows to {table_name}")
    
    sqlite_conn.close()
    pg_conn.close()
    logger.info("Migration completed!")

if __name__ == '__main__':
    migrate_data()
