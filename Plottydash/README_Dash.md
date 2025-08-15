
# SpaceX Dashboard — Plotly Dash

This is the Plotly Dash app for the IBM Data Science Capstone (SpaceX).

## Features
- **Dropdown** to select **Launch Site** (or **All Sites**).
- **Pie chart**: success vs. failure (overall or per selected site).
- **RangeSlider** for **Payload Mass (kg)** to filter missions.
- **Scatter chart**: **Payload Mass (kg)** vs **class** (0/1), colored by **Orbit**.

## Run locally
```bash
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:8050/
```

The app will use `data/spacex_launches_clean.csv` if present; otherwise it falls back to an IBM-hosted CSV.
