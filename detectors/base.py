from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List

@dataclass
class Issue:
    """
    Represents a single data quality issue found by a detector.
    This structure is clean and easy to render in a UI.
    """
    category: str        # e.g., "Schema Mismatch", "Type Drift"
    severity: str        # e.g., "Critical", "Warning", "Info"
    column: str          # The column that has the issue
    description: str     # A clear explanation of what is wrong
    sql_fix: str         # The DuckDB SQL query to fix the data

class BaseDetector(ABC):
    """
    The Base Class for all detectors (Plugin Architecture).
    Any new detector must inherit from this class and implement the detect method.
    """
    
    @abstractmethod
    def detect(self, conn, raw_table: str, ref_table: str) -> List[Issue]:
        """
        Detects issues between raw_table and ref_table.
        
        Args:
            conn: A DuckDB connection object.
            raw_table: The name of the raw data table in DuckDB.
            ref_table: The name of the reference data table in DuckDB.
            
        Returns:
            A list of Issue objects.
        """
        pass
