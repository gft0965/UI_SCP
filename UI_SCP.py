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
pip install dash-loading-spinners
pip install dash-daq?
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
from dash import dcc, Output, Input, State, callback, dash_table
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash_extensions.javascript import assign
import dash_daq as daq

import plotly.express as px

import base64
import datetime
import io
from io import StringIO

#import re
import json
import pandas as pd
import geopy.distance
import numpy as np

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, adjusted_rand_score

#from google.colab import drive
#drive.mount('/content/drive',  force_remount=True)

import sys
import os
from os import listdir

root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
#sys.path.append('/content/drive/MyDrive/Colab Notebooks')
sys.path.append(root_dir + 'modules')
#"/content/drive/MyDrive/Colab Notebooks/calcroutes_module.py"
#import calcroutes_module -> import inside callback function
#import generate_GTFS_module -> import inside callback function

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
#im2 = root_dir +'images/DFG_logo.png'
#im3 = root_dir +'images/MUBIL_logo.png'

#stops_file = "/content/drive/MyDrive/Colab Notebooks/CSL_GIPUZKOA/GTFS_files_bus_stops_12_02_2024/all_stops_12_02_2024.csv"
#stops_file = "/home/beppe23/mysite/assets/all_stops_12_02_2024.csv"
#stops_file = "C:/Users/gfotidellaf/Desktop/CSL_Gipuzkoa/Accessibility/assets/all_stops_12_02_2024.csv"
stops_file = root_dir +'data/all_bus_stops.csv'


from PIL import Image
image1 = Image.open(im1)
#image2 = Image.open(im2)
#image3 = Image.open(im3)


stops_df = pd.read_csv(stops_file, encoding='latin-1')
stops_lat_lon = stops_df[['stop_lat','stop_lon']].to_numpy()

bus_icon = "https://i.ibb.co/HV0K5Fp/bus-stop.png" 
worker_icon = "https://i.ibb.co/W0H7nYM/meeting-point.png"
coworking_icon = "https://i.ibb.co/J2qXGKN/coworking-icon.png"

center = (43.26852347667122, -1.9741372404905988)
#    iconUrl= 'https://uxwing.com/wp-content/themes/uxwing/download/location-travel-map/bus-stop-icon.png',
#    iconUrl= "https://i.ibb.co/6n1tzcQ/bus-stop.png",
custom_icon_bus = dict(
    iconUrl= bus_icon,
    iconSize=[40,40],
    iconAnchor=[22, 40]
)
custom_icon_worker = dict(
    iconUrl= worker_icon,
    iconSize=[40,40],
    iconAnchor=[22, 40]
)
custom_icon_coworking = dict(
    iconUrl= coworking_icon,
    iconSize=[40,40],
    iconAnchor=[22, 40]
)


app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],prevent_initial_callbacks=True)

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
    "width": "25rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
    "overflow": "scroll"           # scrollbar
}

"""
"padding": "2rem 1rem",
"background-color": "#f8f9fa",
"""
# the styles for the main content position it to the right of the sidebar and
# add some padding.

CONTENT_STYLE = {
    "margin-left": "5rem",
    "margin-right": "0rem",
}



INDICATORS_STYLE = {
    "background-color": "#f8f9fa",
}
"""
    "position": "fixed",
    "top": 0,
    "right": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "2rem 1rem",
"""

mouse_over_mess = """
Shifts stops to closest
<p>existing bus stops</p>"""

mouse_over_mess_stops = """
Proposes bus stops based on
<p>workers Lats/Lons in CSV file</p>
<p>and the number of clusters</p>"""

mouse_over_mess_clusters = """
Clusters by which to group workers"""

mouse_over_mess_depot = """
Uncheck box for removing bus stops!"""

routes = [{'label': 'Route ' +str(i+1), 'value': i} for i in range(3)]

stops_actions = [{'label': 'Delete marker', 'value': 'DM'},
                 {'label': 'Set origin of bus routes', 'value': 'SO'},
                 {'label': 'Set coworking hub', 'value': 'SC'}                   
                ]

interventions = [{'label': 'Company transportation', 'value': 'CT'},
                 {'label': 'Remote working', 'value': 'RW'}                   
                ]

choose_transp_hour = [{'label': "{:02d}".format(i) + ':00' + '-' + "{:02d}".format(i+1) + ':00', 'value': i} for i in range(24)] 

sidebar =  html.Div(
       [
        html.P(['Import worker file'],id='import_text',style={"margin-top": "15px","font-weight": "bold"}),
        dcc.Upload(
             id='upload-data',
             children=html.Div([
                       html.A('Import Files')
                       ]),
             style={
                  'width': '100%',
                  'height': '60px',
                  'lineHeight': '60px',
                  'borderWidth': '1px',
                  'borderStyle': 'dashed',
                  'borderRadius': '5px',
                  'textAlign': 'center',
                  'margin': '10px'
                  },
             # Allow multiple files to be uploaded
             multiple=True
        ),
        dcc.Store(id='worker_data', data=[]),
        html.P([ html.Br(),'Choose number of clusters'],id='cluster_num',style={"margin-top": "15px","font-weight": "bold"}),        
        dbc.Popover(
                  dbc.PopoverBody(mouse_over_mess_clusters), 
                  target="n_clusters",
                  body=True,
                  trigger="hover",style = {'font-size': 12, 'line-height':'2px'},
                  placement= 'right',
                  is_open=False),
        #dcc.Input(id="n_clusters", type="text", value='19'),
        dcc.Slider(1, 30, 1,
               value=19,
               id='n_clusters',
               marks=None,
               tooltip={"placement": "bottom", "always_visible": True}
            ) , 

        dbc.Button("Visualize workers", id="show_workers", n_clicks=0,style={"margin-top": "15px","font-weight": "bold"}),
        html.Br(),
        dbc.Button("Calculate baseline scenario", id="calc_baseline", n_clicks=0,style={"margin-top": "15px","font-weight": "bold"}),
        html.Br(),
        dbc.Button("Visualize scenarios", id="visualize_scenarios", n_clicks=0,style={"margin-top": "15px","font-weight": "bold"}),          
        html.P([ html.Br(),'Select type of interventions'],id='intervention_select',style={"margin-top": "15px", "font-weight": "bold"}),
        dcc.Dropdown(interventions, multi=False,style={"margin-top": "15px"}, id='choose_intervention'),
        html.P([ html.Br(),'Select action for markers'],id='action_select',style={"margin-top": "15px", "font-weight": "bold"}),
        dcc.Dropdown(stops_actions, multi=False,style={"margin-top": "15px"}, id='choose_stop_action'),           
        html.Div([
                 html.Div(id='outdata', style={"margin-top": "15px"}),
                 dcc.Store(id='internal-value_stops', data=[]),
                 dcc.Store(id='internal-value_coworking', data=[]),        
                 dcc.Store(id='internal-value_routes', data=[])
                 ],
                 id='sidebar_intervention', style={"margin-top": "15px"})
        ],
       id='sidebar',
       style=SIDEBAR_STYLE)


content = html.Div(
       [
          html.Div([
             html.Img(src=image1,style={'width':'40%', "display": "inlineBlock", "verticalAlign": "top"}),
             #html.Img(src=image2,style={'width':'25%',"display": "inlineBlock", "verticalAlign": "top"}),
             #html.Img(src=image3,style={'width':'25%',"display": "inlineBlock", "verticalAlign": "top"})

             ],style= {'verticalAlign': 'top'}),
          dls.Clock(
                    children=[dl.Map([dl.TileLayer(),
                    dl.ScaleControl(position="topright")], center=center, 
                                     zoom=12,
                                     id="map",style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
                    ],
                    color="#435278",
                    speed_multiplier=1.5,
                    width=80,
                    show_initially=False
                    )
    ],
    style=CONTENT_STYLE)


# plot test data
df = px.data.tips()
fig = px.pie(df, values='tip', names='day')
fig.update_layout(showlegend=False)
fig.update_layout(title_text='Transport share', title_x=0.5)
indicators = html.Div(
        [           
          html.P([ html.Br(),'Liters of gasoline per kilometer'],id='gas_km',style={"margin-top": "15px","font-weight": "bold"}),
          #dcc.Input(id="choose_gas_km", type="text", value='1.12'),
          dcc.Slider(0, 10,0.05,
               value=1.12,
               id='choose_gas_km',
               marks=None,
               tooltip={"placement": "bottom", "always_visible": True}
          ) ,          
          html.P([ html.Br(),'CO2 Kg per lt'],id='CO2_lt',style={"margin-top": "15px","font-weight": "bold"}),
          #dcc.Input(id="choose_CO2_lt", type="text", value='2.3', style={"margin-bottom": "15px"}),             
          dcc.Slider(0, 10,0.05,
               value=2.3,
               id='choose_CO2_lt',
               marks=None,
               tooltip={"placement": "bottom", "always_visible": True}
          ),
          dbc.Row(
            [
                dbc.Col(
                    html.Div(html.P(['Choose trip time'],style={"font-weight": "bold"})),
                    style={"margin-top": "15px"},
                    width="auto"
                ),                
                dbc.Col(
                    html.Div(dcc.Dropdown(choose_transp_hour, multi=False, id='choose_transp_hour')),
                    style={"margin-top": "15px"},
                    width=4
                ),
                dbc.Col(
                    html.Div(dcc.Loading(html.Div(id="running_MCM"), id="loading-component_MCM")),
                    style={"margin-top": "15px"},
                    width="auto"
                ),
                dbc.Col(
                    html.Div(dbc.Button("Run Mode Choice", id="run_MCM", n_clicks=0, disabled=True)),
                    style={"margin-top": "15px"},
                    width="auto"
                )
            ]
          ),
          html.Div([
             daq.Gauge(
             color={"gradient":True,"ranges":{"green":[0,0.333],"yellow":[0.333,0.666],"red":[0.666,1.0]}},
             value=0.3,
             label={'label':'CO2 emissions', 'style':{'font-size':'18px',"font-weight": "bold"}},
             style = {"margin-top": "20px","font-weight": "bold"},
             max=1,
             min=0,
             id='CO2_gauge')
             ]),
          html.Div([
              dcc.Graph(
                figure={
                        'data': [{
                                'labels': [1, 2, 3], 
                                'values': [1, 2, 3], 
                                'type': 'pie',
                                }],
                        'layout': {
                            'title': 'Transport share'
                        }        
                }, id='graph', 
                style={'width':'60vh'})
            ], style={'width':'100%'})
        ],
        style=INDICATORS_STYLE)
"""
          dcc.Graph(figure=fig, id="graph",
                    style={'width': '60vh'})
          ],style={'width': '100%'})
        ],

"""
#app.layout = html.Div([dcc.Location(id="url"), sidebar, content])
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=2, className='bg-light'),
                dbc.Col(content, width=7),
                dbc.Col(indicators, width=3)
                ],
            style={"height": "100vh"}
            ),
    ],
    fluid=True
)


# Folder navigator ###############################################################
def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
    temp_file = root_dir + 'data/temp_workers_data.csv'
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            #tmp = io.StringIO(decoded.decode('utf-8'))
            #print(dir(tmp))
            #print(decoded)
            #print(decoded.decode('utf-8'))
            #print(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    return df.to_csv(temp_file, index=False)  

def drawclusters(workers_df,n_clusters):
    from sklearn.cluster import KMeans
    from scipy.spatial import ConvexHull

    workers_lat_lon = workers_df[['O_lat', 'O_long']].values.tolist()
    workers_lat_lon = np.array(workers_lat_lon)
    model = KMeans(n_clusters=n_clusters, max_iter=500).fit(workers_lat_lon)
    clusters_poly = []
    for i in range(n_clusters):
        points = workers_lat_lon[model.labels_ == i]
        hull = ConvexHull(points)
        vert = np.append(hull.vertices, hull.vertices[0])  # close the polygon by appending the first point at the end
        clusters_poly.append(points[vert])
    return clusters_poly

def suggest_clusters(wdf):
    #sil_score_max = -100 #this is the minimum possible score
    dist_max = 100
    wdf = wdf[['O_lat', 'O_long']].values.tolist()
    alpha = 0.65
    n_max_clusters = int(19.*len(wdf)/2507)
    #beta = (1-alpha)*19 + alpha*0.63
    sil_score_max = 1

    for n_clusters in range(2,31):
        #model = KMeans(n_clusters = n_clusters, init='k-means++', max_iter=100, n_init=1)
        model = KMeans(n_clusters = n_clusters)
        labels = model.fit_predict(wdf)
        #sil_score = silhouette_score(wdf, labels, sample_size=len(wdf), random_state=42, metric= 'mahalanobis')
        sil_score = silhouette_score(wdf, labels, metric= 'manhattan')
        #db_score = davies_bouldin_score(wdf, labels)
        #ar_score = adjusted_rand_score(wdf, labels)
        #sil_score = silhouette_score(wdf, labels)
        #aver_score = (1 - alpha)*n_clusters/n_max_clusters + alpha*sil_score
        #x = (1-alpha)*n_clusters + alpha*sil_score    
        #aver_score = - (x - beta)**2 + 1
        d0 = (1-alpha)*(n_max_clusters - n_clusters)/n_max_clusters
        d1 = alpha*(sil_score_max - sil_score) 
        dist_to_max = (d0**2 + d1**2)**0.5
        print("The average silhouette and db score for %i clusters are %0.2f; the average score is %0.2f" %(n_clusters,sil_score, dist_to_max))
        #if sil_score > sil_score_max:
        if dist_to_max < dist_max:   
           dist_max = dist_to_max
           best_n_clusters = n_clusters
    return best_n_clusters    

def generate_colors(n):
    import random
    colors = []
    for i in range(n):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = '#%02x%02x%02x'%(r, g, b)
        if color not in colors:
            colors.append(color)
    return colors 


def interpolate_color(color_start_rgb, color_end_rgb, t):
    """
    Interpolate between two RGB colors.
    
    Parameters:
    - color_start_rgb: Tuple of integers representing the starting RGB color.
    - color_end_rgb: Tuple of integers representing the ending RGB color.
    - t: Float representing the interpolation factor between 0 and 1.
    
    Returns:
    - A tuple representing the interpolated RGB color.
    """
    #print(color_start_rgb)
    #color_start_rgb = color_start_rgb.split('#')[1] 
    #color_end_rgb = color_end_rgb.split('#')[1]
    return tuple(int(start_val + (end_val - start_val) * t) for start_val, end_val in zip(color_start_rgb, color_end_rgb))

def hex_to_rgb(hex_color):
    """
    Convert hex to RGB.
    
    Parameters:
    - hex_color: String representing the hexadecimal color code.
    
    Returns:
    - A tuple of integers representing the RGB values.
    """
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generate_color_CO2(CO2max,CO2_i):
    #from  matplotlib.colors import ListedColormap, Normalize, LogNorm
    import matplotlib as mpl

    """
    cmap = mpl.colors.ListedColormap(['green', 'yellow', 'red'])
     #norm = mpl.colors.Normalize(vmin=0, vmax=100)
    norm = mpl.colors.LogNorm(vmin=0+1, vmax=CO2max+1) 
    # create a scalarmappable from the colormap
    #sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)  
    sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
    #color_hex= mpl.colors.to_hex(sm.to_rgba(idx), keep_alpha=False)
    color_hex= mpl.colors.to_hex(sm.to_rgba(CO2_i))
    """
    ranges = [
        {"start": "2ECC71", "end": "F7DC6F"},
        {"start": "F7DC6F", "end": "E74C3C"}
    ]

    color_start_hex = ranges[0]["start"]
    color_end_hex = ranges[0]["end"]
    color_start_rgb = hex_to_rgb(color_start_hex)
    color_end_rgb = hex_to_rgb(color_end_hex)
    # Generate gradient
    gradient1 = [interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]
    color_start_hex = ranges[1]["start"]
    color_end_hex = ranges[1]["end"]
    color_start_rgb = hex_to_rgb(color_start_hex)
    color_end_rgb = hex_to_rgb(color_end_hex)
    # Generate gradient
    gradient2 = [interpolate_color(color_start_rgb, color_end_rgb, t) for t in np.linspace(0, 1, 256)]
    gradient = gradient1 + gradient2
    N = len(gradient)

    value = int((CO2_i/CO2max)*N)
    idx = np.argmin(np.abs(np.array(range(N))-value))
    color = [gradient[idx][0]/256,gradient[idx][1]/256,gradient[idx][2]/256]
    color_hex = mpl.colors.to_hex(color)
    #if value == N:
    #print(value,idx,color)

    return color_hex

def run_MCM(Transh, NremDays=0, NremWork=30, CowCoords=None):
    import pandas as pd
    print('Inside run_MCM 0')
    import sys    
    root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
    sys.path.append(root_dir + 'modules')
    import pp
    import prediction
    import pandas as pd
 
    if Transh == None:
        Transh = 8
        print('Transport hour not selected. Using default (08:00)')
    else:
        print('Chosen transport hour: ',Transh)
    workers_data_dir = 'data/'
    MCM_data_dir = 'data/input_data_MCM/'    
    model_dir = 'modules/models/'
    #trips_ez = pd.read_csv(root_dir + data_dir + 'workers_eskuzaitzeta_2k.csv')
    trips_ez = pd.read_csv(root_dir + workers_data_dir + 'temp_workers_data.csv')
    eliminar = ['Unnamed: 0', 'Com_Ori', 'Com_Des', 'Modo', 'Municipio',
                'Motos','Actividad','Año','Recur', 'Income', 'Income_Percentile'] # adaptamos trips como input al pp

    trips_ez = trips_ez.drop(columns=eliminar)
    trips_ez.head(10).to_csv(root_dir + workers_data_dir + 'example_workers_data.csv',index=False)
    trips_ez=pp.pp(Transh,trips_ez, CowCoords, NremDays, NremWork, root_dir + MCM_data_dir) 
    #trips_ez['transit_tt'] = trips_ez['transit_tt'].apply(lambda x: x*0.2)
    #trips_ez['drive_tt'] = trips_ez['drive_tt'].apply(lambda x: x*1)
    prediction=prediction.predict(trips_ez, root_dir + model_dir)  
    print() 
    print('result:')
    print(prediction.head())
    return prediction


@callback([Output('CO2_gauge', 'value',allow_duplicate=True),
          Output('map','children',allow_duplicate=True)],
          State('choose_transp_hour','value'),
          Input('calc_baseline', 'n_clicks'),
          prevent_initial_call = True)
def calc_baseline(TransHour, Nclicks):
    import pandas as pd
    print('Inside run_MCM 0')
    import sys    
    root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
    sys.path.append(root_dir + 'modules')

    #selected_workers = select_workers(hours,origin(Municipio), destination(lat,lon))
    result = run_MCM(TransHour)
    #fig=show_MCM_results(result)
    #fig = px.scatter_geo(result,
    #                lat=result.geometry.y,
    #                lon=result.geometry.x,
    #                hover_name="Mode",
    #                center = {'lat': 43.267237445097614, 'lon': -1.9937731483199466},
    #                color="Mode") 
    #coords_dict = []
    #print('coords dict.:')
    #for i in result.itertuples():
    #    coords_dict.append({'lat': i.geometry.y,'lon': i.geometry.x})
    #    #print(i) 
          
    children = [dl.TileLayer()]
    maxCO2 = result['CO2'].max()
    Total_CO2 = result['CO2'].sum()
    for i_pred in result.itertuples():
        color = generate_color_CO2(maxCO2,i_pred.CO2) 
        #print(color)
        #text = i_pred.Mode
        text = 'CO2: ' + '{0:.2f}'.format(i_pred.CO2) + ' Kg ' + '(' + i_pred.Mode + ')' + '<br>' +  'Tot. distance: ' + '{0:.2f}'.format(i_pred.distance/1000) + ' Km'
        marker_i = dl.CircleMarker(
                        id=str(i_pred),
                        children=[dl.Tooltip(content=text)],
                        center=[i_pred.geometry.y, i_pred.geometry.x],
                        radius=10,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=1,
                        )
        children.append(marker_i)   
    #dl.GeoJSON(data=dlx.dicts_to_geojson(coords_dict), cluster=False),
    children.append(dl.ScaleControl(position="topright"))
    new_map = dl.Map(children, center=center, 
                                     zoom=12,
                                     id="map",style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})

    """
    new_map = dl.Map([dl.TileLayer(), 
                    dl.ScaleControl(position="topright")], center=center, 
                                     zoom=12,
                                     id="map",style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
    """
    return [8,new_map]


@callback([Output('CO2_gauge', 'value',allow_duplicate=True),
           Output('graph','figure',allow_duplicate=True),
           Output('map','children',allow_duplicate=True),
           Output('loading-component_MCM','children')],
          [State('choose_remote_days', 'value'),
          State('choose_remote_workers', 'value'),
          State('internal-value_stops','data'),
          State('internal-value_coworking','data'),
          State('choose_transp_hour','value')],
          Input('run_MCM', 'n_clicks'),
          prevent_initial_call=True)
def run_MCM_callback(NremDays, NremWork, StopsCoords, CowoFlags, TransH, Nclicks):

    print('Cow. Flags:')
    print(CowoFlags)
    CowoIn = np.nonzero(CowoFlags)[0]
    print('Indices:')
    print(CowoIn)
    print('All coords:')
    print(StopsCoords)
    #CowoCoords = np.take(StopsCoords, CowoIn)
    CowoCoords = np.array(StopsCoords)[CowoIn]
    print('Cow coords:')
    print(CowoCoords)
    
    result = run_MCM(TransH, NremDays, NremWork, CowoCoords)
    
    predicted = result['prediction']
    unique_labels, counts = np.unique(predicted, return_counts=True)
    d = {'unique_labels': unique_labels, 'counts':counts}
    df = pd.DataFrame(data=d)    
    #        'labels': df['unique_labels'],
    fig = {
        'data':[{
            'labels': ['Walk','PT','Car'],
            'values': df['counts'],
            'type': 'pie'
        }]
    }


    children = [dl.TileLayer()]
    maxCO2 = result['CO2'].max()
    Total_CO2 = result['CO2'].sum()
    Total_CO2_worst_case = result['CO2_worst_case'].sum()
    for i_pred in result.itertuples():
        color = generate_color_CO2(maxCO2,i_pred.CO2) 
        #print(color)
        #text = i_pred.Mode
        text = 'CO2: ' + '{0:.2f}'.format(i_pred.CO2) + ' Kg ' + '(' + i_pred.Mode + ')' + '<br>' +  'Weekly distance: ' + '{0:.2f}'.format(i_pred.distance/1000) + ' Km'
        #text = text + '<br>' + 'Remote working: ' + str(i_pred.Rem_work)
        n_cw = int(i_pred.Rem_work)
        text = text + '<br>' + 'Remote working: ' + (['Yes']*n_cw + ['No'])[n_cw-1]
        n_cw = int(i_pred.Coworking)    
        text = text + '<br>' + 'Coworking: ' + (['Yes']*n_cw + ['No'])[n_cw-1]          
        marker_i = dl.CircleMarker(
                        id=str(i_pred),
                        children=[dl.Tooltip(content=text)],
                        center=[i_pred.geometry.y, i_pred.geometry.x],
                        radius=10,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=1,
                        )
        children.append(marker_i)   
    #dl.GeoJSON(data=dlx.dicts_to_geojson(coords_dict), cluster=False),
    children.append(dl.ScaleControl(position="topright"))
    new_map = dl.Map(children, center=center, 
                                     zoom=12,
                                     id="map",style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})

    return [Total_CO2/Total_CO2_worst_case, fig, new_map,True]


@callback([Output('worker_data', 'data'),Output('n_clusters','value')],
              [Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              Input('upload-data', 'last_modified')])
def load_worker_data(list_of_contents, list_of_names, list_of_dates):
    root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'        
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        #[print(c, n, d) for c, n, d in
        #    zip(list_of_contents, list_of_names, list_of_dates)]
        #return children
        #content_type, content_string = list_of_contents[0].split(',')
        #decoded = base64.b64decode(content_string)
        #filename = io.StringIO(decoded.decode('utf-8'))
        works_data = children
        temp_file = root_dir + 'data/' + 'temp_workers_data.csv'
        df = pd.read_csv(temp_file) 
        suggested_N_clusters = suggest_clusters(df)
        #print('workers dataframe?', works_data)
        
        return [works_data,suggested_N_clusters]
############################################################################################

#@app.callback([Output("clickdata", "children")],
@app.callback([Output("outdata", "children"), Output('internal-value_stops','data',allow_duplicate=True),Output('internal-value_coworking','data',allow_duplicate=True),Output('map','children',allow_duplicate=True)],
              State("n_clusters", "value"),
              Input("propose_stops", "n_clicks")
              )
def propose_stops(n_clusters,Nclick):
    if Nclick > 0:  
        root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
        sys.path.append(root_dir + 'modules')      
        import find_stops_module   
        n_clusters  = int(n_clusters)
        cutoff = 0.8 # cutoff for maximum density: take maxima which are at least cutoff*max
        #root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
        #workers_DF = pd.read_csv(root_dir + "workers.csv", encoding='latin-1')
        temp_file = root_dir + 'data/' + 'temp_workers_data.csv'
        workers_DF = pd.read_csv(temp_file)    
        stops_DF = pd.read_csv(root_dir + 'data/'+ "all_bus_stops.csv", encoding='latin-1')
        bus_stops_df,model,yhat = find_stops_module.FindStops(workers_DF, stops_DF, n_clusters, cutoff)
        #df = pd.read_csv(filename)
        #out=St.loc[:'Lat']
        #for i in range(len(St)):
        #    out = out + str(St.loc[i,['Lat']]) + ', ' + str(St.loc[i,['Lon']]) + '; '
        out = ''
        St = []
        Cow = []
        for ind in bus_stops_df.index:
            out = out + str(bus_stops_df['Lat'][ind]) + ',' + str(bus_stops_df['Lon'][ind]) +';'
            St.append((bus_stops_df['Lat'][ind],bus_stops_df['Lon'][ind]))
            Cow.append(0)
        markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
        newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                        center=center, zoom=12, id="map",
                        style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
        #return [out,St,newMap]
        return [out,St,Cow,newMap]

@app.callback([Output('map','children',allow_duplicate=True)],
                State("n_clusters", "value"),
               [Input("show_workers", "n_clicks")]
              )
def show_workers(n_clusters,N):
    root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
    temp_file = root_dir + 'data/temp_workers_data.csv'
    workers_DF = pd.read_csv(temp_file)
    """
    St = []
    for ind in workers_DF.index:
         St.append((workers_DF['O_lat'][ind],workers_DF['O_long'][ind]))
    markers = [dl.Marker(dl.Tooltip("Do something?"), position=pos, icon=custom_icon_worker, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
    newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
    """ 
    clusters = drawclusters(workers_DF,n_clusters)
    colors = generate_colors(n_clusters)
    cluster_shapes = [dl.Polygon(children = dl.Tooltip('Number of workers: '+str(len(clusters[i]))), positions=clusters[i], fill=True, fillColor = colors[i], fillOpacity=0.6) for i in range(n_clusters)]
    newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + cluster_shapes,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})

    return [newMap]


@app.callback([Output('sidebar_intervention','children',allow_duplicate=True), Output('run_MCM','disabled')],
              State('internal-value_stops','data'),
              State('internal-value_coworking','data'),
              Input('choose_intervention',"value")
              )
def choose_intervention(St,Cow,interv):
    print('chosen interv.: ', interv)
           
    if interv == 'CT':
        sidebar_transport = html.Div(
            [           
            dbc.Button("Propose stops", id="propose_stops", n_clicks=0,style={"margin-top": "15px","font-weight": "bold"}),
            html.Br(),
            dbc.Popover(dcc.Markdown(mouse_over_mess_stops, dangerously_allow_html=True),
                      target="propose_stops",
                      body=True,
                      trigger="hover",style = {'font-size': 12, 'line-height':'2px'}),


            dbc.Button("Match stops", id="match_stops", n_clicks=0, style={"margin-top": "15px", "font-weight": "bold"}),
            dbc.Popover(dcc.Markdown(mouse_over_mess, dangerously_allow_html=True),
                      target="match_stops",
                      body=True,
                      trigger="hover",style = {'font-size': 12, 'line-height':'2px'}),
            html.P([ html.Br(),'Choose number of buses'],id='buses_num',style={"margin-top": "15px","font-weight": "bold"}),
            #dcc.Input(id="choose_buses", type="text", value='3'),
            dcc.Slider(1, 10, 1,
                   value=2,
                   id='choose_buses'
            ),
            dbc.Button("Calculate routes", id="calc_routes",n_clicks=0, style={"margin-top": "15px"}),
            html.P([ html.Br(),'Select route to visualize'],id='route_select',style={"margin-top": "15px", "font-weight": "bold"}),
            dcc.Dropdown(routes, multi=False,style={"margin-top": "15px"},id='choose_route'),
            dbc.Button("Visualize routes", id="visualize_routes", n_clicks=0,style={"margin-top": "15px"}),
            html.Br(),               
            html.Div(id='outdata', style={"margin-top": "15px"}),
            dcc.Store(id='internal-value_stops', data=St),
            dcc.Store(id='internal-value_coworking', data=Cow),        
            dcc.Store(id='internal-value_routes', data=[])
            ])       
        
        return [sidebar_transport,True]

    if interv == 'RW':         
        
        sidebar_remote_work = html.Div(
                [
                html.P([ html.Br(),'Choose number of days of remote working'],id='remote_days_num',style={"margin-top": "15px","font-weight": "bold"}),
                #dcc.Input(id="choose_buses", type="text", value='3'),
                dcc.Slider(1, 7, 1,
                       value=3,
                       id='choose_remote_days'
                ),
                html.P([ html.Br(),'Choose "%" of remote workers'],id='remote_workers_num',style={"margin-top": "15px","font-weight": "bold"}),
                #dcc.Input(id="choose_buses", type="text", value='3'),
                dcc.Slider(0, 100, 5,
                       value=30,
                       id='choose_remote_workers',
                       marks=None,
                       tooltip={"placement": "bottom", "always_visible": True}                       
                ),
                html.Br(),               
                html.Div(id='outdata', style={"margin-top": "15px"}),
                dcc.Store(id='internal-value_stops', data=St),
                dcc.Store(id='internal-value_coworking', data=Cow),        
                dcc.Store(id='internal-value_routes', data=[])
                ])        

        
        return [sidebar_remote_work,False]



@app.long_callback([Output("outdata", "children",allow_duplicate=True),
               Output('internal-value_routes','data',allow_duplicate=True),
               Output("choose_route", "options",allow_duplicate=True),
               Output('map','children',allow_duplicate=True)],
              [State('choose_buses',"value"),
              State('internal-value_stops','data'),
              State('internal-value_coworking','data'),
              State('choose_CO2_lt','value')],
              [Input("calc_routes", "n_clicks")],
              manager=long_callback_manager
              )
def calc_routes(Nroutes,St,Cow,CO2km,Nclick):
    if Nclick > 0:
      root_dir = 'C:/Users/gfotidellaf/repositories/UI_SCP/assets/'
      sys.path.append(root_dir + 'modules')  
      import calcroutes_module
      import dash_leaflet as dl
      import generate_GTFS_module as gGTFS
      custom_icon_bus = dict(
      iconUrl= "https://i.ibb.co/HV0K5Fp/bus-stop.png",
      iconSize=[40,40],
      iconAnchor=[22, 40]
      )

      custom_icon_coworking = dict(
      iconUrl= "https://i.ibb.co/J2qXGKN/coworking-icon.png",
      iconSize=[40,40],
      iconAnchor=[22, 40]
      )    
    
      center = (43.26852347667122, -1.9741372404905988)
    
      #list_routes = range(1,int(Nroutes)+1)    
      list_routes = range(int(Nroutes))
      new_menu = [{'label': 'Route ' +str(i+1), 'value': i} for i in list_routes]
      Stops = []
      markers = []
      print('Discriminating bus stops from coworking hubs...')
      for i, pos in enumerate(St): 
        if Cow[i]==1:
             custom_icon = custom_icon_coworking
        else:
             custom_icon = custom_icon_bus
             Stops.append(pos)
        tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
        markers.append(tmp)  

      print('List of Stops generated')        
      print('\n')
      print('\n')
      print('Start calculating routes...')
      routes, routes_points_coords, Graph = calcroutes_module.CalcRoutes_module(Stops,int(Nroutes),float(CO2km))
      print('Routes calculated!')
      #print(routes_points_coords)
      gGTFS.gGTFS(routes, Stops, Graph)
      # We don't really need to update the map here. We do it just to make the Spinner work: ############ 
      #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(Stops)]
      newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"}) 
      ###################################################################################################   
      #return ["Calculation completed!", routes_coords, new_menu, newMap]
      return ["Calculation completed for: "+str(len(Stops)), routes_points_coords, new_menu, newMap]


@app.callback([Output('map','children',allow_duplicate=True)],
              [State('choose_route',"value"),
              State('internal-value_stops','data'),
              State('internal-value_coworking','data'),
              State('internal-value_routes','data')],
              [Input("visualize_routes", "n_clicks")]
              )
def visualize_route(Route,St,Cow,RoutesCoords,Nclick):
    if Nclick > 0:
      print('Start route visualization...')
      #Route = int(Route.split(' ')[1])-1
      Route = int(Route)-1    
      RoutesCoords = RoutesCoords[Route]
      markers = []
      for i, pos in enumerate(St): 
        if Cow[i]==1:
             custom_icon = custom_icon_coworking
        else:
             custom_icon = custom_icon_bus
        tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
        markers.append(tmp)     
      #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(Stops)]
      newMap = dl.Map([dl.TileLayer(), dl.ScaleControl(position="topright"), dl.Polyline(positions=RoutesCoords, pathOptions={'weight':10})] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
      return [newMap]


@app.callback([Output("outdata", "children",allow_duplicate=True), Output('internal-value_stops','data',allow_duplicate=True),Output('map','children',allow_duplicate=True)],
              [State('internal-value_stops','data'),
               State('internal-value_coworking','data')],
              [Input("match_stops", "n_clicks")]
              )
def match_stops(St,Cow,Nclick):
    if Nclick > 0:
      print('matching stops...')  
      bus_stops = []
      out = ''
      for i_st in range(len(St)):
        if Cow[i_st] == 0:  
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
      markers = []
      for i, pos in enumerate(St): 
           if Cow[i] == 1:
               custom_icon = custom_icon_coworking
               #print('setting coworking icon...')
           else:
               custom_icon = custom_icon_bus
           tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
           markers.append(tmp)
      #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
      newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
      return [len(St),St,newMap]


@app.callback([Output("outdata", "children",allow_duplicate=True), 
               Output('internal-value_stops','data',allow_duplicate=True),
               Output('internal-value_coworking','data',allow_duplicate=True),
               Output('map','children',allow_duplicate=True)],
              [State('internal-value_stops','data'),
               State('internal-value_coworking','data')],
              [Input('map','clickData')]
              )
def add_marker(St,Cow,clickd):
       marker_lat = clickd['latlng']['lat']
       marker_lon = clickd['latlng']['lng']
       St.append((marker_lat,marker_lon))
       Cow.append(0)
       out=''
       for i in range(len(St)):
           out = out + str(St[i][0]) + ', ' + str(St[i][1]) + '; '
       #markers = [dl.Marker(dl.Tooltip("double click on Marker after drag to update its position"), position=pos, id="marker{}".format(i), draggable=True) for i, pos in enumerate(St)]
       #Layer_group = dl.LayerGroup(markers, id="markers_group")
       #Layer_group = dl.LayerGroup(markers, id={"type": "markers_group", "index": 0})
       #markers = [dl.Marker(id={'type': 'marker', 'index': key}, position=data[key]) for key in data]
       #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
       markers = []
       for i, pos in enumerate(St): 
           if Cow[i] == 1:
               custom_icon = custom_icon_coworking
               #print('setting coworking icon...')
           else:
               custom_icon = custom_icon_bus
           tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
           markers.append(tmp)    

       newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
       return [out,St,Cow,newMap]


@app.callback([Output("outdata", "children",allow_duplicate=True),
               Output('internal-value_stops','data',allow_duplicate=True),
               Output('internal-value_coworking','data',allow_duplicate=True),
               Output("choose_stop_action", "value",allow_duplicate=True),
               Output('map','children',allow_duplicate=True)],
              [State('internal-value_stops','data'), 
               State('internal-value_coworking','data'), 
               State('choose_stop_action',"value")],
              [Input({"type": "marker", "index": ALL},"n_clicks")],
              prevent_initial_callbacks=True)
def change_marker(St, Cow, stop_operation, *args):

    marker_id = callback_context.triggered[0]["prop_id"].split(".")[0].split(":")[1].split(",")[0]
    n_clicks = callback_context.triggered[0]["value"]
    #print('marker id?:', marker_id)
    print('requested Marker Operation:')
    print(stop_operation)
       
    if stop_operation == "DM":      
       del St[int(marker_id)]
       del Cow[int(marker_id)]
       
       markers = []
       for i, pos in enumerate(St): 
           if Cow[i]==1:
               custom_icon = custom_icon_coworking
           else:
               custom_icon = custom_icon_bus
           tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
           markers.append(tmp)    
       newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
       #markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
       #newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
       #              center=center, zoom=12, id="map",
       #              style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
       return ['Stop deleted!',St,Cow,' ',newMap]

    if stop_operation == "SO":
        print()
        print()
        tmp = St[int(marker_id)]
        St.pop(int(marker_id))
        Cow.pop(int(marker_id))
        St.insert(0, tmp)
        Cow.insert(0, 0)
        print('list modified!')
        print()
        
        markers = [dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon_bus, id={'type': 'marker', 'index': i}) for i, pos in enumerate(St)]
        newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
        return ['Origin set!',St,Cow,' ',newMap]
        
    if stop_operation == "SC":
       markers = []
       for i, pos in enumerate(St): 
           if i == int(marker_id) or Cow[i]==1:
               custom_icon = custom_icon_coworking
               Cow[i] = 1               
           else:
               custom_icon = custom_icon_bus
           tmp = dl.Marker(dl.Tooltip("Double click on Marker to remove it"), position=pos, icon=custom_icon, id={'type': 'marker', 'index': i})    
           markers.append(tmp)    
       newMap = dl.Map([dl.TileLayer(),dl.ScaleControl(position="topright")] + markers,
                     center=center, zoom=12, id="map",
                     style={'width': '100%', 'height': '80vh', 'margin': "auto", "display": "block"})
       return ['Stop deleted!',St,Cow,' ',newMap]
       

if __name__ == '__main__':
    #app.run_server(Debug=True)
    #app.run_server(port=8058,Debug=True)
    app.run_server(port=8058)
    #app.run_server(port=8058,host= '0.0.0.0')