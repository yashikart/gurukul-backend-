"""
Script to add the missing cohort_id column to the users table
Run this once to update your existing database schema
"""
import sqlite3
import os

# Path to database
db_path = os.path.join(os.path.dirname(__file__), 'gurukul.db')

if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
    print("The database will be created automatically on next startup.")
    exit(0)

print(f"Connecting to database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'cohort_id' in columns:
        print("✓ Column 'cohort_id' already exists in users table")
    else:
        print("Adding 'cohort_id' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN cohort_id TEXT")
        conn.commit()
        print("✓ Successfully added 'cohort_id' column to users table")
    
    conn.close()
    print("Database update complete!")
    
except sqlite3.Error as e:
    print(f"Error updating database: {e}")
    exit(1)

