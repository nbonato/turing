# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
import sys

from elections import elections_replaced
from press_directories_cleaner import cleaned_press_directories




df = cleaned_press_directories.copy()


## Dash App starts below

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Label('Select Year:'),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': str(year), 'value': year} for year in sorted(df['year'].unique())],
        clearable=False
    ),
    html.Label('Select County:'),
    dcc.Dropdown(
        id='county-dropdown',
        options=[{'label': county, 'value': county} for county in sorted(df['county'].unique())],
        clearable=False
    ),
    html.Div(id='output')
])

@app.callback(
    Output('output', 'children'),
    [Input('year-dropdown', 'value'), Input('county-dropdown', 'value')]
)
def update_output(year, county):
    if year is None or county is None:
        raise PreventUpdate

    filtered_df = df[(df['year'] == year) & (df['county'] == county)]

    total_count = len(filtered_df)
    nan_count = filtered_df['S-POL'].isna().sum()
    nan_percentage = nan_count / total_count * 100

    value_counts = filtered_df['S-POL'].value_counts()
    threshold = total_count * 0.01

    value_counts_freq_gt_threshold = value_counts[value_counts > threshold]
    value_counts_freq_le_threshold = value_counts[value_counts <= threshold]
    other_count = value_counts_freq_le_threshold.sum()
    other_percentage = other_count / total_count * 100

    labels = ['NaN S-POL'] + list(value_counts_freq_gt_threshold.index) + ['Other']
    counts = [nan_count] + list(value_counts_freq_gt_threshold.values) + [other_count]

    fig = go.Figure(data=[go.Pie(labels=labels, values=counts, hole=0.5)])

    chart_div = dcc.Graph(figure=fig)

    rows = []

    rows.append(html.Div([
        html.Strong('NaN S-POL:'),
        html.Span(f"{nan_count} ({nan_percentage:.2f}%)")
    ]))

    for value, count in value_counts_freq_gt_threshold.items():
        percentage = count / total_count * 100
        rows.append(html.Div([
            html.Strong(f"S-POL '{value}':"),
            html.Span(f"{count} ({percentage:.2f}%)")
        ]))

    if other_count > 0:
        rows.append(html.Div([
            html.Strong('Other (S-POL frequency <= threshold):'),
            html.Span(f"{other_count} ({other_percentage:.2f}%)")
        ]))

    rows.append(html.Hr())
    rows.append(chart_div)

    rows.append(html.Hr())

    for _, row in filtered_df.iterrows():
        rows.append(html.Div([
            html.Strong('S-TITLE:'),
            html.Span(row['S-TITLE']),
            html.Strong('S-POL:'),
            html.Span(row['S-POL']),
            html.Hr()
        ]))

    return rows

if __name__ == '__main__':
    app.run_server(debug=True)