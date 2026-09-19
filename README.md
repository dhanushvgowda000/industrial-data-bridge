# Industrial Data Bridge

A live monitoring dashboard that bridges **OT (device-level industrial data)** with **IT (software dashboards, alerting, and trend analysis)** — built to demonstrate the OT-to-software integration skillset used in Industry 4.0 / Industrial IoT environments.

## What it does

- Reads live sensor data (temperature, pressure, flow, vibration) at a configurable interval — simulating a Modbus register read from a PLC or field instrument
- Applies specification-based deviation checks (the same pattern used in instrument calibration to flag out-of-tolerance/OOT conditions)
- Classifies severity (Normal / Warning / Critical) based on how many parameters deviate
- Visualizes live trends on interactive charts
- Maintains a rolling deviation/alert log, similar to an incident/event log

## Why this exists

Most software engineers have never touched a PLC or an industrial protocol. Most instrumentation/automation engineers don't build software. This project sits deliberately at that intersection — real industrial-systems logic (deviation detection, specification limits, calibration-style tolerance checking) wired into a modern, live, interactive dashboard.

## Architecture

```
data_source.py   → simulates device-level sensor reads (swap for a real
                    pymodbus client to connect to an actual PLC/device)
alerting.py      → applies specification limits, flags deviations,
                    classifies severity
app.py           → Streamlit dashboard: live metrics, trend charts,
                    deviation/alert log
```

Connecting this to **real hardware** instead of the simulator only requires replacing the body of the read function in `data_source.py` with a `pymodbus` client call — everything downstream (dashboard, alerting, logging) works unchanged.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tech stack

Python, Streamlit, Plotly, pandas

## Author

Dhanush V Gowda — Electronics & Communication Engineer with hands-on industrial instrumentation experience (PLC, SCADA, DCS, field instrument calibration) and software development background (Python, cloud, CI/CD).
[LinkedIn](https://www.linkedin.com/in/dhanush-v-gowda/)
