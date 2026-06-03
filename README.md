# Data Quality & SQL Repair Studio

Hi! Welcome to my submission for the Data Engineering Intern assignment. 

I built this web application to automate the tedious process of finding data quality issues in raw datasets and manually writing SQL to fix them. The core of this project is a **Plugin-Based Profiling Engine** that detects issues and generates runnable DuckDB SQL transformations.

## 🚀 Key Features & Architecture

When designing this, I wanted to ensure the system was modular, fast, and easy to extend. 

1. **Plugin Architecture (`detectors/`)**
   - **The Problem:** Hardcoding `if issue == 'null'` is brittle. The prompt explicitly requested that adding new issue types shouldn't require modifying the core profiling engine.
   - **My Solution:** I implemented an extensible plugin system. The core `DataProfiler` dynamically discovers any class inheriting from `BaseDetector` inside the `detectors` folder. To add a new check, you simply drop a new Python file in the folder!

2. **DuckDB Engine (`engine/`)**
   - I chose DuckDB over Pandas because it is built for fast analytical workloads and allows us to generate very elegant SQL (like `SELECT * REPLACE` and `EXCLUDE`). It processes the CSVs entirely in-memory.

3. **Interactive UI (`app.py`)**
   - Built with Streamlit for a fast, clean interface.
   - **Data Preview:** Instead of just generating the SQL, I added a feature to execute the generated SQL against DuckDB so you can immediately preview the cleaned data!

## 📁 Repository Structure

```text
├── app.py                 # Streamlit frontend dashboard
├── requirements.txt       # Dependencies (streamlit, duckdb, pandas)
├── engine/
│   ├── database.py        # DuckDB in-memory DB connection manager
│   └── profiler.py        # Engine that orchestrates detector plugins
├── detectors/
│   ├── base.py            # Abstract Base Class defining the plugin interface
│   ├── schema.py          # Detects schema mismatches (extra/missing columns)
│   ├── nulls.py           # Detects NOT NULL violations
│   ├── duplicates.py      # Detects duplicate primary keys via Window Functions
│   ├── types.py           # Detects data type drift
│   ├── domain.py          # Detects categorical/out-of-domain violations
│   └── format.py          # Detects format inconsistencies (Dates, Phones via Regex)
└── data/                  
    ├── raw/               # Messy dataset
    └── reference/         # Clean reference dataset
```

## 🛠️ How to Run

1. Clone this repository:
   ```bash
   git clone <your-repo-link>
   cd data-quality-studio
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the Streamlit application:
   ```bash
   streamlit run app.py
   ```
   *The application will automatically open in your default browser at `http://localhost:8501`.*

## 🔌 Adding a New Issue Type (Extensibility)

To add a new detector (e.g., an Email Format checker), you do not need to touch `app.py` or `profiler.py`. Simply create a new file in the `detectors/` directory:

```python
from typing import List
from .base import BaseDetector, Issue

class EmailDetector(BaseDetector):
    def detect(self, conn, raw_table: str, ref_table: str) -> List[Issue]:
        # Your SQL or Python detection logic goes here
        # Return a list of Issue objects with your generated SQL fixes
        return [Issue(category="Email", severity="Warning", column="email", description="Invalid email", sql_fix="...")]
```
The Profiler will automatically pick it up on the next run.

## 📹 Loom Video Walkthrough

[Insert Loom Video Link Here]

## 🌟 Future Improvements
If I had more time, I would:
- Add a "Download Cleaned Dataset" button that applies all SQL fixes and exports a clean CSV.
- Integrate unit tests for the individual detectors.
- Allow users to upload their own raw and reference datasets directly through the UI.

---
*Developed from scratch by Karan for the HealthKart Data Engineering Internship Assignment.*
