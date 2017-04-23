
# coding: utf-8

# # SkyScanner Flight Data / OpenFlights Data
# 
# - This python script  will download and store [SkyScanner](https://www.skyscanner.com/) Flight Data
# - [Skyscanner Travel APIs](https://skyscanner.github.io/) connect you to access Quotes on Flights, Schedule and Routes data of Future flights.
# - The free version of Skyscanner Business APIs lets you access cache data(Cached weekly from actual data), which is close to live data.
# 
# 
# [OpenFlights](http://openflights.org/data.html) is a tool that lets you map your flights around the world, search and filter them in all sorts of interesting ways. It's also the name of the open-source project to build the tool.
# 
# - As of January 2017, the OpenFlights Airports Database contains over 10,000 airports.
# - As of January 2012, the OpenFlights Airlines Database contains 5888 airlines.
# - As of January 2012, the OpenFlights/Airline Route Mapper Route Database contains 59036 routes between 3209 airports on 531 airlines spanning the globe

# In[2]:

import requests
import json
import os
import glob

import datetime

import pandas as pd
import numpy as np
from geopy.distance import vincenty # Install this
import plotly
plotly.offline.init_notebook_mode()

import plotly.offline as offline
import plotly.graph_objs as go
from IPython.display import Image


# - Data will be downloaded for Places and Routes for once a week. So if you dont want to spend time to download the data use a hack like renaming these folders to "YYYY-MM-Weeknumber" to save time

# In[3]:

sky_domain = 'http://partners.api.skyscanner.net/apiservices/'
sky_api_key = 'apiKey=' + os.getenv("sky_api_key")

raw_data = '../Data/raw_data/'    
download_dir_Places = raw_data + "Places_" + datetime.date.today().strftime("%Y_%m_%W") + "/"
download_dir_Routes = raw_data + "Routes_" + datetime.date.today().strftime("%Y_%m_%W") + "/"

#API to download Airports data from SkyScanner
def getPlacesurl():    
    return sky_domain + "geo/v1.0?" + sky_api_key

#API to download Routes data from SkyScanner
def getRoutesurl(source,dest):    
    return sky_domain + "browseroutes/v1.0/US/USD/en-US/" + source + "/" + dest + "/anytime/?" + sky_api_key

# Function to create directory if it does not exist already
def createdir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except OSError as exception:
        return False

def checkOfflineData(path):
    if os.path.exists(path):
        return True
    else:
        return False
 


# ## Airports
# 
# - This script will download data only if data for that week is not already present

# In[4]:

#Only download if not already present
def DownloadAirportsData():
    if (checkOfflineData(download_dir_Places) == False):
        createdir(download_dir_Places)
        response = requests.get(getPlacesurl())
        if response.status_code is 200:
            try:
                with open(download_dir_Places + "/" + "Places.json", "w") as jsonfile:
                    json.dump(response.json(), jsonfile, indent=4, sort_keys=True)
            except:
                print("Failed in dumping Places.json")
                
DownloadAirportsData()


# - Sample Places.Json file has following structure{
#   "Continents": [
#     {
#       "Countries": [
#         {
#           "CurrencyId": "AFN",
#           "Regions": [],
#           "Cities": [
#             {
#               "SingleAirportCity": true,
#               "Airports": [
#                 {
#                   "CityId": "BINA",
#                   "CountryId": "AF",
#                   "Location": "67.823611, 34.804167",
#                   "Id": "BIN",
#                   "Name": "Bamiyan"
#                 }
#               ],
#               "CountryId": "AF",
#               "Location": "67.823611, 34.804167",
#               "IataCode": "BIN",
#               "Id": "BINA",
#               "Name": "Bamiyan"
#             },
#             ...
#           ]
#         },
#         ...
#       ]
#     },
#     ...
#   ]
# }

# In[5]:

alldata = []
# Read all data from the downloaded file and store it in a Dataframe/CSV
def ReadAirportsData():
    with open(download_dir_Places + "/" + "Places.json") as jsfile:
        placesdata = json.load(jsfile)
        for cont in range(0, len(placesdata["Continents"])):
            for cnty in range(0, len(placesdata["Continents"][cont]["Countries"])):
                for city in range(0, len(placesdata["Continents"][cont]["Countries"][cnty]["Cities"])):
                    for airp in range(0, len(placesdata["Continents"][cont]["Countries"][cnty]["Cities"][city]["Airports"])):
                        Airport = placesdata["Continents"][cont]["Countries"][cnty]["Cities"][city]["Airports"][airp]
                        alldata.append({'Airport': Airport['Name'] , 
                                        'City' : placesdata["Continents"][cont]["Countries"][cnty]["Cities"][city]['Name'], 
                                        'Country': placesdata["Continents"][cont]["Countries"][cnty]['Name'] ,
                                        'IATA/FAA' : Airport['Id'],
                                        'Longitude': Airport['Location'].split(', ')[0],
                                        'Latitude': Airport['Location'].split(', ')[1],
                                        'Continent': placesdata["Continents"][cont]['Name']})

ReadAirportsData()
AirportsSky = pd.DataFrame(alldata)
AirportsSky.to_csv(raw_data+'AirportsSkyScanner.csv',index=False)
AirportsSky.head()


# - Skyscanner API has 4127 Unique Airports. Let us enrich this data even further by using More Airports Data from Openflights
# - This Airport Data is downloaded from [OpenFlights Airports](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat) and stored at ../Data/raw_data/Airports.csv

# In[6]:

columns = ["Airport_ID", "Airport", "City", "Country", "IATA/FAA", "ICAO","Latitude", "Longitude", "Altitude", 
           "Timezone", "DST", "Continent"]
Airportsopf = pd.read_csv(raw_data + 'airports.csv', sep=",", na_values=['\\N'], names=columns)
Airportsopf.drop(['ICAO', 'Altitude', 'Timezone','DST', 'Airport_ID'], axis=1, inplace=True)

#Combining both Dataframes into one Airports Dataframe
Airports = AirportsSky.append(Airportsopf)

#Dropping duplicate rows of the same airport from combined dataframe
Airports.drop_duplicates(subset=['IATA/FAA'], inplace=True)

Airports = Airports.reset_index(drop=True)
Airports['Airports_ID'] = np.arange(1, len(Airports) + 1)
Airports = Airports.dropna(subset=['IATA/FAA'])
Airports.head()


# ## Routes
# - This script will download Routes data only if data for that week is not already present
# - If download starts this routine will take close to 45 minutes to download all the data
# - Total hits to the SkyScanner API will be equal to number of airports (6253) in Airports Dataframe

# In[6]:

def DownloadRoutesData(source, destination, count):
    createdir(download_dir_Routes)
    response = requests.get(getRoutesurl(source, destination))
    if response.status_code is 200 and response.json() is not None:
        if len(response.json()['Routes']) > 0 and len(response.json()['Quotes']) > 0:
            try:
                with open(download_dir_Routes + "/" + source +".json", "w") as jsonfile:
                    json.dump(response.json(), jsonfile, indent=4, sort_keys=True)
            except:
                print("Failed in dumping {0}.json".format(source))
        else:
            print("No outbound route for {0} {1} ".format(source, count))
cnt = 1

if (checkOfflineData(download_dir_Routes) == False):
    for airport in Airports['IATA/FAA'].unique():
        DownloadRoutesData(airport, "anywhere", cnt)
        cnt += 1


# - Sample Routes.Json file has following structure
# {
#   "Routes": [
#     {
#       "OriginId": 1811,
#       "DestinationId": 1845,
#       "QuoteIds": [
#         1,
#         2
#       ],
#       "Price": 326,
#       "QuoteDateTime": "2016-11-13T01:30:00"
#     },
#     {
#       "OriginId": 1811,
#       "DestinationId": 929,
#       "QuoteIds": [
#         3
#       ],
#       "Price": 150,
#       "QuoteDateTime": "2016-11-09T17:44:00"
#     },
#   ...
#   ],
#   "Quotes": [
#     {
#       "QuoteId": 1,
#       "MinPrice": 381,
#       "Direct": true,
#       "OutboundLeg": {
#         "CarrierIds": [
#           470
#         ],
#         "OriginId": 68033,
#         "DestinationId": 42833,
#         "DepartureDate": "2017-02-03T00:00:00"
#       },
#       "InboundLeg": {
#         "CarrierIds": [
#           470
#         ],
#         "OriginId": 42833,
#         "DestinationId": 68033,
#         "DepartureDate": "2017-02-06T00:00:00"
#       },
#       "QuoteDateTime": "2016-11-09T21:20:00"
#     },
#   ...
#   ],

# In[7]:

allroutedata = []
# Read all data from the downloaded JSON files and store it in a Dataframe/CSV
def ReadAllRoutesData():
    if os.path.exists(download_dir_Routes):
        json_files = glob.glob(download_dir_Routes + '*.json')
        for i in range(len(json_files)):
            with open(json_files[i]) as datafile:
                route_data = json.load(datafile)
                for r in range(0, len(route_data["Quotes"])):
                    source_id = route_data["Quotes"][r]['OutboundLeg']['OriginId']
                    desti_id = route_data["Quotes"][r]['OutboundLeg']['DestinationId']
                    outbair_id = np.nan
                    if (len(route_data["Quotes"][r]['OutboundLeg']['CarrierIds']) > 0):
                        outbair_id = route_data["Quotes"][r]['OutboundLeg']['CarrierIds'][0]
                    else:
                        continue
                    source_code = ''
                    desti_code = ''
                    airline_name = ''
                    for p in range(0, len(route_data["Places"])):
                        if (route_data["Places"][p]['PlaceId'] == source_id):
                            source_code = route_data["Places"][p]['IataCode']
                        if (route_data["Places"][p]['PlaceId'] == desti_id):
                            desti_code = route_data["Places"][p]['IataCode']
                    
                    for q in range(0, len(route_data["Carriers"])):
                        if (route_data["Carriers"][q]['CarrierId'] == outbair_id):
                            airline_name = route_data["Carriers"][q]['Name']
                            
                    allroutedata.append({'Source_Airport_ID': source_id,
                                         'Source_Airport': source_code,
                                         'Destination_Airport_ID': desti_id,
                                         'Destination_Airport': desti_code,
                                         'Airline_ID': outbair_id,
                                         'Airline_Name': airline_name,
                                        })
ReadAllRoutesData()
SkyRoutes = pd.DataFrame(allroutedata) 
SkyRoutes.drop_duplicates(subset=['Source_Airport', 'Destination_Airport', 'Airline_Name'], inplace=True)
SkyRoutes.reset_index(drop=True, inplace=True)
SkyRoutes.to_csv(raw_data + 'RoutesSkyScanner.csv',index=False)
SkyRoutes.head()


# - Skyscanner API has 47246 Routes. Let us enrich this data even further by using More Routes Data from Openflights
# - This Routes Data is downloaded from [OpenFlights Routes](https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat) and stored at ../Data/raw_data/Routes.csv

# In[8]:

columns= ["Airline_Code", "Airline_ID", "Source_Airport", "Source_Airport_ID","Destination_Airport", 
          "Destination_Airport_ID", "Codeshare", "Stops","Equipment"]
routesopf = pd.read_csv(raw_data + 'routes.csv', sep=",", na_values=['\\N'], names=columns)
routesopf = routesopf.dropna(subset=['Airline_ID', 'Source_Airport_ID', 'Destination_Airport_ID'])
routesopf[['Airline_ID','Source_Airport_ID', 'Destination_Airport_ID']] = routesopf[['Airline_ID','Source_Airport_ID',
                                                                               'Destination_Airport_ID']].astype(int)

routesopf.drop(['Codeshare', 'Stops', 'Equipment'], axis=1, inplace=True)
routesopf.drop_duplicates(subset=['Source_Airport', 'Destination_Airport', 'Airline_ID'], inplace=True)
routesopf.reset_index(drop=True, inplace=True)

#Combining both Dataframes into one Routes Dataframe
Routes = SkyRoutes.append(routesopf)
Routes.drop_duplicates(subset=['Source_Airport', 'Destination_Airport', 'Airline_ID', 'Airline_Name'], inplace=True)
Routes.reset_index(drop=True, inplace=True)
Routes.drop_duplicates(subset=['Destination_Airport', 'Source_Airport', 'Airline_ID'], inplace=True)
Routes.reset_index(drop=True, inplace=True)
Routes.head()


# In[9]:

Routes.info()


# ## Pure Routes
# - There are routes on which multiple airlines fly. Following script will get strict number of unique routes 

# In[10]:

pure_routes = Routes.copy()# Get a copy of Routes Data

# Function to convert and sort alpha numeric string of 4 columns of the dataframe
def createalpha(row):
    mystr = str(row['Source_Airport_ID']) + row['Source_Airport'] + str(row['Destination_Airport_ID'])     + row['Destination_Airport']
    return''.join(sorted(mystr))

# Create new column in this dataframe to get combined alpha numeric string
pure_routes["Temp"] = pure_routes.apply(createalpha, axis=1)

# Dropping duplicates here will eliminate all routes which are served by multiple airlines
pure_routes.drop_duplicates(subset=['Temp'], inplace=True)
pure_routes.drop(['Temp'], axis=1, inplace=True)
pure_routes = pure_routes.reset_index(drop=True)

pure_routes.to_csv(raw_data+'PureRoutesData.csv',index=False)
pure_routes.head()


# In[11]:

pure_routes.info()


# -  If we see count of pure_routes and Routes we can clearly understand the dropping duplicate routes logic in action
# 
# ## Airlines
# 
# - This Airport Data is downloaded from [OpenFlights Airlines](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat) and stored at ../Data/raw_data/Airlines.csv

# In[12]:

columns=["Airline_ID","Airline_Name", "Alias", "IATA", "ICAO", "Callsign", "Airline_HQ", "Active"]
airlines = pd.read_csv(raw_data + 'airlines.csv', sep=",", names=columns, na_values=['\\N'])
airlines.drop(['Alias', 'ICAO', 'Callsign'], axis=1, inplace=True)
airlines.head()


# ## Joining the above 3 Dataframes together
# 
# I have chosen to merge the routes table with the airports twice via an inner join in order to obtain the Source
# Airport and Destination Airport coordinate pairs as well as linking the respective airline information for each route

# In[13]:

airports_routes = pure_routes.merge(Airports, right_on = "IATA/FAA", left_on = 'Source_Airport')        .merge(Airports, right_on="IATA/FAA", left_on="Destination_Airport", suffixes=("_start", "_end"))        .merge(airlines, on="Airline_ID")
airports_routes.drop(['IATA/FAA_start', 'IATA/FAA_end'], axis=1, inplace=True)

multi_ports_routes = Routes.merge(Airports, right_on = "IATA/FAA", left_on = 'Source_Airport')        .merge(Airports, right_on="IATA/FAA", left_on="Destination_Airport", suffixes=("_start", "_end"))        .merge(airlines, on="Airline_ID")
multi_ports_routes.drop(['IATA/FAA_start', 'IATA/FAA_end'], axis=1, inplace=True)


# ## Defining distance calculation function
# I have coordinate pairs of the source and destination airports for each of the journeys, Lets calculate the distance.
# 
# I have chosen to use the vincenty function from the geopy package to calculate the distance, there is also another 
# function (great_circle) that does the same thing only difference is that vincenty assumes Earth to be ellipsoidal while great circle assumes a spherical Earth.
# 
# However, as I have chosen to calcualte distances to a precision of 2 decimal places both functions will return the same result anyway.

# In[14]:

# defining function to apply to merged table
def ellip_dist(row):
    start =  (row["Latitude_start"], row["Longitude_start"])
    end = (row["Latitude_end"], row["Longitude_end"])
    return round((vincenty(start,end)).kilometers,2)

# Rounded outputs to a precision of 2 decimal places
#Choosing specific columns to show.
dispColumns = ["Source_Airport", "Airport_start", "City_start", "Country_start", "Destination_Airport", "Airport_end",
              "City_end", "Country_end", "Distance(km)", "Airline_Name_y"]


# In[15]:

airports_routes["Distance(km)"] = airports_routes.apply(ellip_dist, axis=1)
airports_routes = airports_routes[airports_routes["Distance(km)"] != 0]
airports_routes.to_csv(raw_data+'UniqueRoutesData.csv',index=False)

multi_ports_routes["Distance(km)"] = multi_ports_routes.apply(ellip_dist, axis=1)
multi_ports_routes = multi_ports_routes[multi_ports_routes["Distance(km)"] != 0]
multi_ports_routes.to_csv(raw_data+'MultiRoutesData.csv',index=False)
multi_ports_routes.head()[dispColumns]


# - Lets find the longest and the shortest flight routes 

# In[16]:

distance = airports_routes[airports_routes["Distance(km)"] == airports_routes["Distance(km)"].max()]
distance = distance.append(
    airports_routes[airports_routes["Distance(km)"] == airports_routes["Distance(km)"].min()]).reset_index(drop=True)
distance.head()[dispColumns]


# - Let us visualize this data in order to establish the correctness of the data
# - We will plot the longest and shortest flight paths on world map and observe these routes

# In[17]:

distance['starttext'] = distance['Airport_start'] + '<br>' + distance['City_start']+ '<br>' + distance['Country_start']
distance['endtext'] = distance['Airport_end'] + '<br>' + distance['City_end']+ '<br>'+ distance['Country_end']

airports = [(
    dict(
        type = 'scattergeo',
        locationmode = 'country names',
        lon = distance['Longitude_start'],
        lat = distance['Latitude_start'],
        hoverinfo = 'text',
        text = distance['starttext'],
        mode = 'markers',
        marker = dict( 
            size=10, 
            color='rgb(255, 0, 0)',
            line = dict(
                width=9,
                color='rgba(68, 68, 68, 0)'
            )
            )
    )
)]

airports.append(
        dict(
            type = 'scattergeo',
            locationmode = 'country names',
            lon = distance['Longitude_end'],
            lat = distance['Latitude_end'],
            hoverinfo = 'text',
            text = distance['endtext'],
            mode = 'markers',
            marker = dict( 
                size=6, 
                color='rgb(0, 0, 255)',
                line = dict(
                    width=9,
                    color='rgba(68, 68, 68, 0)'
                )
            )
        )
)
        
flight_paths = []
for i in range( len( distance )):
    flight_paths.append(
        dict(
            type = 'scattergeo',
            locationmode = 'country names',
            lon = [ distance['Longitude_start'][i], distance['Longitude_end'][i] ],
            lat = [ distance['Latitude_start'][i], distance['Latitude_end'][i] ],
            mode = 'lines',
            line = dict(
                width = 3,
                color = 'blue',
            ),
            opacity = 1,
        )
    )

continents = [(
    dict(
        type = 'scattergeo',
        locationmode = 'country names',
        lat = [28.37,39.55,04.23, -35.15, 39.91, 45.27, 51.36, 55.45, -33.24 ],
        lon = [77.13,116.20,18.35, 149.08, -77.02, -75.42, 00.05, 37.35, -70.40],
        hoverinfo = 'text',
        text = ["India", "China","Africa","Australia","USA", "Canada", "UK", "Russia", "South America"],
        mode = 'text',
        textfont={
                "color": "#bc80bd",
                "family": "Droid Serif, serif",
                "size": 18,
            },
        textposition= ["middle center","middle left","top center","top left","bottom left","top center",
                       "middle left","middle right", "top center"],
    )
)]

layout = dict(
        title = 'Longest and shortest flight distances in the world<br>(Hover for airport names)',
        showlegend = False, 
        geo = dict(
            scope='world',
            projection=dict( type='equirectangular' ),
            showland = True,
            landcolor = 'rgb(217, 217, 217)',
            countrycolor = 'rgb(204, 204, 204)',
            resolution = 110
        ),
    )
    
fig = dict( data= flight_paths + airports + continents, layout=layout)
offline.iplot(fig, filename='Longest and shortest distances', image_width=1024,
              image_height=768)


# - Shortest distance plot is not visible at this zoom level, but different marker sizes of Source and Destinations clearly suggest that two locations are in vicinity.
# - This plot clearly suggests that these routes are indeed one of the farthest and shortest routes taken by commercial passenger airlines

# In[13]:

# Displaying image just in case plotly fails to render it in Jupyter notebook
Image('../Output/images/Longest and shortest distances.png')


# In[ ]:



