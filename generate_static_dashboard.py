import os
import pandas as pd
from datetime import datetime

# Paths
data_folder = "data"
report_7271_path = os.path.join(data_folder, "R7271.xlsx")
report_7272_path = os.path.join(data_folder, "R7272.xlsx")
output_html = "docs/index.html"  # we'll put output in docs folder for GitHub Pages

def load_report(file_path, timestamp_col, label):
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        if timestamp_col not in df.columns:
            print(f"Warning: '{timestamp_col}' not found in {label}")
            return pd.DataFrame()
        df["timestamp"] = pd.to_datetime(df[timestamp_col], errors="coerce")
        df = df.dropna(subset=["timestamp"])
        df["Report"] = label
        return df
    else:
        print(f"File not found: {file_path}")
        return pd.DataFrame()

df1 = load_report(report_7271_path, "Power Down - Windows: Completed", "7271 - Windows")
df2 = load_report(report_7272_path, "Power Down - Linux: Completed", "7272 - Linux")

combined_df = pd.concat([df1, df2], ignore_index=True)
if combined_df.empty:
    print("No data available.")
    exit(1)

# Filter by fixed date range or entire dataset
start_date = datetime(2025, 1, 1)
end_date = combined_df["timestamp"].max()

def filter_data(df, start_date, end_date):
    if df.empty:
        return df
    return df[(df["timestamp"] >= start_date) & (df["timestamp"] <= end_date)]

filtered1 = filter_data(df1, start_date, end_date)
filtered2 = filter_data(df2, start_date, end_date)

# Simple HTML builder
def build_html():
    html = f"""
    <html>
    <head>
        <title>CCT Systems - Decommission Closure Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 900px; margin: auto; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 40px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            h2 {{ color: #2c3e50; }}
        </style>
    </head>
    <body>
        <h1>💻 CCT Systems - Decommission Closure Report</h1>

        <h2>📘 Report 7271 - Windows</h2>
        <p><b>Total Devices:</b> {int(filtered1["*Number of Devices"].sum()):,}</p>
        <p><b>Count of Titles:</b> {filtered1["Title"].dropna().shape[0]:,}</p>
        {filtered1.to_html(index=False)}

        <h2>🐧 Report 7272 - Linux</h2>
        <p><b>Total Devices:</b> {int(filtered2["*Number of Devices"].sum()):,}</p>
        <p><b>Count of Titles:</b> {filtered2["Title"].dropna().shape[0]:,}</p>
        {filtered2.to_html(index=False)}
    </body>
    </html>
    """
    return html

# Create docs folder if not exists
os.makedirs("docs", exist_ok=True)

with open(output_html, "w", encoding="utf-8") as f:
    f.write(build_html())

print(f"Static dashboard generated: {output_html}")
