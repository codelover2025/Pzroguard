import sqlite3
import pandas as pd
import os

# Connect to the SQLite database
db_path = 'proguard.db'
export_dir = 'database_exports'

os.makedirs(export_dir, exist_ok=True)

# Connect to the database
conn = sqlite3.connect(db_path)

# Query to get all table names
query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
tables = pd.read_sql_query(query, conn)

print(f"\n[📦] Exporting Database Tables to: {export_dir}/")
print("-" * 50)

# Loop through all tables and export them to CSVs
for table_name in tables['name']:
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    csv_path = os.path.join(export_dir, f"{table_name}.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ Saved: {table_name}.csv ({len(df)} rows)")

conn.close()
print("-" * 50)
print(f"🎉 Database Export complete! You can find the Excel files in the '{export_dir}' folder.\n")
