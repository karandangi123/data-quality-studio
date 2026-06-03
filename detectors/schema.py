from typing import List
from .base import BaseDetector, Issue

class SchemaMismatchDetector(BaseDetector):
    def detect(self, conn, raw_table: str, ref_table: str) -> List[Issue]:
        issues = []
        raw_cols = [r[0] for r in conn.execute(f"DESCRIBE {raw_table}").fetchall()]
        ref_cols = [r[0] for r in conn.execute(f"DESCRIBE {ref_table}").fetchall()]
        
        extra_cols = set(raw_cols) - set(ref_cols)
        missing_cols = set(ref_cols) - set(raw_cols)
        
        if extra_cols:
            for col in extra_cols:
                safe_cols = ", ".join(ref_cols)
                # We drop the extra column by selecting only the valid reference columns
                sql_fix = f"SELECT {safe_cols} FROM {raw_table};"
                issues.append(Issue(
                    category="Schema Mismatch",
                    severity="Critical",
                    column=col,
                    description=f"Extra column '{col}' found in raw data.",
                    sql_fix=sql_fix
                ))
                
        if missing_cols:
            for col in missing_cols:
                issues.append(Issue(
                    category="Schema Mismatch",
                    severity="Critical",
                    column=col,
                    description=f"Missing column '{col}' in raw data.",
                    sql_fix=f"ALTER TABLE {raw_table} ADD COLUMN {col} VARCHAR;\nSELECT * FROM {raw_table};"
                ))
                
        return issues
