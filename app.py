# Dash application about losing streaks
# G. Jan - 12/18

# Libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import requests, zipfile, io, os
pd.options.mode.chained_assignment = None  # default='warn'

##################################################################################################################################################################################################

# CSS design
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Dash server
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Dash layout
app.layout = html.Div(children=[
    html.H1(
        children='Corona Virus in Norway',
        style={
            'textAlign': 'center'}),
    html.Br(),
    html.Br(),
    html.Div(children='Today', style={
        'textAlign': 'center'}),
    html.Div([
        html.Div([
            dcc.Dropdown(id='Date',
                options=[
                    {'label': u'Today', 'value': '9999'},
                    {'label': 'Yesterday', 'value': '99999'},
                ],
                placeholder="Select date",
                style={'margin':'10px 0px', 'width': '150px'}),
        ], className="one columns"),
    ], className="row"),

    html.Div([
        html.Div([
            html.Button(id='submit-button', n_clicks=0, children='Submit',
                style={'color': 'white','background-color':'blue','margin':'10px 0px'})
        ], className="one columns"),
        html.Div([
            html.Div(id='fail',style={'color':'red','font-weight': 'bold','margin':'15px 0px', 'width': '150px'}),
        ], className="one columns"),
    ], className="row"),

    # dcc.Graph(id='bar-graph',figure={'data': []},),
    html.Div([
        html.Div(children='by Gregoire Jan'),
        dcc.Link('https://gregoirejan.github.io/', href="https://gregoirejan.github.io/")
    ])
])

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
#################################################################################################################################################################################################

# Run dash server
if __name__ == '__main__':
    app.run_server(debug=True)
    
    
    
    
