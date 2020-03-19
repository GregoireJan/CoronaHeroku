# Dash application about losing streaks
# G. Jan - 03/20

# Libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import requests, zipfile, io, os
from datetime import datetime as dt
from datetime import timedelta 


# import tabula
# import PyPDF2
from tika import parser


import seaborn as sns
import matplotlib.pyplot as plt
import re
import wget
import os
import numpy as np

pd.options.mode.chained_assignment = None  # default='warn'

##################################################################################################################################################################################################

# Setting default
yesterday=(dt.today()- timedelta(days=1))

# CSS design
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Dash server
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Dash layout
app.layout = html.Div(children=[
    html.Br(),
    html.H1(
        children='Corona Virus in Norway',
        style=dict(display='flex', justifyContent='center')),
    html.Br(),
    html.Br(),
    # html.Div(children='Today', style={
    #     'textAlign': 'center'}),
    html.Div([
        html.Div(
            children=[dcc.DatePickerSingle(
                id='my-date-picker-single',
                min_date_allowed=dt(2020, 3, 1),
                max_date_allowed=dt.today(),
                initial_visible_month=dt(2020, 3, 1),
                date=yesterday.strftime('%Y-%m-%d'))],  # fill out your Input however you need
            style=dict(display='flex', justifyContent='center')
        )
    ]),
    # html.Div(id='df',style=dict(display='flex', justifyContent='center', color='green',fontsize='100px')),
    html.H2(children='Totalt tilfeller',style={'color':'black','font-weight': 'bold','font-size':'50px','textAlign': 'center'}),
    html.Div(id='df_tt',style={'color':'green','font-weight': 'bold','font-size':'50px','textAlign': 'center'}),
    html.H2(children='Nye tilfeller',style={'color':'black','font-weight': 'bold','font-size':'50px','textAlign': 'center'}),
    html.Div(id='df_nt',style={'color':'purple','font-weight': 'bold','font-size':'50px','textAlign': 'center'}),
    html.H2(children='Pasienter',style={'color':'black','font-weight': 'bold','font-size':'50px','textAlign': 'center'}),
    html.Div(id='df_p',style={'color':'orange','font-weight': 'bold','font-size':'50px','textAlign': 'center'}),
    html.H2(children='Dodsfall',style={'color':'black','font-weight': 'bold','font-size':'50px','textAlign': 'center'}),
    html.Div(id='df_d',style={'color':'red','font-weight': 'bold','font-size':'50px','textAlign': 'center'}),
    html.H2(children='Totalt testet',style={'color':'black','font-weight': 'bold','font-size':'50px','textAlign': 'center'}),
    html.Div(id='df_ttt',style={'color':'black','font-weight': 'bold','font-size':'50px','textAlign': 'center'}),
        # html.Div([
        #     dcc.DatePickerSingle(
        #         id='my-date-picker-single',
        #         min_date_allowed=dt(2020, 3, 1),
        #         max_date_allowed=dt(2020, 4, 1),
        #         initial_visible_month=dt(2020, 3, 1),
        #         date=dt.today().strftime('%Y-%m-%d')),
        # ], className="one columns"),

    # html.Div([
    #     html.Div([
    #         html.Button(id='submit-button', n_clicks=0, children='Submit',
    #             style={'color': 'white','background-color':'blue','margin':'10px 0px'})
    #     ], className="one columns"),
    #     html.Div([
    #         html.Div(id='fail',style={'color':'red','font-weight': 'bold','margin':'15px 0px', 'width': '150px'}),
    #     ], className="one columns"),
    # ], className="row"),

    # dcc.Graph(id='bar-graph',figure={'data': []},),
    html.Div([
        html.Div(children='by Gregoire Jan'),
        dcc.Link('https://gregoirejan.github.io/', href="https://gregoirejan.github.io/")
    ])
])

@app.callback(
    Output('df_tt', 'children'),
    [Input('my-date-picker-single', 'date')])
def output(date):
    return df.loc[date,'Totalt_Tilfeller'][0]

@app.callback(
    Output('df_nt', 'children'),
    [Input('my-date-picker-single', 'date')])
def output(date):
    return df.loc[date,'Nye_tilfeller'][0]

@app.callback(
    Output('df_p', 'children'),
    [Input('my-date-picker-single', 'date')])
def output(date):
    return df.loc[date,'Pasienter'][0]

@app.callback(
    Output('df_d', 'children'),
    [Input('my-date-picker-single', 'date')])
def output(date):
    return df.loc[date,'Dødsfall'][0]

@app.callback(
    Output('df_ttt', 'children'),
    [Input('my-date-picker-single', 'date')])
def output(date):
    return df.loc[date,'Totalt_testet'][0]

# Load data
files = [f for f in os.listdir('.') if f.endswith('.txt') and f.startswith('2020')]
df = pd.DataFrame (columns = ['Totalt_Tilfeller','Nye_tilfeller','Pasienter','Dødsfall','Totalt_testet'])
df_fylke = pd.DataFrame(columns = list(['Agder',
'Innlandet',
'Møre og Romsdal',
'Nordland',
'Oslo',
'Rogaland',
'Troms og Finnmark',
'Trøndelag',
'Vestfold og Telemark',
'Vestland',
'Viken']))
df_age = pd.DataFrame(columns = list(['0 – 9 år',
'10 – 19 år',
'20 -29 år',
'30 – 39 år',
'40 – 49 år',
'50 – 59 år',
'60 – 69 år',
'70 – 79 år',
'80 – 89 år',
'90 – 99 år']))

for f in files:
    print(f)
    # # Fylke
    # temp = tabula.read_txt('./'+f,pages='all')
    # try:
    #     df_fylke.loc[re.sub(r'.txt', '', f)]=list([item for item in temp if 'Fylke' in item][0]["Antall positive"])
    # except:
    #     df_fylke.loc[re.sub(r'.txt', '', f)]=[np.nan]*11
    # # Age
    # try:
    #     df_age.loc[re.sub(r'.txt', '', f)]=list([item for item in temp if 'Alder' in item][0]["Antall positive"])
    # except:
    #     df_age.loc[re.sub(r'.txt', '', f)]=[np.nan]*10
    # Text scraping
    raw = parser.from_file('./'+f)
    line = re.sub(r'(\d)\s+(\d)', r'\1\2', raw['content']).split("utbruddsregisteret",1)[1]
    try:
        ttilfeller=re.findall(r"(\d+) tilfeller", line)[0]
    except:
        ttilfeller=np.nan
    try:
        ntilfeller=re.findall(r"hvorav (\d+) tilfeller", line)[0]
    except:
        ntilfeller=np.nan
    try:
        pasienter=re.findall(r"(\d+) pasienter", line)[0]
    except:
        pasienter=np.nan
    try:
        dødsfall=re.findall(r"(\d+) dødsfall", line)[0]
    except:
        dødsfall=np.nan
    try:
        testet=re.findall(r"Totalt (\d+) er rapportert testet for Koronavirus ", line)[0]
    except:
        testet=np.nan
    data = {'Totalt_Tilfeller':  [ttilfeller],
        'Nye_tilfeller': [ntilfeller],
        'Pasienter': [pasienter],
        'Dødsfall': [dødsfall],
        'Totalt_testet': [testet],
        }
    df = df.append(pd.DataFrame (data, columns = ['Totalt_Tilfeller','Nye_tilfeller','Pasienter','Dødsfall','Totalt_testet']))
datetime_index = pd.DatetimeIndex([re.sub(r'.txt', '', f) for f in files])
df=df.set_index(datetime_index)

#################################################################################################################################################################################################

# Run dash server
if __name__ == '__main__':
    app.run_server(debug=True)

# # Callback to check for avaibility of input data after clicking the submit button
# @app.callback(
#     dash.dependencies.Output('fail', 'children'),
#     [dash.dependencies.Input('submit-button', 'n_clicks')],
#     [dash.dependencies.State('season', 'value'),
#     dash.dependencies.State('country', 'value'),
#     dash.dependencies.State('league', 'value')])

# # Display error message if not available
# def available(n_clicks, season, country,league):
#     try:
#         r = requests.get("http://www.football-data.co.uk/mmz4281/"+season+"/data.zip")
#         z = zipfile.ZipFile(io.BytesIO(r.content))
#         zip_filepath="."
#         if country in ["E","SC"]:
#             league=str(int(league)-1)
#         z.extract(country+league+'.csv', zip_filepath)
#         z.close()
#     except KeyError:
#         return '''Not available'''

# # Callback to update bar plot after clicking the submit button
# @app.callback(
#     dash.dependencies.Output('bar-graph', 'figure'),
#     [dash.dependencies.Input('submit-button', 'n_clicks')],
#     [dash.dependencies.State('season', 'value'),
#     dash.dependencies.State('country', 'value'),
#     dash.dependencies.State('league', 'value')])

# ####################################################################################################################################################################################################

# # Update bar plot with computed number of games lost when the opponent was on 2 games losing streak
# def update_graph(n_clicks, season, country,league):  
#     # Download data from football-data.co.uk
#     r = requests.get("http://www.football-data.co.uk/mmz4281/"+season+"/data.zip")
#     z = zipfile.ZipFile(io.BytesIO(r.content))
#     zip_filepath="."
#     if country in ["E","SC"]:
#         league=str(int(league)-1)
#     z.extract(country+league+'.csv', zip_filepath)
#     z.close()
#     df=pd.read_csv(country+league+'.csv',usecols=["HomeTeam","AwayTeam","FTR"])
#     os.remove(country+league+'.csv')

#     teams = {}
#     for team in df['HomeTeam'].unique():
#         if not pd.isnull(team):
#             teams[team] = df[(df['HomeTeam']==team) | (df['AwayTeam']==team)]

#     for team in teams:
#         # Initilize resulsts with -1 for a defeat
#         teams[team]["results"]=-1
#         j=1
#         for i in teams[team].index:
#             teams[team].loc[i,"matchday"]=j
#             # Results = 1 for a victory (home or away)
#             if (teams[team].loc[i,"FTR"]=="H") & (teams[team].loc[i,"HomeTeam"]==team):
#                 teams[team].loc[i,"results"]=1
#             if (teams[team].loc[i,"FTR"]=="A") & (teams[team].loc[i,"AwayTeam"]==team):
#                 teams[team].loc[i,"results"]=1
#             # Results = 0 for a draw
#             if teams[team].loc[i,"FTR"]=="D":
#                 teams[team].loc[i,"results"]=0
#             # Set flag whether team is at home or away
#             if teams[team].loc[i,"HomeTeam"]==team:
#                 teams[team].loc[i,"homeaway"]="home"
#             else:
#                 teams[team].loc[i,"homeaway"]="away"
#             j+=1

#     for team in teams:
#         teams[team]=teams[team].reset_index(drop=True)
#         # After the 3rd match day sum the previous results of the 2 games from the opponent 
#         for i in teams[team].index:
#             if teams[team].loc[i,"matchday"] > 3:
#                 if teams[team].loc[i,"homeaway"]=="home":
#                     teams[team].loc[i,"resultsop"]=sum(teams[teams[team].loc[i,"AwayTeam"]]["results"][int(teams[team].loc[i,"matchday"])-3:int(teams[team].loc[i,"matchday"])-1])
#                 if teams[team].loc[i,"homeaway"]=="away":
#                     teams[team].loc[i,"resultsop"]=sum(teams[teams[team].loc[i,"HomeTeam"]]["results"][int(teams[team].loc[i,"matchday"])-3:int(teams[team].loc[i,"matchday"])-1])
#                 # if the game is lost and the opponent has at least lost its 2 previous games hen the flag is 1 - otherwise 0
#                 if (teams[team].loc[i,"resultsop"] < -1) & (teams[team].loc[i,"results"]==-1):
#                     teams[team].loc[i,"relance"]=1
#                 else:
#                     teams[team].loc[i,"relance"]=0

#     relancesum={}
#     # For each team sum the flags = number of games lost when the opponent was on a 2 games losing streak
#     for team in teams:
#         relancesum[team]=teams[team]["relance"].sum()
#     relancesum= pd.DataFrame(sorted(relancesum.items(), key=lambda kv: kv[1],reverse = True))
#     relancesum.columns=["Team","Relance games"]

#     # Plot bar plot
#     return go.Figure(data=[
#         go.Bar(
#             x=list(relancesum["Team"]),
#             y=list(relancesum["Relance games"])
#         )],
#         layout=go.Layout(xaxis={'title':'Teams'}, yaxis={'title':'Number of games'})
#     )

    
    
