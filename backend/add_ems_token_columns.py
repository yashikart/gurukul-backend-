"""
Migration script to add ems_token and ems_token_expires_at columns to users table.
Run this once to update the database schema.
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
    
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    print(f"Existing columns in 'users' table: {columns}")
    
    # Add ems_token column if it doesn't exist
    if 'ems_token' in columns:
        print("✓ Column 'ems_token' already exists in users table")
    else:
        print("Adding 'ems_token' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN ems_token TEXT")
        conn.commit()
        print("✓ Successfully added 'ems_token' column to users table")
    
    # Add ems_token_expires_at column if it doesn't exist
    if 'ems_token_expires_at' in columns:
        print("✓ Column 'ems_token_expires_at' already exists in users table")
    else:
        print("Adding 'ems_token_expires_at' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN ems_token_expires_at TEXT")
        conn.commit()
        print("✓ Successfully added 'ems_token_expires_at' column to users table")
    
    conn.close()
    print("\n✅ Database update complete! Migration successful.")
    
except sqlite3.Error as e:
    print(f"\n❌ Error updating database: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

