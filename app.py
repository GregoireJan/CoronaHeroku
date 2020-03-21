# Dash application about losing streaks
# G. Jan - 03/20

# Libraries
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import requests, zipfile, io, os
from datetime import datetime as dt
from datetime import timedelta

import seaborn as sns
import matplotlib.pyplot as plt
import re
import wget
import os
import numpy as np

pd.options.mode.chained_assignment = None  # default='warn'

##################################################################################################################################################################################################

# Setting default
yesterday = dt.today() - timedelta(days=1)

# CSS design
external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    dbc.themes.BOOTSTRAP,
]

# Dash server
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Dash layout
app.layout = html.Div(
    [
        dbc.Navbar(
            [
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [dbc.Col(dbc.NavbarBrand("COVID-19 IN NORWAY", className="mb-0 h1",style={"font-size":"30px"})),],
                    align="center",
                    no_gutters=True,
                ),
            ],
            color="dark",
            dark=True,
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H2(
                                children="Change date below",
                                style={
                                    "color": "grey",
                                    # "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                            html.Div(
                                children=[
                                    dcc.DatePickerSingle(
                                        id="my-date-picker-single",
                                        min_date_allowed=dt(2020, 3, 1),
                                        max_date_allowed=dt.today(),
                                        initial_visible_month=dt(2020, 3, 1),
                                        date=yesterday.strftime("%Y-%m-%d"),
                                    )
                                ],  # fill out your Input however you need
                                # style=dict(display="flex", justifyContent="center"),
                                style={
                                    "font-size": "20px",
                                    "font-weight": "bold",
                                    "textAlign": "center",
                                },
                            ),
                            html.Br(),
                            html.Br(),
                            html.Br(),
                            html.Br(),
                            html.Br(),
                            html.H2(
                                children="Total cases",
                                style={
                                    "color": "black",
                                    # "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                            html.Div(
                                id="df_tt",
                                style={
                                    "color": "LightSlateGrey",
                                    "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                            html.H2(
                                children="New cases",
                                style={
                                    "color": "black",
                                    # "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                            html.Div(
                                id="df_nt",
                                style={
                                    "color": "LightSlateGrey",
                                    "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                            html.H2(
                                children="Patients hospitalized",
                                style={
                                    "color": "black",
                                    # "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                            html.Div(
                                id="df_p",
                                style={
                                    "color": "LightSlateGrey",
                                    "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                            html.H2(
                                children="Deaths",
                                style={
                                    "color": "black",
                                    # "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                            html.Div(
                                id="df_d",
                                style={
                                    "color": "LightSlateGrey",
                                    "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                            html.H2(
                                children="Total Corona tested",
                                style={
                                    "color": "black",
                                    # "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                            html.Div(
                                id="df_ttt",
                                style={
                                    "color": "LightSlateGrey",
                                    "font-weight": "bold",
                                    "font-size": "30px",
                                    "textAlign": "center",
                                },
                            ),
                        ],
                    ),
                    width=3,
                    align="center",
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.Div([dcc.Graph(id="bar-graph", figure={"data": []},)]),
                            html.Div(
                                [dcc.Graph(id="bar-graph2", figure={"data": []},)]
                            ),
                        ]
                    ),
                    width=9,
                ),
            ]
        ),
    ]
)


@app.callback(Output("df_tt", "children"), [Input("my-date-picker-single", "date")])
def output(date):
    return df.loc[date, "Totalt_Tilfeller"]


@app.callback(Output("df_nt", "children"), [Input("my-date-picker-single", "date")])
def output(date):
    return df.loc[date, "Nye_tilfeller"]


@app.callback(Output("df_p", "children"), [Input("my-date-picker-single", "date")])
def output(date):
    return df.loc[date, "Pasienter"]


@app.callback(Output("df_d", "children"), [Input("my-date-picker-single", "date")])
def output(date):
    return df.loc[date, "Dødsfall"]


@app.callback(Output("df_ttt", "children"), [Input("my-date-picker-single", "date")])
def output(date):
    return df.loc[date, "Totalt_testet"]


@app.callback(
    dash.dependencies.Output("bar-graph", "figure"),
    [Input("my-date-picker-single", "date")],
)
def barplot(date):
    return go.Figure(
        data=[
            go.Bar(
                x=list(df.index),
                y=list(df["Totalt_Tilfeller"]),
                marker={"color": "DarkOliveGreen"},
            )
        ],
        layout=go.Layout(
            title={"text": "Total cases", "font": {"size": 30}, "x": 0.5},
            xaxis={
                "title": "",
                "range": [dt(2020, 3, 1), dt(2020, 4, 1)],
                "tickmode": "linear",
            },
            yaxis={"title": "Total cases"},
            plot_bgcolor="rgb(255,255,255)",
        ),
    )


@app.callback(
    dash.dependencies.Output("bar-graph2", "figure"),
    [Input("my-date-picker-single", "date")],
)
def barplot(date):
    return go.Figure(
        data=[
            go.Bar(
                x=list(df.index),
                y=list(df["Nye_tilfeller"]),
                marker={"color": "DarkOliveGreen"},
            )
        ],
        layout=go.Layout(
            title={"text": "New cases", "font": {"size": 30}, "x": 0.5},
            xaxis={
                "title": "",
                "range": [dt(2020, 3, 1), dt(2020, 4, 1)],
                "tickmode": "linear",
            },
            yaxis={"title": "New cases"},
            plot_bgcolor="rgb(255,255,255)",
        ),
    )


######################################################################################
# Load data
files = [f for f in os.listdir(".") if f.endswith(".txt") and f.startswith("2020")]
df = pd.DataFrame(
    columns=[
        "Totalt_Tilfeller",
        "Nye_tilfeller",
        "Pasienter",
        "Dødsfall",
        "Totalt_testet",
    ]
)
df_fylke = pd.DataFrame(
    columns=list(
        [
            "Agder",
            "Innlandet",
            "Møre og Romsdal",
            "Nordland",
            "Oslo",
            "Rogaland",
            "Troms og Finnmark",
            "Trøndelag",
            "Vestfold og Telemark",
            "Vestland",
            "Viken",
        ]
    )
)
df_age = pd.DataFrame(
    columns=list(
        [
            "0 – 9 år",
            "10 – 19 år",
            "20 -29 år",
            "30 – 39 år",
            "40 – 49 år",
            "50 – 59 år",
            "60 – 69 år",
            "70 – 79 år",
            "80 – 89 år",
            "90 – 99 år",
        ]
    )
)

for f in sorted(files):
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
    f = open("./" + f, "r")
    raw = f.read()
    line = re.sub(r"(\d)\s+(\d)", r"\1\2", raw).split("utbruddsregisteret", 1)[1]
    # if f == '2020-03-16.txt':
    # print(line.split("Fylker",1)[1][50:750])
    # try:
    #     one=line.split("Fylker",1)[1][50:750]
    #     df_fylke.loc[re.sub(r'.txt', '', f)]=list([item for item in one.split()[:40] if item.isdigit()])
    # except:
    #     df_fylke.loc[re.sub(r'.txt', '', f)]=[np.nan]*11
    try:
        ttilfeller = re.findall(r"(\d+) tilfeller", line)[0]
    except:
        ttilfeller = np.nan
    try:
        ntilfeller = re.findall(r"hvorav (\d+) tilfeller", line)[0]
    except:
        ntilfeller = np.nan
    try:
        pasienter = re.findall(r"(\d+) pasienter", line)[0]
    except:
        pasienter = np.nan
    try:
        dødsfall = re.findall(r"(\d+) dødsfall", line)[0]
    except:
        dødsfall = np.nan
    try:
        testet = re.findall(
            r"Totalt (\d+) er rapportert testet for Koronavirus ", line
        )[0]
    except:
        testet = np.nan
    data = {
        "Totalt_Tilfeller": [ttilfeller],
        "Nye_tilfeller": [ntilfeller],
        "Pasienter": [pasienter],
        "Dødsfall": [dødsfall],
        "Totalt_testet": [testet],
    }
    df = df.append(
        pd.DataFrame(
            data,
            columns=[
                "Totalt_Tilfeller",
                "Nye_tilfeller",
                "Pasienter",
                "Dødsfall",
                "Totalt_testet",
            ],
        )
    )
datetime_index = pd.DatetimeIndex([re.sub(r".txt", "", f) for f in sorted(files)])
df = df.set_index(datetime_index)
print(df.index.values)

#################################################################################################################################################################################################

# Run dash server
if __name__ == "__main__":
    app.run_server(debug=True)
