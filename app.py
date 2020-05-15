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
import pycountry


pd.options.mode.chained_assignment = None  # default='warn'


######################################################################################
# Load data
files = [
    f for f in os.listdir("./Data/") if f.endswith(".txt") and f.startswith("2020")
]
# Dataframe columns name
df = pd.DataFrame(
    columns=["Totalt_Tilfeller", "Nye_tilfeller", "Dødsfall", "Totalt_testet",]
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

# Scrap through daily files from FHI
for ff in sorted(files):
    print(ff)
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
    #####
    # Text scraping
    f = open("./Data/" + ff, "r")
    raw = f.read()
    line = re.sub(r"(\d)\s+(\d)", r"\1\2", raw)
    # Get total cases
    if dt.strptime(re.sub(".txt", "", ff), "%Y-%m-%d") > dt(2020, 3, 25):
        try:
            line1 = re.search("(.*)personer", line).group(1)
            ttilfeller = re.findall(r"(\d+)", line1)[0]
        except:
            ttilfeller = np.nan
        try:
            ntilfeller = str(int(ttilfeller) - int(df["Totalt_Tilfeller"][-1:][0]))
        except:
            ntilfeller = np.nan
    else:
        # Get new cases
        try:
            line1 = re.search("otalt(.*)hvorav", line).group(1)
            ttilfeller = re.findall(r"(\d+)", line1)[0]
        except:
            ttilfeller = np.nan
        try:
            ntilfeller = re.findall(r"hvorav (\d+)", line)[0]
        except:
            ntilfeller = np.nan
    try:
        dødsfall = re.findall(r"(\d+) dødsfall", line)[0]
    except:
        dødsfall = np.nan
    # Get total tested
    try:
        line1 = re.search("otalt(.*)testet", line).group(1)
        testet = re.findall(r"(\d+)", line1)[0]
    except:
        testet = np.nan
    ###############
    # Append dataframe df
    data = {
        "Totalt_Tilfeller": [ttilfeller],
        "Nye_tilfeller": [ntilfeller],
        "Dødsfall": [dødsfall],
        "Totalt_testet": [testet],
    }
    df = df.append(
        pd.DataFrame(
            data,
            columns=["Totalt_Tilfeller", "Nye_tilfeller", "Dødsfall", "Totalt_testet",],
        )
    )
# Get timestamp index for df
datetime_index = pd.DatetimeIndex([re.sub(r".txt", "", f) for f in sorted(files)])
df = df.set_index(datetime_index)

# Retreive patients from Helsedirektorat csv
df_pasienter = pd.read_csv("./Data/data.csv")
df["Pasienter"] = df_pasienter["Innlagte med påvist covid-19"][1:].values

###################################################################################
### Time Series from John Hopkins

#Load population (fix country names in datpop notebook)
pop = pd.read_csv("./Data/population.csv")

# Load
df_tsdeath = pd.read_csv("Data/time_series_covid19_deaths_global.csv")
# Group by contry and transpose
df_tsdeath = df_tsdeath.groupby("Country/Region").sum().rename(index={'Burma':'Myanmar','Korea, South':'Republic of Korea','Laos':'Lao','Taiwan*':'Taiwan','Congo (Brazzaville)':'Republic of the Congo','Congo (Kinshasa)':'Congo, The Democratic Republic of the','West Bank and Gaza':'Palestine, State of'}).reset_index().T[:-1]
# Fix column name
df_tsdeath.columns = df_tsdeath.iloc[0, :]
df_tsdeath = df_tsdeath[3:]
# Get timestamp index
datetime_index = pd.DatetimeIndex(df_tsdeath.index)
df_tsdeath = df_tsdeath.set_index(datetime_index)

df_daysdeath = df_tsdeath.copy()
# Threshold deaths
n = 0
for col in df_daysdeath.columns:
    if df_daysdeath[col].max() > n:
        firsdeath = df_daysdeath.index[df_daysdeath[col] > n][0]
        df_daysdeath[col] = df_daysdeath[col].shift(-(firsdeath - dt(2020, 1, 22)).days)
        # Get ratio per million inhabitant 
        try:
            df_daysdeath[col] = 1000000*(df_daysdeath[col] / pop[pop['Country/Region']==col]['Pop'].values)
        except:
            #print(col)
            df_daysdeath[col] = [np.nan]*len(df_daysdeath[col])
# Reset index
df_daysdeath = df_daysdeath.reset_index().drop(columns="index")
df_daysdeath.index.names = ["Days"]
# Ratio=0 for day 0
df_daysdeath.iloc[0, :] = 1

# Same as above for confirmed cases
df_tsconf = pd.read_csv("Data/time_series_covid19_confirmed_global.csv")
df_tsconf = df_tsconf.groupby("Country/Region").sum().rename(index={'Burma':'Myanmar','Korea, South':'Republic of Korea','Laos':'Lao','Taiwan*':'Taiwan','Congo (Brazzaville)':'Republic of the Congo','Congo (Kinshasa)':'Congo, The Democratic Republic of the','West Bank and Gaza':'Palestine, State of'}).reset_index().T[:-1]
df_tsconf.columns = df_tsconf.iloc[0, :]
df_tsconf = df_tsconf[3:]
datetime_index = pd.DatetimeIndex(df_tsconf.index)
df_tsconf = df_tsconf.set_index(datetime_index)

df_daysconf = df_tsconf.copy()
# Threshold conf
n = 50
for col in df_daysconf.columns:
    if df_daysconf[col].max() > n:
        firsconf = df_daysconf.index[df_daysconf[col] > n][0]
        df_daysconf[col] = df_daysconf[col].shift(-(firsconf - dt(2020, 1, 22)).days)
        #df_daysconf[col] = df_daysconf[col] / (df_daysconf[col][0])
        # Get ratio per million inhabitant 
        try:
            df_daysconf[col] = 1000000*(df_daysconf[col] / pop[pop['Country/Region']==col]['Pop'].values)
        except:
            df_daysconf[col] = [np.nan]*len(df_daysconf[col])

df_daysconf = df_daysconf.reset_index().drop(columns="index")
df_daysconf.index.names = ["Days"]
df_daysconf.iloc[0, :] = 1

def convert_options(optionlabels, optionvals):
    return [
        dict(label=x, value=y)
        for x, y in zip(optionlabels, optionvals)
        if x != "Sweden"
    ]


##################################################################################################################################################################################################
# DASH

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
                    [
                        dbc.Col(
                            dbc.NavbarBrand(
                                "COVID-19 IN NORWAY",
                                className="mb-0 h1",
                                style={"font-size": "30px"},
                            )
                        ),
                        # SUPER UGLY
                        dbc.Col(),
                        dbc.Col(),
                        dbc.Col(),
                        dbc.Col(),
                        dbc.Col(),
                        dbc.Col(),
                        dbc.Col(),
                        dbc.Col(),
                        dbc.Col(),
                        dbc.Col(
                            [
                                html.Div(
                                    children="by Gregoire Jan",
                                    style={
                                        "color": "white",
                                        # "font-weight": "bold",
                                        "font-size": "10px",
                                        "textAlign": "center",
                                    },
                                ),
                                html.A(
                                    "https://gregoirejan.github.io/",
                                    href="https://gregoirejan.github.io/",
                                    target="_blank",
                                ),
                            ]
                        ),
                    ],
                    align="center",
                    no_gutters=True,
                    className="col-12",
                ),
            ],
            color="dark",
            dark=True,
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2(
                            children="Select date",
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
                            ],
                            style={
                                "font-size": "20px",
                                "font-weight": "bold",
                                "textAlign": "center",
                            },
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H2(
                            children="Total cases",
                            style={
                                "color": "black",
                                "font-size": "30px",
                                "textAlign": "center",
                            },
                        ),
                        html.Div(
                            id="df_tt",
                            style={
                                "color": "MediumAquaMarine",
                                "font-weight": "bold",
                                "font-size": "30px",
                                "textAlign": "center",
                            },
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H2(
                            children="New cases",
                            style={
                                "color": "black",
                                "font-size": "30px",
                                "textAlign": "center",
                            },
                        ),
                        html.Div(
                            id="df_nt",
                            style={
                                "color": "SteelBlue",
                                "font-weight": "bold",
                                "font-size": "30px",
                                "textAlign": "center",
                            },
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H2(
                            children="Patients hospitalized",
                            style={
                                "color": "black",
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
                    ]
                ),
                dbc.Col(
                    [
                        html.H2(
                            children="Deaths",
                            style={
                                "color": "black",
                                "font-size": "30px",
                                "textAlign": "center",
                            },
                        ),
                        html.Div(
                            id="df_d",
                            style={
                                "color": "Crimson",
                                "font-weight": "bold",
                                "font-size": "30px",
                                "textAlign": "center",
                            },
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H2(
                            children="Total Corona tested",
                            style={
                                "color": "black",
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
                    ]
                ),
            ],
            style={"border": "50px solid", "color": "white"},
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div([dcc.Graph(id="bar-graph", figure={"data": []},)]),
                        html.Div([dcc.Graph(id="bar-graph2", figure={"data": []},)]),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Alert(
                            "Comparing Growth Rate for Total Cases is highly depend on how each country test its inhabitants",
                            color="danger",
                            is_open=True,
                            duration=10000,
                            style={"textAlign": "center","font-size": "10px",},
                        ),
                        dbc.Row([
                            dbc.Col(
                            dcc.Dropdown(
                                id="country",
                                value="Norway",
                                options=convert_options(
                                    df_daysconf.columns, df_daysconf.columns
                                ),
                                placeholder="Select a country to compare to Norway",
                                style={
                                    "font-size": "20px",
                                    "font-weight": "bold",
                                    "textAlign": "center",
                                },
                            )),
                            dbc.Col(
                            dcc.Dropdown(
                                id="country2",
                                value="Sweden",
                                options=convert_options(
                                    df_daysconf.columns, df_daysconf.columns
                                ),
                                placeholder="Select a country to compare to",
                                style={
                                    "font-size": "20px",
                                    "font-weight": "bold",
                                    "textAlign": "center",
                                },
                            )),]
                        ),
                        # html.Div(
                        #     dcc.Dropdown(
                        #         id="country2",
                        #         value="Sweden",
                        #         options=convert_options(
                        #             df_daysconf.columns, df_daysconf.columns
                        #         ),
                        #         placeholder="Select a country to compare to",
                        #         style={
                        #             "font-size": "20px",
                        #             "font-weight": "bold",
                        #             "textAlign": "center",
                        #         },
                        #     ),
                        # ),
                        html.Div([dcc.Graph(id="scatter-graph", figure={"data": []},)]),
                        html.Div(
                            [dcc.Graph(id="scatter-graph2", figure={"data": []},)]
                        ),
                    ],
                    align="center",
                ),
            ]
        ),
        html.Footer(
            children=["© 2020 Copyright / Data from FHI & John Hopkins University"],
            style={"textAlign": "center"},
        ),
    ]
)


@app.callback(Output("df_tt", "children"), [Input("my-date-picker-single", "date")])
def outputtt(date):
    try:
        daybefore = dt.strptime(date, "%Y-%m-%d") - timedelta(days=1)
        if int(df.loc[date, "Totalt_Tilfeller"]) > int(
            df.loc[daybefore, "Totalt_Tilfeller"]
        ):
            arrow = " \u2B09"
        elif int(df.loc[date, "Totalt_Tilfeller"]) < int(
            df.loc[daybefore, "Totalt_Tilfeller"]
        ):
            arrow = " \u2B0A"
        else:
            arrow = " \uFF1D"
        return df.loc[date, "Totalt_Tilfeller"] + arrow
    except:
        return "NA"


@app.callback(Output("df_nt", "children"), [Input("my-date-picker-single", "date")])
def outputnt(date):
    try:
        daybefore = dt.strptime(date, "%Y-%m-%d") - timedelta(days=1)
        if int(df.loc[date, "Nye_tilfeller"]) > int(df.loc[daybefore, "Nye_tilfeller"]):
            arrow = " \u2B09"
        elif int(df.loc[date, "Nye_tilfeller"]) < int(
            df.loc[daybefore, "Nye_tilfeller"]
        ):
            arrow = " \u2B0A"
        else:
            arrow = " \uFF1D"
        return df.loc[date, "Nye_tilfeller"] + arrow
    except:
        return "NA"


@app.callback(Output("df_p", "children"), [Input("my-date-picker-single", "date")])
def outputp(date):
    try:
        daybefore = dt.strptime(date, "%Y-%m-%d") - timedelta(days=1)
        if int(df.loc[date, "Pasienter"]) > int(df.loc[daybefore, "Pasienter"]):
            arrow = " \u2B09"
        elif int(df.loc[date, "Pasienter"]) < int(df.loc[daybefore, "Pasienter"]):
            arrow = " \u2B0A"
        else:
            arrow = " \uFF1D"
        return str(df.loc[date, "Pasienter"]) + arrow
    except:
        return "NA"


@app.callback(Output("df_d", "children"), [Input("my-date-picker-single", "date")])
def outputd(date):
    try:
        daybefore = dt.strptime(date, "%Y-%m-%d") - timedelta(days=1)
        if int(df.loc[date, "Dødsfall"]) > int(df.loc[daybefore, "Dødsfall"]):
            arrow = " \u2B09"
        elif int(df.loc[date, "Dødsfall"]) < int(df.loc[daybefore, "Dødsfall"]):
            arrow = " \u2B0A"
        else:
            arrow = " \uFF1D"
        return df.loc[date, "Dødsfall"] + arrow
    except:
        return "NA"


@app.callback(Output("df_ttt", "children"), [Input("my-date-picker-single", "date")])
def outputttt(date):
    try:
        daybefore = dt.strptime(date, "%Y-%m-%d") - timedelta(days=1)
        if int(df.loc[date, "Totalt_testet"]) > int(df.loc[daybefore, "Totalt_testet"]):
            arrow = " \u2B09"
        elif int(df.loc[date, "Totalt_testet"]) < int(
            df.loc[daybefore, "Totalt_testet"]
        ):
            arrow = " \u2B0A"
        else:
            arrow = " \uFF1D"
        return df.loc[date, "Totalt_testet"] + arrow
    except:
        return "NA"


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
                marker={"color": "MediumAquaMarine"},
            )
        ],
        layout=go.Layout(
            title={"text": "Total cases", "font": {"size": 30}, "x": 0.5},
            xaxis={
                "title": "",
                "range": [dt(2020, 3, 1), dt(2020, 5, 30)],
                "tickangle":45
            },
            yaxis={"title": "Total cases"},
            plot_bgcolor="rgb(255,255,255)",
        ),
    )


@app.callback(
    dash.dependencies.Output("bar-graph2", "figure"),
    [Input("my-date-picker-single", "date")],
)
def barplot2(date):
    return go.Figure(
        data=[
            go.Bar(
                x=list(df.index),
                y=list(df["Nye_tilfeller"]),
                marker={"color": "SteelBlue"},
            )
        ],
        layout=go.Layout(
            title={"text": "New cases", "font": {"size": 30}, "x": 0.5},
            xaxis={
                "title": "",
                "range": [dt(2020, 3, 1), dt(2020, 5, 30)],
                "tickangle":45
            },
            yaxis={"title": "New cases"},
            plot_bgcolor="rgb(255,255,255)",
        ),
    )


@app.callback(
    dash.dependencies.Output("scatter-graph", "figure"), [Input("country", "value"),Input("country2", "value")],
)
def scatter(country,country2):
    return go.Figure(
        data=[
            go.Scatter(
                x=list(df_daysconf.index.values),
                y=list(df_daysconf[country2].values),
                mode="markers",
                name=country2,
            ),
            go.Scatter(
                x=list(df_daysconf.index.values),
                y=list(df_daysconf[country].values),
                mode="markers",
                name=country,
            ),
        ],
        layout=go.Layout(
            title={
                "text": "Total Cases \n(per million inhabitants)",
                "font": {"size": 30},
                "x": 0.5,
            },
            xaxis={"title": "Days", "range": [-1, 90],"tickangle":45},
            yaxis={"title": "Total Cases per million"},
            plot_bgcolor="rgb(255,255,255)",
            annotations=[
                go.layout.Annotation(
                    text="Day 0 = first day to reach 50 total cases",
                    align="center",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=1.15,
                )
            ],
        ),
    )


@app.callback(
    dash.dependencies.Output("scatter-graph2", "figure"), [Input("country", "value"),Input("country2", "value")],
)
def scatter2(country,country2):
    return go.Figure(
        data=[
            go.Scatter(
                x=list(df_daysdeath.index.values),
                y=list(df_daysdeath[country2].values),
                mode="markers",
                name=country2,
            ),
            go.Scatter(
                x=list(df_daysdeath.index.values),
                y=list(df_daysdeath[country].values),
                mode="markers",
                name=country,
            ),
        ],
        layout=go.Layout(
            title={"text": "Deaths \n(per million inhabitants)", "font": {"size": 30}, "x": 0.5,},
            xaxis={"title": "Days", "range": [-1, 90],"tickangle":45},
            yaxis={"title": "Deaths per million"},
            plot_bgcolor="rgb(255,255,255)",
            annotations=[
                go.layout.Annotation(
                    text="Day 0 = first death",
                    align="center",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=1.15,
                )
            ],
        ),
    )


#################################################################################################################################################################################################

# Run dash server
if __name__ == "__main__":
    app.run_server(debug=True)
