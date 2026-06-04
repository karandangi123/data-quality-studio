from engine.database import Database
from engine.profiler import DataProfiler

print("Starting test...")
db = Database()
db.load_csv("raw_data", "data/raw/customers_raw.csv")
db.load_csv("ref_data", "data/reference/customers_reference.csv")

print("Data loaded. Running profiler...")
profiler = DataProfiler()
issues = profiler.profile(db.conn, "raw_data", "ref_data")
print(f"Found {len(issues)} issues.")

for issue in issues:
    print(issue.category, issue.column)
    print(issue.sql_fix)
    print("-----")
    # Test executing the SQL fix
    try:
        preview_sql = issue.sql_fix.rstrip(';')
        if "SELECT * EXCLUDE" in preview_sql or "SELECT * REPLACE" in preview_sql or "SELECT" in preview_sql:
            db.execute(f"{preview_sql} LIMIT 5;")
        else:
            db.execute(preview_sql)
    except Exception as e:
        print(f"ERROR executing SQL for {issue.category} on {issue.column}: {e}")

print("Test complete.")
