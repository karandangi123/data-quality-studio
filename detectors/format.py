from typing import List
from .base import BaseDetector, Issue

class FormatDetector(BaseDetector):
    def detect(self, conn, raw_table: str, ref_table: str) -> List[Issue]:
        issues = []
        raw_cols = [r[0] for r in conn.execute(f"DESCRIBE {raw_table}").fetchall()]
        
        # Check signup_date format (YYYY-MM-DD)
        if 'signup_date' in raw_cols:
            invalid_dates = conn.execute(f"""
                SELECT COUNT(*) FROM {raw_table}
                WHERE signup_date IS NOT NULL 
                AND CAST(signup_date AS VARCHAR) != ''
                AND NOT regexp_matches(CAST(signup_date AS VARCHAR), r'^\d{{4}}-\d{{2}}-\d{{2}}$')
            """).fetchone()[0]
            
            if invalid_dates > 0:
                issues.append(Issue(
                    category="Format Inconsistencies",
                    severity="Warning",
                    column="signup_date",
                    description=f"Found {invalid_dates} dates not matching YYYY-MM-DD format.",
                    sql_fix=f"SELECT * REPLACE (TRY_CAST(signup_date AS DATE) AS signup_date) FROM {raw_table};"
                ))
                
        # Check phone format (+91-XXXXX...)
        if 'phone' in raw_cols:
            invalid_phones = conn.execute(f"""
                SELECT COUNT(*) FROM {raw_table}
                WHERE phone IS NOT NULL 
                AND CAST(phone AS VARCHAR) != ''
                AND NOT regexp_matches(CAST(phone AS VARCHAR), r'^\+\d{{2}}-\d{{10}}$')
            """).fetchone()[0]
            
            if invalid_phones > 0:
                issues.append(Issue(
                    category="Format Inconsistencies",
                    severity="Warning",
                    column="phone",
                    description=f"Found {invalid_phones} phones not matching +XX-XXXXXXXXXX format.",
                    # Removes all non-numeric characters and formats as +91-XXXXXXXXXX (assuming Indian numbers for this assignment)
                    sql_fix=f"SELECT * REPLACE ('+91-' || RIGHT(regexp_replace(CAST(phone AS VARCHAR), '[^0-9]', '', 'g'), 10) AS phone) FROM {raw_table};"
                ))
                
        return issues
