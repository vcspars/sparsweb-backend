"""
Migration script to add new fields to talk_to_sales_forms table
Run this once to update the existing database schema
"""
import sqlite3
import os
from pathlib import Path

# Get database path
db_path = Path(__file__).parent / "spars_forms.db"

if not db_path.exists():
    print(f"Database not found at {db_path}. It will be created automatically on next server start.")
    exit(0)

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(talk_to_sales_forms)")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Add new columns if they don't exist
    new_columns = {
        "current_system": "TEXT",
        "warehouses": "INTEGER",
        "users": "INTEGER",
        "requirements": "TEXT",
        "timeline": "TEXT"
    }
    
    for column_name, column_type in new_columns.items():
        if column_name not in columns:
            print(f"Adding column: {column_name}")
            cursor.execute(f"ALTER TABLE talk_to_sales_forms ADD COLUMN {column_name} {column_type}")
        else:
            print(f"Column {column_name} already exists, skipping...")
    
    conn.commit()
    print("Migration completed successfully!")
    
except Exception as e:
    print(f"Error during migration: {e}")
    conn.rollback()
finally:
    conn.close()


