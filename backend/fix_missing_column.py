# fix_missing_column.py
import sqlite3
from pathlib import Path

# Connect to database
db_path = Path(__file__).parent / 'database' / 'accident_prediction.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check existing columns in accident_predictions table
cursor.execute("PRAGMA table_info(accident_predictions)")
columns = [col[1] for col in cursor.fetchall()]
print("Existing columns:", columns)

# List of columns to add if missing
columns_to_add = [
    ('light_condition', 'VARCHAR(50)', "ALTER TABLE accident_predictions ADD COLUMN light_condition VARCHAR(50)"),
    ('severity_score', 'FLOAT', "ALTER TABLE accident_predictions ADD COLUMN severity_score FLOAT"),
    ('actual_severity', 'VARCHAR(50)', "ALTER TABLE accident_predictions ADD COLUMN actual_severity VARCHAR(50)"),
    ('feedback_provided', 'BOOLEAN', "ALTER TABLE accident_predictions ADD COLUMN feedback_provided BOOLEAN DEFAULT 0"),
]

# Add missing columns
for col_name, col_type, sql_command in columns_to_add:
    if col_name not in columns:
        try:
            cursor.execute(sql_command)
            print(f"✅ Added '{col_name}' column")
        except Exception as e:
            print(f"⚠️ Could not add '{col_name}': {e}")

conn.commit()
conn.close()

print("\n✅ Database fixed! You can now restart the application.")