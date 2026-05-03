# test_db.py - Test database connection
import os
import sqlite3
from pathlib import Path

# Get backend directory
backend_dir = Path(__file__).parent
database_dir = backend_dir / 'database'

# Create directory if it doesn't exist (FIXED: exist_ok not exit_ok)
database_dir.mkdir(exist_ok=True)

# Database path
db_path = database_dir / 'accident_prediction.db'

print(f"📁 Backend directory: {backend_dir}")
print(f"📁 Database directory: {database_dir}")
print(f"📄 Database file: {db_path}")

try:
    # Test SQLite connection
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create a test table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')
    
    conn.commit()
    print("✅ SQLite connection successful!")
    print(f"✅ Database file created at: {db_path}")
    
    # Close connection
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")