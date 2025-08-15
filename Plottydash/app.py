#%%

# app.py — SpaceX Launch Dashboard (Plotly Dash)
# Author: Iliya Pezeshki

!pip install -r requirements.txt

# Then open http://127.0.0.1:8050/ in your browser.

import pandas as pd
import numpy as np
from pathlib import Path

import dash
from dash import dcc, html, Input, Output
import plotly.express as px

DATA_LOCAL = Path('data/spacex_launches_clean.csv')
DATA_URL = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/labs/module_3/data/spacex_launch_dash.csv'

def load_data():
    # Prefer local cleaned CSV if available (richer columns)
    if DATA_LOCAL.exists():
        df = pd.read_csv(DATA_LOCAL)
        # Normalize to expected column names
        rename = {
            'LaunchSite': 'Launch Site',
            'PayloadMass': 'Payload Mass (kg)',
            'Class': 'class'
        }
        for k, v in rename.items():
            if k in df.columns and v not in df.columns:
                df[v] = df[k]
        # Coerce minimal required columns
        required = ['Launch Site', 'class', 'Payload Mass (kg)', 'Orbit']
        for col in required:
            if col not in df.columns:
                df[col] = np.nan
        return df[required].copy()

    # Fallback to IBM lab dataset
    df = pd.read_csv(DATA_URL)
    # Ensure expected columns exist
    if 'Payload Mass (kg)' not in df.columns and 'PayloadMass' in df.columns:
        df['Payload Mass (kg)'] = df['PayloadMass']
    return df

df = load_data().copy()
df['Payload Mass (kg)'] = pd.to_numeric(df['Payload Mass (kg)'], errors='coerce')
df['class'] = pd.to_numeric(df['class'], errors='coerce').fillna(0).astype(int)

# ---------------------
# App layout
# ---------------------
app = dash.Dash(__name__)
server = app.server

site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': s, 'value': s} for s in sorted(df['Launch Site'].dropna().unique())]

min_mass = int(np.nanmin(df['Payload Mass (kg)'])) if df['Payload Mass (kg)'].notna().any() else 0
max_mass = int(np.nanmax(df['Payload Mass (kg)'])) if df['Payload Mass (kg)'].notna().any() else 10000

app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center'}),

    # Dropdown for site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder='Select a Launch Site',
        searchable=True,
        style={'width': '60%', 'margin': '0 auto 20px auto'}
    ),

    # Pie chart
    dcc.Graph(id='success-pie-chart'),

    # Payload range slider
    html.Div([
        html.P('Payload Mass (kg):'),
        dcc.RangeSlider(
            id='payload-slider',
            min=min_mass, max=max_mass, step=100,
            value=[min_mass, max_mass],
            marks={
                min_mass: str(min_mass),
                max_mass: str(max_mass)
            }
        ),
    ], style={'width': '80%', 'margin': '20px auto'}),

    # Scatter chart
    dcc.Graph(id='success-payload-scatter-chart'),
], style={'fontFamily': 'Segoe UI, Roboto, Arial, sans-serif'})

# ---------------------
# Callbacks
# ---------------------
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # overall success counts
        counts = df['class'].value_counts().rename(index={0: 'Failure', 1: 'Success'})
        fig = px.pie(
            names=counts.index, values=counts.values,
            title='Overall Success vs Failure'
        )
    else:
        subset = df[df['Launch Site'] == selected_site]
        counts = subset['class'].value_counts().rename(index={0: 'Failure', 1: 'Success'})
        fig = px.pie(
            names=counts.index, values=counts.values,
            title=f'{selected_site}: Success vs Failure'
        )
    return fig

@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter(selected_site, payload_range):
    lo, hi = payload_range
    mask = (df['Payload Mass (kg)'] >= lo) & (df['Payload Mass (kg)'] <= hi)
    if selected_site != 'ALL':
        mask &= (df['Launch Site'] == selected_site)
    filtered = df[mask]

    # Use Orbit as color if available; otherwise color by class
    color_col = 'Orbit' if 'Orbit' in filtered.columns else 'class'
    fig = px.scatter(
        filtered,
        x='Payload Mass (kg)',
        y='class',
        color=color_col,
        hover_data=['Launch Site'] if 'Launch Site' in filtered.columns else None,
        title='Payload vs. Outcome (1=Success, 0=Failure)'
    )
    fig.update_yaxes(tickmode='array', tickvals=[0,1], ticktext=['Failure','Success'])
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)

# %%
