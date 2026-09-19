"""
Industrial Data Bridge
A live monitoring dashboard for industrial sensor/process data,
demonstrating OT-to-software integration: reading device-level data
(simulated here as Modbus register reads), applying specification-based
deviation checks, and visualizing trends and alerts in real time.

Run locally:
    streamlit run app.py

Deploy free:
    https://share.streamlit.io  (Streamlit Community Cloud) -- connect
    this GitHub repo and it deploys automatically.
"""

import time
from collections import deque

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_source import IndustrialDataSimulator
from alerting import check_deviations, severity

st.set_page_config(page_title="Industrial Data Bridge", layout="wide")

MAX_POINTS = 60  # rolling window of readings shown on the trend charts

if "history" not in st.session_state:
    st.session_state.history = deque(maxlen=MAX_POINTS)
if "simulator" not in st.session_state:
    st.session_state.simulator = IndustrialDataSimulator()
if "event_log" not in st.session_state:
    st.session_state.event_log = []

st.title("🏭 Industrial Data Bridge")
st.caption(
    "Live process monitoring — bridges device-level data (PLC/Modbus-style "
    "sensor reads) with a software dashboard for trending, deviation "
    "detection, and alerting."
)

col_controls, col_status = st.columns([1, 3])
with col_controls:
    running = st.toggle("Live feed", value=True)
    refresh_rate = st.slider("Refresh interval (sec)", 0.5, 3.0, 1.0, 0.5)

# --- Acquire one reading ---
if running:
    reading = st.session_state.simulator.read()
    st.session_state.history.append(reading)

    deviations = check_deviations(reading)
    sev = severity(deviations)
    if deviations:
        st.session_state.event_log.insert(
            0,
            {
                "time": reading.timestamp.strftime("%H:%M:%S"),
                "severity": sev,
                "details": ", ".join(
                    f"{d.parameter} = {d.value} (spec {d.low}-{d.high})"
                    for d in deviations
                ),
            },
        )
        st.session_state.event_log = st.session_state.event_log[:20]

# --- Status banner ---
if st.session_state.history:
    latest = st.session_state.history[-1]
    latest_dev = check_deviations(latest)
    latest_sev = severity(latest_dev)

    with col_status:
        if latest_sev == "Normal":
            st.success(f"✅ System Normal — last reading {latest.timestamp.strftime('%H:%M:%S')}")
        elif latest_sev == "Warning":
            st.warning(f"⚠️ Warning — 1 parameter out of tolerance ({latest.timestamp.strftime('%H:%M:%S')})")
        else:
            st.error(f"🚨 Critical — multiple parameters out of tolerance ({latest.timestamp.strftime('%H:%M:%S')})")

    # --- Current readings ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Temperature (°C)", latest.temperature_c)
    m2.metric("Pressure (bar)", latest.pressure_bar)
    m3.metric("Flow (L/min)", latest.flow_lpm)
    m4.metric("Vibration (mm/s)", latest.vibration_mm_s)

    # --- Trend chart ---
    df = pd.DataFrame(
        [
            {
                "time": r.timestamp,
                "Temperature (°C)": r.temperature_c,
                "Pressure (bar)": r.pressure_bar,
                "Flow (L/min)": r.flow_lpm,
                "Vibration (mm/s)": r.vibration_mm_s,
            }
            for r in st.session_state.history
        ]
    )

    st.subheader("Live Trends")
    param_choice = st.multiselect(
        "Parameters to plot",
        ["Temperature (°C)", "Pressure (bar)", "Flow (L/min)", "Vibration (mm/s)"],
        default=["Temperature (°C)", "Pressure (bar)"],
    )
    if param_choice:
        fig = go.Figure()
        for p in param_choice:
            fig.add_trace(go.Scatter(x=df["time"], y=df[p], mode="lines+markers", name=p))
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # --- Event / deviation log ---
    st.subheader("Deviation / Alert Log")
    if st.session_state.event_log:
        st.dataframe(pd.DataFrame(st.session_state.event_log), use_container_width=True, hide_index=True)
    else:
        st.info("No deviations detected yet.")

else:
    st.info("Toggle 'Live feed' to start receiving data.")

if running:
    time.sleep(refresh_rate)
    st.rerun()
