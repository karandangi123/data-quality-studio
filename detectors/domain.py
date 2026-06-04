from typing import List
from .base import BaseDetector, Issue

class DomainDetector(BaseDetector):
    def detect(self, conn, raw_table: str, ref_table: str) -> List[Issue]:
        issues = []
        # Find string columns in reference data that have a small domain (categorical)
        ref_cols = [r[0] for r in conn.execute(f"DESCRIBE {ref_table}").fetchall() if r[1] == 'VARCHAR']
        raw_cols = [r[0] for r in conn.execute(f"DESCRIBE {raw_table}").fetchall()]
        
        for col in ref_cols:
            if col not in raw_cols:
                continue
                
            # Skip high cardinality columns
            if col in ['customer_id', 'full_name', 'email', 'phone', 'signup_date']:
                continue
            
            # Get valid values from reference
            valid_values = [str(r[0]) for r in conn.execute(f"SELECT DISTINCT {col} FROM {ref_table} WHERE {col} IS NOT NULL").fetchall()]
            
            if not valid_values or len(valid_values) > 20:
                continue
                
            # DuckDB handles list containment cleanly
            valid_list_str = "[" + ", ".join(f"'{v}'" for v in valid_values) + "]"
            
            invalid_count = conn.execute(f"""
                SELECT COUNT(*) FROM {raw_table} 
                WHERE {col} IS NOT NULL 
                AND CAST({col} AS VARCHAR) != ''
                AND NOT list_contains({valid_list_str}, CAST({col} AS VARCHAR))
            """).fetchone()[0]
            
            if invalid_count > 0:
                invalids = [str(r[0]) for r in conn.execute(f"""
                    SELECT DISTINCT {col} FROM {raw_table} 
                    WHERE {col} IS NOT NULL 
                    AND CAST({col} AS VARCHAR) != ''
                    AND NOT list_contains({valid_list_str}, CAST({col} AS VARCHAR))
                    LIMIT 3
                """).fetchall()]
                
                # We can generate SQL to NULL out invalid domains or uppercase/lowercase them
                sql_fix = f"""
-- Invalid values are nulled out, but you can also write a CASE WHEN to map them
SELECT * REPLACE (
    CASE WHEN list_contains({valid_list_str}, CAST({col} AS VARCHAR)) THEN {col} 
    ELSE NULL END AS {col}
) FROM {raw_table};
                """.strip()
                
                issues.append(Issue(
                    level="Content",
                    category="Out-of-Domain Values",
                    severity="Warning",
                    column=col,
                    description=f"Found {invalid_count} out-of-domain values (e.g., {', '.join(invalids)}). Expected one of {valid_values}.",
                    sql_fix=sql_fix
                ))
                
        return issues
