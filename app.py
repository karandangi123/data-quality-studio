import streamlit as st
import os
import pandas as pd
from engine.database import Database
from engine.profiler import DataProfiler

# Set the page configuration for a modern, wide layout
st.set_page_config(page_title="Data Quality & SQL Repair Studio", page_icon="🛠️", layout="wide")

# Custom CSS for clean and modern look
st.markdown("""
<style>
    .reportview-container {
        background: #fafafa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
    }
    .severity-Critical { color: #d9534f; font-weight: bold; }
    .severity-Warning { color: #f0ad4e; font-weight: bold; }
    .severity-Info { color: #5bc0de; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🛠️ Data Quality & SQL Repair Studio")
st.markdown("Automated data profiling and SQL generation for your messy datasets.")

def main():
    # Define paths to our datasets
    raw_path = "data/raw/customers_raw.csv"
    ref_path = "data/reference/customers_reference.csv"
    
    if not os.path.exists(raw_path) or not os.path.exists(ref_path):
        st.error(f"Datasets not found. Please ensure {raw_path} and {ref_path} exist.")
        return

    # To avoid Thread safety issues in Streamlit Cloud with DuckDB, 
    # we instantiate the database fresh on every thread run.
    db = Database()
    try:
        db.load_csv("raw_data", raw_path)
        db.load_csv("ref_data", ref_path)
    except Exception:
        db.conn.execute("DROP TABLE IF EXISTS raw_data")
        db.conn.execute("DROP TABLE IF EXISTS ref_data")
        db.load_csv("raw_data", raw_path)
        db.load_csv("ref_data", ref_path)

    # Load data on click
    if st.button("Start Profiling"):
        with st.spinner("Running Plugin Detectors..."):
            # Initialize our profiling engine which auto-discovers plugins
            profiler = DataProfiler()
            issues = profiler.profile(db.conn, "raw_data", "ref_data")
            
            # Save issues in session state so we don't re-run profiling every time
            st.session_state['issues'] = issues
            st.session_state['profiled'] = True

    if st.session_state.get('profiled'):
        issues = st.session_state['issues']
        
        # Top level metrics
        col1, col2, col3 = st.columns(3)
        raw_count = db.conn.execute("SELECT COUNT(*) FROM raw_data").fetchone()[0]
        ref_count = db.conn.execute("SELECT COUNT(*) FROM ref_data").fetchone()[0]
        
        col1.metric("Raw Rows", raw_count)
        col2.metric("Reference Rows", ref_count)
        col3.metric("Total Issues Detected", len(issues))
        
        st.divider()
        st.subheader("Data Quality Report")
        
        # Group issues by category for a cleaner UI
        issues_by_cat = {}
        for issue in issues:
            issues_by_cat.setdefault(issue.category, []).append(issue)
            
        for category, cat_issues in issues_by_cat.items():
            with st.expander(f"📌 {category} ({len(cat_issues)} issues)", expanded=True):
                for idx, issue in enumerate(cat_issues):
                    st.markdown(f"**Column**: `{issue.column}` | **Severity**: <span class='severity-{issue.severity}'>{issue.severity}</span>", unsafe_allow_html=True)
                    st.markdown(f"> {issue.description}")
                    
                    # Display the generated SQL. Streamlit handles copy-to-clipboard natively!
                    st.code(issue.sql_fix, language="sql")
                    
                    # Add a preview button to run the generated SQL
                    preview_key = f"preview_{category}_{issue.column}_{idx}"
                    if st.button(f"Preview Cleaned Data for {issue.column}", key=preview_key):
                        try:
                            # We limit to 5 rows for preview
                            preview_sql = issue.sql_fix.rstrip(';')
                            # If it's a CTE, we need to handle LIMIT carefully, but typically adding LIMIT 5 works
                            if "SELECT * EXCLUDE" in preview_sql or "SELECT * REPLACE" in preview_sql or "SELECT" in preview_sql:
                                preview_df = db.execute(f"{preview_sql} LIMIT 5;")
                                st.success("SQL executed successfully! Here is the preview:")
                                st.dataframe(preview_df)
                            else:
                                # For ALTER TABLE, we run it then preview the table
                                db.execute(preview_sql)
                                preview_df = db.execute("SELECT * FROM raw_data LIMIT 5;")
                                st.success("SQL executed successfully! Here is the preview:")
                                st.dataframe(preview_df)
                        except Exception as e:
                            st.error(f"Failed to execute SQL: {e}")
                    st.divider()

if __name__ == "__main__":
    main()
