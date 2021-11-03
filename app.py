from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import dash
import json
import pandas as pd
import plotly
import plotly.express as px
from dash import html
from dash import dcc


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# loading data
df = pd.read_csv("./data/clean_data.csv")

# loding json
map_edi_geo = json.load(open("./data/eh.geojson", "r"))

# data manipulation edinburgh only postcodes
df_edi = df[df.post_code.str.contains("EH")]
median_edi_post_code = df_edi.groupby(["post_code", "beds"])[
    "price"].agg(["count", "median", "min", "max", "mean"]).reset_index()
median_edi_post_code.rename(columns={"post_code": "name"}, inplace=True)
median_edi_post_code.name = median_edi_post_code.name.str.strip()


# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "13rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content.
CONTENT_STYLE = {
    "margin-left": "13rem",
    "margin-right": "0rem",
    "padding": "0rem 0rem",
    "width": "65rem",
    "height": "150rem",
    "border": "black 1px solid"
}
# sidebar html
sidebar = dbc.Container(
    [html.H2("EHPrices", className="display-6"), html.Hr(),
     html.P("Number of bedrooms", className="lead"),

        html.Div(dbc.Checklist(id='bedrooms',
                               options=[{'label': '1 bedroom', 'value': 1},
                                        {'label': '2 bedrooms', 'value': 2},
                                        {'label': '3 bedrooms', 'value': 3},
                                        {'label': '4 bedrooms', 'value': 4},
                                        {'label': '5 bedrooms', 'value': 5}

                                        ], value=[2, 3]), className="nav"),
     html.Hr(),
     dbc.Button("Reset map", id="reset_map", color="success", className="me-1")], style=SIDEBAR_STYLE, )
# content elements
# Cards
min_card = dbc.Card(
    dbc.CardBody(
        [html.H4("Price min"),
            html.H5(id="cards_min", className="card-title"),
         ], className="shadow-lg")
)
max_card = dbc.Card(
    dbc.CardBody(
        [html.H4("Max price"),
            html.H5(id="cards_max", className="card-title"),
         ], className="shadow-lg")
)
count_card = dbc.Card(
    dbc.CardBody(
        [html.H4("No. properties"),
            html.H5(id="price_count", className="card-title "),
         ], className="shadow-lg"),
)
median_card = dbc.Card(
    dbc.CardBody([
        html.H4("Median price"),
        html.H5(id="cards_median", className="card-title active")
    ], className="shadow-lg")
)
# _____________end of Cards_____________


# Row start_______________________________
row = dbc.Container(
    dbc.Row([
        dbc.Col(count_card, width=3),
        dbc.Col(min_card, width=3),
        dbc.Col(max_card, width=3),
        dbc.Col(median_card, width=3),
    ], justify="center")
)
# Row end_______________________________
# content html
content = html.Div(
    [dcc.Graph(id="map", figure={}),
     html.Hr(),
     dbc.Container([dbc.Alert(id="location_alert",
                              children={}),
                    ],
                   className="justify-content-md-ends "),
     row
     ],
    style=CONTENT_STYLE)

app.layout = html.Div([sidebar, content])


# function for map in the main content page.
@ app.callback(
    Output(component_id="map", component_property='figure'),
    Input(component_id='bedrooms', component_property='value')
)
def update_map(beds):

    # filtering data
    df = median_edi_post_code[median_edi_post_code["beds"].isin(beds)]

    fig = px.choropleth_mapbox(df,
                               locations="name",
                               color="median",
                               mapbox_style='stamen-toner',
                               geojson=map_edi_geo,
                               featureidkey="properties.name",
                               center={'lat': 55.953251, 'lon': -3.188267},
                               zoom=9,
                               opacity=0.8,
                               color_continuous_scale=px.colors.sequential.algae,
                               hover_name="name",
                               hover_data={"name": True, "median": True},
                               custom_data=["name", "median", "min", "max", "count"],
                               # custom_data={"name": "name", "median": "median", "min": "min"},
                               title=f"Median of house prices for {beds} bedroom(s) properies",

                               )

    fig.update_geos(fitbounds="locations", visible=True)
    return fig


@ app.callback(
    Output(component_id="location_alert", component_property='children'),
    Output(component_id="cards_median", component_property='children'),
    Output(component_id="cards_min", component_property='children'),
    Output(component_id="cards_max", component_property='children'),
    Output(component_id="price_count", component_property='children'),
    Input(component_id='map', component_property='clickData'),
    Input(component_id='bedrooms', component_property='value'),
    # Input(component_id="reset_map", component_property="n_clicks")
)
def update_alert(map, drop_down):
    if map is None:
        df = median_edi_post_code[median_edi_post_code["beds"].isin(drop_down)]
        median_price = df["median"].mean()
        min_price = df["min"].min()
        max_price = df["max"].max()
        price_count = df_edi.shape[0]
        location = "All properties, please choose post code area by clicking the map."

        return location, median_price, min_price, max_price, price_count
    elif map != 0:
        location = (map["points"][0]["customdata"][0])
        median_price = (map["points"][0]["customdata"][1])
        min_price = (map["points"][0]["customdata"][2])
        max_price = (map["points"][0]["customdata"][3])
        df_loc = df_edi[(df_edi["beds"].isin(drop_down)) & (df_edi["post_code"] == location)]
        price_count = df_loc.shape[0]

        return f"Data for {location}", round(median_price, 2), min_price, max_price, price_count


@app.callback(
    Output(component_id='map', component_property='clickData'),
    Output(component_id='bedrooms', component_property='value'),
    Input(component_id="reset_map", component_property="n_clicks"),
)
def reset_clickData(n_clicks):

    return None, [2, 3]


if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
