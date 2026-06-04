from typing import List
from .base import BaseDetector, Issue

class TypeDriftDetector(BaseDetector):
    def detect(self, conn, raw_table: str, ref_table: str) -> List[Issue]:
        issues = []
        raw_info = {r[0]: r[1] for r in conn.execute(f"DESCRIBE {raw_table}").fetchall()}
        ref_info = {r[0]: r[1] for r in conn.execute(f"DESCRIBE {ref_table}").fetchall()}
        
        for col, ref_type in ref_info.items():
            if col in raw_info:
                raw_type = raw_info[col]
                # If the reference expects a more specific type than raw (like BOOLEAN vs VARCHAR)
                if raw_type != ref_type:
                    sql_fix = f"SELECT * REPLACE (TRY_CAST({col} AS {ref_type}) AS {col}) FROM {raw_table};"
                    issues.append(Issue(
                        level="Schema",
                        category="Type Drift",
                        severity="Critical",
                        column=col,
                        description=f"Type mismatch: Reference expects {ref_type}, but Raw contains {raw_type}.",
                        sql_fix=sql_fix
                    ))
                    
        return issues
