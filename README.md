# Data Quality & SQL Repair Studio

🌍 **Live Demo:** https://data-quality-studio-fdj7uhv9xdxvdndt5yhtbl.streamlit.app/

This web application automates detecting data quality issues in raw datasets and generating runnable SQL to fix them.

## 🚀 Architecture

1. **Plugin-Based Profiling Engine**: Dynamically discovers issue detectors from `detectors/`. New issues can be added without modifying the engine.
2. **DuckDB**: Powers fast in-memory analytics and elegant SQL generation (`REPLACE`, `EXCLUDE`).
3. **Streamlit UI**: A clean dashboard rendering side-by-side **Schema-level** and **Content-level** issue reports with one-click SQL previews.

## 📁 Project Structure

```text
├── app.py                 # Streamlit dashboard
├── run.sh                 # Single-command startup script
├── engine/                # Profiling engine & database layer
├── detectors/             # Modular plugins (Schema, Nulls, Duplicates, Types, Domain, Format)
└── data/                  # Raw and reference datasets
```

## 🛠️ How to Run Locally

Clone the repository and execute the setup script (requires Python 3):

```bash
git clone <your-repo-link>
cd data-quality-studio
sh run.sh
```

## 🔌 Adding a New Detector

Create a Python file in `detectors/` inheriting from `BaseDetector`.
Set `level="Schema"` or `level="Content"` in the returned `Issue` objects. The `DataProfiler` will load it automatically.

## 📹 Loom Walkthrough
[Watch the Loom Walkthrough Here](https://www.loom.com/share/5970483aab3243c999ab71941c092813)
