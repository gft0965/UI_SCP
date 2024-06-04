## In Colab install the following packages: ###################################
#%pip install osmnx
#%pip install dash
#%pip install dash_leaflet
#%pip install dash_bootstrap_components
#%pip install cplex
#%pip install docplex
#%pip install dash-loading-spinners
###############################################################################

"""
With Anaconda in a local pc, in your environment, run: ########################

conda install spyder
conda install pandas
conda config --add channels conda-forge
conda config --set channel_priority strict
conda install osmnx
conda install dash
pip install dash-leaflet
pip install dash-bootstrap-components
pip install dash-loading-spinner
conda install geopy
pip install docplex
pip install cplex
###############################################################################
"""

import dash
from dash import Dash
import dash_bootstrap_components as dbc
import dash_loading_spinners as dls
from dash import html, callback_context, ALL
from dash import dcc, Output, Input, State, callback
import dash_leaflet as dl
#import re
import json
import pandas as pd
import geopy.distance
import numpy as np

#from google.colab import drive
#drive.mount('/content/drive',  force_remount=True)

import sys

root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
#sys.path.append('/content/drive/MyDrive/Colab Notebooks')
sys.path.append(root_dir + 'modules')
#"/content/drive/MyDrive/Colab Notebooks/calcroutes_module.py"
import calcroutes_module

from dash.long_callback import DiskcacheLongCallbackManager
## Diskcache
import diskcache
cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

print('Code restarted!')
"""
# the following code caused some problem...
# clean console ###############################################################
try:
    from IPython import get_ipython
    get_ipython().magic('clear')
    get_ipython().magic('reset -f')
except:
    pass
###############################################################################
print('Console cleared!')
"""
#"/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/calcroutes_module.py"

#im1 = '/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/CSL_logo.PNG'
#im2 = '/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/DFG_logo.png'
#im1 = '/home/beppe23/mysite/assets/CSL_logo.PNG'
#im2 = '/home/beppe23/mysite/assets/DFG_logo.png'
im1 = root_dir +'images/CSL_logo.PNG'
im2 = root_dir +'images/DFG_logo.png'

#stops_file = "/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/GTFS_files_bus_stops_12_02_2024/all_stops_12_02_2024.csv"
#stops_file = "/home/beppe23/mysite/assets/all_stops_12_02_2024.csv"
#stops_file = "C:/Users/gfotidellaf/Desktop/CSL_Gipuzkoa/Accessibility/assets/all_stops_12_02_2024.csv"
stops_file = root_dir +'data/all_bus_stops.csv'


from PIL import Image
image1 = Image.open(im1)
image2 = Image.open(im2)


stops_df = pd.read_csv(stops_file, encoding='latin-1')

stops_lat_lon = stops_df[['stop_lat','stop_lon']].to_numpy()

center = (43.26852347667122, -1.9741372404905988)
#    iconUrl= 'https://uxwing.com/wp-content/themes/uxwing/download/location-travel-map/bus-stop-icon.png',
#    iconUrl= "https://i.ibb.co/6n1tzcQ/bus-stop.png",
custom_icon = dict(
    iconUrl= "https://i.ibb.co/HV0K5Fp/bus-stop.png",
    iconSize=[40,40],
    iconAnchor=[22, 40]
)

app = Dash(prevent_initial_callbacks=True)

"""
app.layout = html.Div([
    html.Img(src=image1,style={'width':'40%', "display": "inlineBlock", "verticalAlign": "top"}),
    html.Img(src=image2,style={'width':'25%',"display": "inlineBlock", "verticalAlign": "top"}),
    html.Div(dl.Map([dl.TileLayer()],
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})),
    dbc.Button("Load stops", id="load_stops", n_clicks=0),
    html.Div(id='clickdata'),
    dcc.Store(id='internal-value', data=[])
])
"""
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
}

mouse_over_mess = """
Shifts stops to closest
<p>existing bus stops</p>"""

routes = [{'label': 'Route ' +str(i+1), 'value': i} for i in range(3)]

sidebar =  html.Div(
       [
        html.Button("Propose stops", id="propose_stops", n_clicks=0,style={"margin-top": "15px","font-weight": "bold"}),
        html.Br(),
        dcc.Input(id="n_clusters", type="text", value='19', style={"margin-top": "15px"}),
        html.Br(),
        html.Button("Match stops", id="match_stops", n_clicks=0, style={"margin-top": "15px", "font-weight": "bold"}),
        dbc.Popover(dcc.Markdown(mouse_over_mess, dangerously_allow_html=True),
                  target="match_stops",
                  body=True,
                  trigger="hover",style = {'font-size': 12, 'line-height':'2px'}),
        html.P([ html.Br(),'Choose number of buses'],id='buses_num',style={"margin-top": "15px","font-weight": "bold"}),
        dcc.Input(id="choose_buses", type="text", value='3'),
        html.Button("Calculate routes", id="calc_routes", n_clicks=0,style={"margin-top": "15px"}),
        html.P([ html.Br(),'Select route to visualize'],id='route_select',style={"margin-top": "15px", "font-weight": "bold"}),
        dcc.Dropdown(routes, multi=False,style={"margin-top": "15px"},id='choose_route'),
        html.Button("Visualize routes", id="visualize_routes", n_clicks=0,style={"margin-top": "15px"}),
        html.Br(),        
        html.P([ html.Br(),'Liters of gasoline per kilometer'],id='gas_km',style={"margin-top": "15px","font-weight": "bold"}),
        dcc.Input(id="choose_gas_km", type="text", value='1.12'),
        html.P([ html.Br(),'CO2 Kg per lt'],id='CO2_lt',style={"margin-top": "15px","font-weight": "bold"}),
        dcc.Input(id="choose_CO2_lt", type="text", value='2.3'),        
        html.Div(id='outdata', style={"margin-top": "15px"}),
        dcc.Store(id='internal-value_stops', data=[]),
        dcc.Store(id='internal-value_routes', data=[])
       ],
       style=SIDEBAR_STYLE)

"""
content = html.Div(
    [
          html.Div([
             html.Img(src=image1,style={'width':'40%', "display": "inlineBlock", "verticalAlign": "top"}),
             html.Img(src=image2,style={'width':'25%',"display": "inlineBlock", "verticalAlign": "top"}),
          ]),
          html.Div([dl.Map([dl.TileLayer()], center=center, zoom=12, id="map",style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"})
          ])
    ],
    style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
"""

content = html.Div(
    [
          html.Div([
             html.Img(src=image1,style={'width':'40%', "display": "inlineBlock", "verticalAlign": "top"}),
             html.Img(src=image2,style={'width':'25%',"display": "inlineBlock", "verticalAlign": "top"})
             ],style= {'verticalAlign': 'top'}),
          dls.Clock(
                    children=[dl.Map([dl.TileLayer(),
                    dl.ScaleControl(position="topright")], center=center, zoom=12, id="map",style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
],
                    color="#435278",
                    speed_multiplier=1.5,
                    width=80,
                    show_initially=False
                    )
    ],
    style=CONTENT_STYLE)
#app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=3, className='bg-light'),
                dbc.Col(content, width=9)
                ],
            style={"height": "100vh"}
            ),
    ],
    fluid=True
)




@app.long_callback([Output("outdata", "children",allow_duplicate=True),
               Output('internal-value_routes','data',allow_duplicate=True),
               Output("choose_route", "options",allow_duplicate=True),
               Output('map','children',allow_duplicate=True)],
              [State('choose_buses',"value")],
              [State('internal-value_stops','data')],
              [State('choose_CO2_lt','value')],
              [Input("calc_routes", "n_clicks")],
              manager=long_callback_manager
              )
def calc_routes(Nroutes,Stops,CO2km,Nclick):
    import calcroutes_module
    import dash_leaflet as dl
    custom_icon = dict(
    iconUrl= "https://i.ibb.co/HV0K5Fp/bus-stop.png",
    iconSize=[40,40],
    iconAnchor=[22, 40]
    )
    center = (43.26852347667122, -1.9741372404905988)
    
    #list_routes = range(1,int(Nroutes)+1)    
    list_routes = range(int(Nroutes))
    new_menu = [{'label': 'Route ' +str(i+1), 'value': i} for i in list_routes]
    print('\n')
    print('\n')
    print('Start calculating routes...')
    routes_coords = calcroutes_module.CalcRoutes_module(Stops,int(Nroutes),float(CO2km))
    print('Routes calculated!')
    print(routes_coords)
    # We don't really need to update the map here. We do it just to make the Spinner work: ############ 
    markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i}) for i, pos in enumerate(Stops)]
    newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"}) 
    ###################################################################################################   
    #return ["Calculation completed!", routes_coords, new_menu, newMap]
    return ["Calculation completed for: "+str(len(Stops)), routes_coords, new_menu, newMap]

#Output('map','children',allow_duplicate=True)

@app.callback([Output('map','children',allow_duplicate=True)],
              [State('choose_route',"value")],
              [State('internal-value_stops','data')],
              [State('internal-value_routes','data')],
              [Input("visualize_routes", "n_clicks")]
              )
def visualize_route(Route,Stops,RoutesCoords,Nclick):
    #Route = int(Route.split(' ')[1])-1
    Route = int(Route)-1    
    RoutesCoords = RoutesCoords[Route]

    markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i}) for i, pos in enumerate(Stops)]
    newMap = dl.Map([dl.TileLayer(), dl.ScaleControl(position="topright"), dl.Polyline(positions=RoutesCoords)] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
    return [newMap]


@app.callback([Output("outdata", "children",allow_duplicate=True), Output('internal-value_stops','data',allow_duplicate=True),Output('map','children',allow_duplicate=True)],
              [State('internal-value_stops','data')],
              [Input("match_stops", "n_clicks")]
              )
def match_stops(St,Nclicks):
    bus_stops = []
    out = ''
    for i_st in range(len(St)):
        #ref = np.array([lat,lon])
        ref = np.array([St[i_st][0],St[i_st][1]])
        ref = np.tile(ref,(len(stops_lat_lon),1)) # generate replicas of ref point
        #d = [sum((p-q)**2)**0.5 for p, q in zip(ref, stops_lat_lon)] # calculate distance of each bus stop to ref point
        d = [geopy.distance.geodesic((p[0],p[1]), (q[0],q[1])).km for p, q in zip(ref, stops_lat_lon)] # calculate distance of each bus stop to ref point

        ind_min = d.index(min(d)) # find index of closest bus stop
        x = stops_lat_lon[ind_min][0]
        y = stops_lat_lon[ind_min][1]
        bus_stops.append((x, y))
        St[i_st]=(x,y)
        out = out + str(St[i_st][0]) + ', ' + str(St[i_st][1]) + '; '
    markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
    newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
    return [len(St),St,newMap]


#@app.callback([Output("clickdata", "children")],
@app.callback([Output("outdata", "children"), Output('internal-value_stops','data',allow_duplicate=True),Output('map','children',allow_duplicate=True)],
              [State("n_clusters", "value"),
               Input("propose_stops", "n_clicks")]
              )
def propose_stops(n_clusters,N):
    import find_stops_module   
    n_clusters  = int(n_clusters)
    #filename = '/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/Accessibility_Map/INPUT_stops.csv'
    #filename = 'C:/Users/gfotidellaf/Desktop/CSL_Gipuzkoa/Accessibility/assets/INPUT_stops.csv'
    #filename = './assets/data/INPUT_stops.csv'
    #n_clusters = 19
    cutoff = 0.8 # cutoff for maximum density: take maxima which are at least cutoff*max
    root_dir = './assets/data/'
    #root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
    workers_DF = pd.read_csv(root_dir + "workers.csv", encoding='latin-1')
    stops_DF = pd.read_csv(root_dir + "all_bus_stops.csv", encoding='latin-1')
    bus_stops_df,model,yhat = find_stops_module.FindStops(workers_DF, stops_DF, n_clusters, cutoff)
    #df = pd.read_csv(filename)
    #out=St.loc[:'Lat']
    #for i in range(len(St)):
    #    out = out + str(St.loc[i,['Lat']]) + ', ' + str(St.loc[i,['Lon']]) + '; '
    out = ''
    St = []
    for ind in bus_stops_df.index:
         out = out + str(bus_stops_df['Lat'][ind]) + ',' + str(bus_stops_df['Lon'][ind]) +';'
         St.append((bus_stops_df['Lat'][ind],bus_stops_df['Lon'][ind]))
    markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
    newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
    #return [out,St,newMap]
    return [out,St,newMap]


@app.callback([Output("outdata", "children",allow_duplicate=True), Output('internal-value_stops','data',allow_duplicate=True),Output('map','children',allow_duplicate=True)],
              [State('internal-value_stops','data')],
              [Input('map','clickData')]
              )
def add_marker(St,clickd):
       #try:
       marker_lat = clickd['latlng']['lat']
       marker_lon = clickd['latlng']['lng']
       St.append((marker_lat,marker_lon))
       out=''
       for i in range(len(St)):
           out = out + str(St[i][0]) + ', ' + str(St[i][1]) + '; '
       #markers = [dl.Marker(dl.Tooltip("double click on Marker after drag to update its position"), position=pos, id="marker{}".format(i), draggable=True) for i, pos in enumerate(St)]
       #Layer_group = dl.LayerGroup(markers, id="markers_group")
       #Layer_group = dl.LayerGroup(markers, id={"type": "markers_group", "index": 0})
       #markers = [dl.Marker(id={'type': 'marker', 'index': key}, position=data[key]) for key in data]
       markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
       newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
       return [out,St,newMap]
       #except:
       #return [] 

@app.callback([Output("outdata", "children",allow_duplicate=True),Output('internal-value_stops','data',allow_duplicate=True),Output('map','children',allow_duplicate=True)],
              [State('internal-value_stops','data')],
              [Input({"type": "marker", "index": ALL},"n_clicks")],
              prevent_initial_callbacks=True)
def remove_marker(St,*args):
    marker_id = callback_context.triggered[0]["prop_id"].split(".")[0].split(":")[1].split(",")[0]
    n_clicks = callback_context.triggered[0]["value"]
    if n_clicks ==2:
       del St[int(marker_id)]
       out=''
       for i in range(len(St)):
           out = out + str(St[i][0]) + ', ' + str(St[i][1]) + '; '
       markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
       newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
       return [out,St,newMap]


if __name__ == '__main__':
    #app.run_server(Debug=True)
    app.run_server(port=8058,Debug=True)