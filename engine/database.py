import duckdb
import os

class Database:
    """
    Handles the DuckDB connection and data loading.
    We use an in-memory database for speed and simplicity.
    """
    def __init__(self):
        # Create an in-memory DuckDB connection
        self.conn = duckdb.connect(database=':memory:')

    def load_csv(self, table_name: str, csv_path: str):
        """
        Loads a CSV file into a DuckDB table.
        DuckDB's read_csv_auto infers schema automatically.
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        
        # Using read_csv_auto with all_varchar=True is sometimes useful for raw data,
        # but read_csv_auto is smart enough to handle types.
        # We will load it normally, but if there are format issues, DuckDB might complain.
        # To make it robust against really bad data, we can read everything as VARCHAR
        # and do the casting in SQL.
        query = f"""
        CREATE TABLE {table_name} AS 
        SELECT * FROM read_csv_auto('{csv_path}', all_varchar=true)
        """
        self.conn.execute(query)

    def get_columns(self, table_name: str):
        """
        Returns a list of column names for a given table.
        """
        result = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
        # The first column in DESCRIBE result is the column name
        return [row[0] for row in result]
    
    def execute(self, query: str):
        """
        Executes a query and returns a pandas DataFrame.
        """
        return self.conn.execute(query).df()
