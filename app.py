# 🏥 Real-Time Hospital ICU Occupancy Dashboard — Colab Single-File Version

# Setup: install and configure dependencies
!pip install streamlit pyngrok pandas --quiet

NGROK_AUTH_TOKEN = "YOUR_TOKEN_HERE"  # 🔒 set your ngrok token
from pyngrok import ngrok
if NGROK_AUTH_TOKEN and "YOUR_TOKEN_HERE" not in NGROK_AUTH_TOKEN:
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# Write Streamlit app
%%writefile app.py
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hospital ICU Dashboard", layout="wide")
st.title("🏥 ICU Occupancy Comparison — Adult vs Pediatric")

# Data loader with fallback for Colab or local paths
def load_csv(name):
    path = f"/content/{name}" if os.path.exists(f"/content/{name}") else name
    if not os.path.exists(path):
        st.error(f"Missing file: {name}")
        st.stop()
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date"])

adult = load_csv("adult_icu_cleaned.csv")
pediatric = load_csv("pediatric_icu_cleaned.csv")

# Compute utilization if absent
for df, label in [(adult, "adult"), (pediatric, "pediatric")]:
    if "icu_utilization_pct" not in df.columns and {"icu_capacity", "icu_occupied"}.issubset(df.columns):
        df["icu_utilization_pct"] = (df["icu_occupied"] / df["icu_capacity"]).clip(0, 1) * 100
    df.rename(columns={"icu_utilization_pct": f"{label}_icu_utilization_pct"}, inplace=True)

# Merge on date/state
merged = pd.merge(adult, pediatric, on=["date", "state"], how="inner", suffixes=("_adult", "_pediatric"))
if merged.empty:
    st.warning("No overlapping data between datasets.")
    st.stop()

# Sidebar filters
states = sorted(merged["state"].unique())
sel_state = st.sidebar.selectbox("Select State", states)
state_data = merged[merged["state"] == sel_state].sort_values("date")

min_d, max_d = state_data["date"].min().date(), state_data["date"].max().date()
date_sel = st.sidebar.date_input("Select Date Range", (min_d, max_d), min_value=min_d, max_value=max_d)
start_d, end_d = date_sel if isinstance(date_sel, tuple) else (date_sel, date_sel)

filtered = state_data[(state_data["date"].dt.date >= start_d) & (state_data["date"].dt.date <= end_d)]
if filtered.empty:
    st.info("No data available for selected range.")
    st.stop()

# KPI metrics
latest = filtered.iloc[-1]
col1, col2 = st.columns(2)
col1.metric(f"Adult ICU Utilization ({sel_state})", f"{latest['adult_icu_utilization_pct']:.1f}%")
col2.metric(f"Pediatric ICU Utilization ({sel_state})", f"{latest['pediatric_icu_utilization_pct']:.1f}%")

# Trend visualization
st.subheader(f"ICU Utilization Trends — {sel_state}")
st.line_chart(filtered.set_index("date")[["adult_icu_utilization_pct", "pediatric_icu_utilization_pct"]])

# Download
st.download_button(
    "⬇️ Download Filtered Data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name=f"{sel_state}_icu_data.csv",
    mime="text/csv",
)

# Launch Streamlit via ngrok
from pyngrok import ngrok
import subprocess
try:
    ngrok.kill()
except:
    pass

subprocess.Popen(["streamlit", "run", "app.py"])
public_url = ngrok.connect(8501, bind_tls=True)
print("🚀 App running at:", public_url)
