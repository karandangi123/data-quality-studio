from typing import List
from .base import BaseDetector, Issue

class NullDetector(BaseDetector):
    def detect(self, conn, raw_table: str, ref_table: str) -> List[Issue]:
        issues = []
        raw_cols = [r[0] for r in conn.execute(f"DESCRIBE {raw_table}").fetchall()]
        
        for col in raw_cols:
            null_count = conn.execute(f"""
                SELECT COUNT(*) FROM {raw_table} 
                WHERE {col} IS NULL OR CAST({col} AS VARCHAR) = ''
            """).fetchone()[0]
            
            if null_count > 0:
                # DuckDB's REPLACE syntax is super elegant for fixing a single column in a SELECT *
                sql_fix = f"SELECT * REPLACE (COALESCE(NULLIF(CAST({col} AS VARCHAR), ''), 'Unknown') AS {col}) FROM {raw_table};"
                issues.append(Issue(
                    level="Content",
                    category="Null Violations",
                    severity="Warning",
                    column=col,
                    description=f"Found {null_count} null or empty values in '{col}'.",
                    sql_fix=sql_fix
                ))
                
        return issues
