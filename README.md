# Data Quality & SQL Repair Studio

🌍 **Live Demo:** https://data-quality-studio-fdj7uhv9xdxvdndt5yhtbl.streamlit.app/

This web application automates detecting data quality issues in raw datasets and generating runnable SQL to fix them.

## 🚀 Architecture

1. **Plugin-Based Profiling Engine**: The engine dynamically discovers issue detectors from the `detectors/` folder. Adding a new issue type does *not* require modifying the core engine.
2. **DuckDB**: Used for fast in-memory analytical workloads and elegant SQL generation (`REPLACE`, `EXCLUDE`).
3. **Streamlit**: A clean UI that allows executing the generated SQL to instantly preview the cleaned data.

## 📁 Project Structure

```text
├── app.py                 # Streamlit frontend dashboard
├── engine/                # Core profiling engine and DuckDB database layer
├── detectors/             # Modular plugin detectors (Schema, Nulls, Duplicates, Types, Domain, Format)
└── data/                  # Raw and reference datasets
```

## 🛠️ How to Run Locally

1. Clone this repository:
   ```bash
   git clone <your-repo-link>
   cd data-quality-studio
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## 🔌 Adding a New Detector

To add a new issue detector, simply create a new Python file in the `detectors/` directory inheriting from `BaseDetector`. The `DataProfiler` will automatically load it.

## 📹 Loom Walkthrough

[Insert Loom Video Link Here]
