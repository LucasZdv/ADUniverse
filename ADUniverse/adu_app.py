import adusql as ads
import dash
import dash_core_components as dcc
import dash_html_components as html
import folium
import functions
import geojson
import json
import pandas as pd
import sys

from dash.dependencies import Input, Output
from folium.plugins import Search
import nltk
nltk.download('punkt')

#FILE = "adudata_UnivDist_small.csv"
SEATTLE_COORDINATES = (47.6062, -122.3321)
init_zoom = 12
#data = pd.read_csv(FILE)

adunit = ads.Connection("adunits.db")
adunit.connect()
addresses = adunit.select("address")
adunit.disconnect()

# create empty map zoomed in on Seattle
map = folium.Map(location=SEATTLE_COORDINATES,
                 zoom_start=12, control_scale=True)

# add neighborhoods on top of this. This is an experiment to be replaced with a polygon geojson
geo_json_data = json.load(open('neighborhoods.geojson'))
# folium.GeoJson(geo_json_data).add_to(map)

# regular style of polygons

def style_function(feature):
    return {
        'weight': 2,
        'dashArray': '5, 5',
        'fillOpacity': 0,
        'lineOpacity': 1,
    }

def highlight_function(feature):
    return {
        'fillColor': 'blue',
        'weight': 2,
        'lineColor': 'black',
        'lineWeight': 2,
        'dashArray': '5, 5',
        'fillOpacity': 0.5,
        'lineOpacity': 1,
    }


# apply the neighborhood outlines to the map
neighborhoods = folium.features.GeoJson(geo_json_data,
                                        style_function=style_function,
                                        highlight_function=highlight_function,
                                        )
popup = folium.Popup('Your Dream is Here!')
popup.add_to(neighborhoods)
neighborhoods.add_to(map)

neighborhoodsearch = Search(
    layer=neighborhoods,
    geom_type='Polygon',
    placeholder='Search for a neighborhood name',
    collapsed=False,
    search_label='name',
    weight=3,
    kwargs={'fillColor': "blue",
            'fillOpacity': 0.6}
).add_to(map)
# We need to fix kwargs and popups of polygons iterating through geojson

# print(geo_json_data[1,:])
# geo_json_data_df = pd.DataFrame.from_dict(geo_json_data)
# geo_json_data_df.to_csv(r'/Users/Anaavu/Documents/GitHub/ADUniverse/app/geo_json_data_df.csv')
# Anagha

# for speed purposes
MAX_RECORDS = 100

# add a marker for every record in the filtered data, use a clustered view
#for _, row in data[0:MAX_RECORDS].iterrows():
    #popup = folium.Popup("Year Build: " + str(row['YRBUILT']) +
    #                     "<br> Address: " + str(row['ADDRESS']), max_width=300)
    #folium.Marker([row['INTPTLA'], row['INTPTLO']], popup=popup).add_to(map)

map.save("map.html")

# Dashify

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash("SeattleADU",
                external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("Seattle ADU Feasibility"),

    html.H3("Find your home"),
    dcc.Dropdown(
        id='addressDropdown',
        options=[
            {'label': i, 'value': i} for i in addresses.address.unique()
        ],
        placeholder='Type your house address here...'),

    # Not intuitively named
    html.Div(id='intermediate-value', style={'display': 'none'}),

    # Not intuitively named
    html.Div(id='output-container'),

    html.Iframe(id='map', srcDoc=open("map.html", "r").read(),
                width="100%", height="550"),

    html.H2("Why are you thinking of building an ADU?"),
    dcc.Dropdown(
        # Not intuitively named
        id='my-dropdown',
        options=[
            {'label': 'Build one more unit for rental income', 'value': 'income'},
            {'label': 'A Relative needs some housing', 'value': 'support'},
        ],
        value='purposes'
    ),
    # Not intuitively named
    html.Div(id='output_drop'),

    html.H3("How much do you want to borrow?"),
    dcc.Input(id='LoanInput', value='0', type='number'),
    html.Table([
        html.Tr([html.Td(['15 Year Fix Rate Loan']), html.Td(id='LoanAmount')]),
        html.Tr([html.Td(['Monthly Payment']), html.Td(id='MortgageCalculator')])

    ]),

    dcc.Markdown('''
    # **Frequently Asked Questions**
    # How to be a good landlord?
    here are some useful information.
    [Rental Housing Association of Washington](https://www.rhawa.org/)
    # More financial information?
    here are the home equity loan informations
    *Disclaimer: We help to gether useful informtions to facilitate your decisions *
    '''),
])

# dynamically updates the map based on the address selected


@app.callback(
    [Output('output-container', 'children'),
     Output('map', 'srcDoc')],
    [Input('addressDropdown', 'value')]
)
def update_map(value, coords=SEATTLE_COORDINATES, zoom=init_zoom):
    yearbuilt = 1

    if value != None:
        yearbuilt = 1
        #long = addresses.loc[addresses.address == value].reset_index()['INTPTLA'][0]
        #lat = addresses.loc[addresses.address == value].reset_index()['INTPTLO'][0]
        adunit = ads.Connection("adunits.db")
        adunit.connect()
        newCoords = adunit.getCoords(value)
        adunit.disconnect()
        coords = (newCoords.intptla[0], newCoords.intptlo[0])
        zoom = 14

    new_map = folium.Map(location=coords, zoom_start=zoom)


    neighborhoods.add_to(new_map)
    neighborhoodsearch = Search(
        layer=neighborhoods,
        geom_type='Polygon',
        placeholder='Search for a neighborhood name',
        collapsed=False,
        search_label='name',
        weight=3,
        kwargs={'fillColor': "blue",
                'fillOpacity': 0.6}
    ).add_to(new_map)
    new_map.save("map.html")
    # map.render()
    return 'The home you selected was built in year "{}"'.format(yearbuilt), open("map.html", "r").read()


@app.callback(
    Output('intermediate-value', 'children'),
    [Input('addressDropdown', 'value')]
)
def get_features(value):
    #if value != None:
        #output = data.loc[data['ADDRESS'] == value].reset_index()['YRBUILT'][0]
        #output = addresses.loc[addresses.address == value].reset_index()['YRBUILT'][0]
    output = 0
    return output


@app.callback(
    [Output(component_id='LoanAmount', component_property='children'),
     Output(component_id='MortgageCalculator', component_property='children')],
    [Input(component_id='LoanInput', component_property='value'),
     Input(component_id='intermediate-value', component_property='children')]
)
def loan_calculator(loan, feature):
    return functions.loan_calculator(loan, feature)


@app.callback(
    Output('output_drop', 'children'),
    [Input('my-dropdown', 'value')])
def update_purpose(value):
    return 'You are builing this ADU for "{}"'.format(value)


if __name__ == '__main__':
    app.run_server(debug=True)
