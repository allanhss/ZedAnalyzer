import dash
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets = external_stylesheets)


app.layout = html.Div([
    html.Div(children=[
        html.Div([
            html.Label('Char'),
            dcc.RadioItems(
                id = 'CharSelected',
                options= [''],
                value = '',
                labelStyle={'display': 'block'},
            ),
        ],style={'padding': 10}),
        html.Div([
            html.Label('Loot log'),
            dcc.Textarea(
                id='Lootlog',
                value = '##:## The following items dropped by ## are avaiable in your reward chest: a ##, an ##, ... (Boss Bonus)',
                style={'width': 300, 'height': 100},
            ),
            html.Br(),
            html.Button('Submit', id='loot-buttom', n_clicks=0),
        ],style={'display':'block', 'padding' : 10}),
    ], style={'display':'flex'}),
    html.Div(id='loot_result', style={'whiteSpace':'pre-line', 'padding':10}),
])

@app.callback(
    Output('loot_result', 'children'),
    Input('loot-buttom', 'n_clicks'),
    State('Lootlog', 'value'),
    State('CharSelected', 'value'),
)
def submite_loot(clicks, lootlog, charSelect):
    if clicks > 0:
        return '{} have looted: \n{}'.format(charSelect, lootlog)


if __name__ == '__main__':
    app.run_server(debug=True)
