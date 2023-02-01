import dash
from dash import Dash, html, dcc, dash_table
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
from tibiaRegex import GetLootfBoss, PutPriceInLootDf, OrderLootIndex, OrderLootByValue
import datetime

bosslog_csv = r'log\bosslog.csv'
bosspoints_csv = r'\log\bosspoints.csv'


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets = external_stylesheets)


app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label('Char'),
            dcc.RadioItems(
                id = 'CharSelected',
            ),
            dcc.Input(id= 'newChar', placeholder='New Char',type = 'text', size='sm'),
            html.Button(id = 'newChar-buttom', n_clicks = 1, children='Submit'),
        ],style={'padding': 10, 'display': 'block'}),

        html.Div([
            html.Label('Loot'),
            dcc.Textarea(
                id = 'Lootlog',
                placeholder=' ##:##(:##)? The following items dropped by ## are avaiable in your reward chest: # ##',
                style ={'width': 400, 'height' :100},
            ),
            html.Br(),
            html.Button(id = 'loot-buttom', n_clicks = 0, children='Submit'),
        ],style={'padding': 10, 'display': 'block'}),
    ], style={'display': 'flex', 'flex-direction': 'row'}),
    html.Br(),
    html.Div(id='loot_result', style={'whiteSpace':'pre-line', 'padding':10}),
])
 
@app.callback( #Atualiza a Output idependente de qualquer coisa
    Output('CharSelected','options'),
    Output('newChar','value'),
    Input('newChar-buttom', 'n_clicks'),
    State ('newChar', 'value'),
)
def update_char(n_clicks, name):
    try:
        names = list(set(pd.read_csv(r'log\bosslog.csv')['Char']))
        if str(name) != 'None':
            print (n_clicks, {'label': str(name), 'value': str(name)})
            names.append(name)
            return names, ''
        else:
            return names, ''
    except Exception as e:
        if 'file or directory' in e.args[1]:
            print(f'Char-update: No csv')
            if str(name) !='None':
                return [name]
            else:
                return ['New Character'], ''
        else:
            print(f'Char-update: {e.args}')


@app.callback(
    Output('CharSelected', 'value'),
    Input('CharSelected', 'options')
)
def update_nada(options):
    return options[-1]

@app.callback(
    Output('loot_result', 'children'),
    Output('Lootlog', 'value'),
    Input('loot-buttom', 'n_clicks'),
    State('Lootlog', 'value'),
    State('CharSelected', 'value'),
)
def submit_loot(clicks, lootlog, charSelect):
    if str(lootlog) != 'None':
        looted = GetLootfBoss(lootlog,[charSelect, 0 ]) #Corrigir Bosspoints
        try:
            loot = pd.concat ([pd.read_csv(bosslog_csv), looted], ignore_index=True)
            print('Loot Loaded')
            loot = PutPriceInLootDf(loot)
            print('Loot Priced')
            loot.to_csv(bosslog_csv, index = False)
            print('Loot Saved')
        except Exception as e:
            if 'file or directory' in e.args[1]:
                looted.to_csv(bosslog_csv)
                print(f'DfToCSV: Done')
            else:
                print(f'DfToCSV: {e.args}')
        
        time = datetime.datetime.now()
        loot = pd.read_csv(bosslog_csv)
        #Order the DataFrame by Item Value keeping the order sequence
        loot_show = loot[loot['Time'] == f'{time.day}/{time.month}/{time.year}'].loc[::-1]
        print("Today's Loot Loaded")
        loot_show = OrderLootByValue(loot_show)
        print("Today's Loot Values Ordered")
        return dash_table.DataTable(
            style_table={'overflowX': 'auto'},
            style_cell={
                'height': 'auto',
                # all three widths are needed
                'minWidth': '20px', 'width': '50', 'maxWidth': '70px',
                'whiteSpace': 'normal',
            },
            data =   loot_show.to_dict('records'),
            columns = [{"name": i, "id": i} for i in looted.columns],
        ), ''
    else:
        return "Today's loot log", ''

if __name__ == '__main__':
    app.run_server(debug=True)
