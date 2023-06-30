import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from elections import elections


# Create the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    html.Label('Year:'),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in elections['yr'].unique()],
        value=elections['yr'].unique()[0]
    ),
    
    html.Label('CST:'),
    dcc.Dropdown(
        id='cst-dropdown',
        options=[{'label': cst, 'value': cst} for cst in elections['cst'].unique()],
        value=elections['cst'].unique()[0]
    ),
    
    html.Div(id='output-list')
])

# Define the callback function
@app.callback(
    Output('output-list', 'children'),
    [Input('year-dropdown', 'value'),
     Input('cst-dropdown', 'value')]
)
def update_output_list(year, cst):
    filtered_data = elections[(elections['yr'] == year) & (elections['cst'] == cst)]
    values_cst_n =filtered_data['cst_n'].tolist()
    values_pvs1 = filtered_data['pvs1'].tolist()
    values_pty_n = filtered_data['pty_n'].tolist()
    values_mag = filtered_data['mag'].tolist()
    unique_values_pty_n = filtered_data['pty_n'].unique().tolist()

    output = html.Div([
        html.H3('Values for cst_n:'),
        html.Ul([html.Li(value) for value in values_cst_n]),

        html.H3('Unique values for pty_n:'),
        html.Ul([html.Li(value) for value in unique_values_pty_n]),
        
        html.H3('Values for pvs1:'),
        html.Ul([html.Li(value) for value in values_pvs1]),
        
        html.H3('Values for pty_n:'),
        html.Ul([html.Li(value) for value in values_pty_n]),
        
        html.H3('Values for mag:'),
        html.Ul([html.Li(value) for value in values_mag])
    ])
    
    return output

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)