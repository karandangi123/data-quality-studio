from typing import List
from .base import BaseDetector, Issue

class DuplicateDetector(BaseDetector):
    def detect(self, conn, raw_table: str, ref_table: str) -> List[Issue]:
        issues = []
        # customer_id is our assumed primary key for this dataset
        pk = 'customer_id'
        
        raw_cols = [r[0] for r in conn.execute(f"DESCRIBE {raw_table}").fetchall()]
        if pk not in raw_cols:
            return issues
            
        dup_count_df = conn.execute(f"""
            SELECT {pk}, COUNT(*) as cnt
            FROM {raw_table}
            GROUP BY {pk}
            HAVING COUNT(*) > 1
        """).df()
        
        if not dup_count_df.empty:
            num_dups = len(dup_count_df)
            sql_fix = f"""
WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER(
               PARTITION BY {pk}
               -- If there are duplicates, we keep the first one we see
           ) as rn
    FROM {raw_table}
)
SELECT * EXCLUDE(rn)
FROM ranked
WHERE rn=1;
            """.strip()
            
            issues.append(Issue(
                level="Content",
                category="Duplicate Keys",
                severity="Critical",
                column=pk,
                description=f"Found {num_dups} duplicated {pk}(s).",
                sql_fix=sql_fix
            ))
            
        return issues
