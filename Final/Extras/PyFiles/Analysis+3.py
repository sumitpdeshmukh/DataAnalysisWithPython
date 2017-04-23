
# coding: utf-8

# # Cost analysis on weekend trips to major US cities from Boston

# In[ ]:

import requests
import json
import os
import glob
from os.path import basename
from os.path import splitext
import datetime
import calendar
import pandas as pd

import plotly
plotly.offline.init_notebook_mode()

import plotly.offline as offline
import plotly.graph_objs as go

api_key = "apiKey=" + os.getenv("sky_api_key")


# - Read BostonFlightsData to get all the flights that start from Boston to any location in United States.

# In[ ]:

flights = pd.read_csv('../Output/BostonFlightsData.csv', low_memory=False)


# - SkyScanner API to get the Quote on Prices in USD for a particular route

# In[ ]:

sky_domain = 'http://partners.api.skyscanner.net/apiservices/browsequotes/v1.0/US/USD/en-US/'
sky_api_key = api_key
def geturl(source, dest, outb_date="__", inb_date="__"):    
    return sky_domain + source + "/" + dest + "/" + outb_date + "/" + inb_date + "?" + sky_api_key 

flights['URL'] = flights.apply(lambda x: geturl(x.Source_Airport, x.Destination_Airport) , axis=1)


# - This script will give Start and End date for the quote prices we are interestd in
# - It will calulate date after 6 months from start date
# - Start day needs to be a Friday, because we are planning weekend trips where we start on Friday and Return on Sunday

# In[ ]:

# Add given months to source date
def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

# Start day needs to be a Friday, Check if it is a friday or not or get next Friday
d  = datetime.date.today()
while d.weekday() != 4:
    d += datetime.timedelta(1)

start_date = d
end_date = add_months(start_date, 6)


# - Get all weekend dates for Departure and Return dates

# In[ ]:

depart_dates = []
return_dates = []
delta = datetime.timedelta(days=1)
d = start_date
weekend = set([4, 6])

#Create arrays dates having of Start day and Return day
while d <= end_date:
    if d.weekday() == 4:
        depart_dates.append(d)
    elif d.weekday() == 6:
        return_dates.append(d)
    d += delta


# In[ ]:

def createdir(path): # Function to create directory if it does not exist already
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except OSError as exception:
        return False


download_dir = "../Output/QuotesData_" + datetime.date.today().strftime("%Y_%m_%W") + "/" 


def checkofflinedata():
    if os.path.exists(download_dir):
        return True
    else:
        return False


# - This will check if the Quotes data is already present for that week or not
# - In the Free version signup with Sky scanner API we are anyway hitting cached prices which will be a week old. So there is no point in getting new data daily. I am querying for new data weekly.

# In[ ]:

def DownloadData():
    if (checkofflinedata() == False):
        createdir(download_dir)
        for _, rows in flights.iterrows():    
            outdir = download_dir + rows.Source_Airport + "_" + rows.Destination_Airport
            createdir(outdir)
            for dep, arr in zip(depart_dates, return_dates):
                url = geturl(rows.Source_Airport, rows.Destination_Airport, dep.strftime("%Y-%m-%d"), arr.strftime("%Y-%m-%d"))
                response = requests.get(url)
                if response.status_code is 200:
                    outputdir = outdir + "/" + str(dep.year) + "/" + str(dep.month)
                    createdir(outputdir)
                    try:
                        with open(outputdir + "/" + str(dep.isocalendar()[1]) + ".json", "w") as jsonfile:
                            json.dump(response.json(), jsonfile, indent=4, sort_keys=True)
                    except:
                        print("Failed in dumping {0}".format(outputdir + "/" + str(dep.isocalendar()[1]) + ".json"))
                else:
                    print("Are you online? If yes, then your url seems to be fuzzy or skyscanner went down under.")
DownloadData()


# - This part will read all the download data and create a new Quotes Dataframe having prices for each route

# In[ ]:

quotes_df = pd.DataFrame()
for _, rows in flights.iterrows():
    outdir = download_dir + rows.Source_Airport + "_" + rows.Destination_Airport
    weeks = []
    avg_price = []
    d = start_date
    while d <= end_date:
        outputdir = outdir + "/" + str(d.year) + "/" + str(d.month)
        if os.path.exists(outputdir):
            json_files = glob.glob(outputdir + '/*.json')
            if json_files is not None:
                for i in range(len(json_files)):
                    min_price = 0
                    cnt = cnt_d = cnt_r = 0
                    dep_price = ret_price = 0
                    with open(json_files[i]) as datafile:
                        quote_data = json.load(datafile)
                        for x in range(0, len(quote_data["Quotes"])):
                            json_data = quote_data["Quotes"][x]
                            try :
                                if "OutboundLeg" in json_data and "InboundLeg" in json_data: 
                                    if json_data["OutboundLeg"] and json_data["InboundLeg"] is not None:                                
                                        min_price += json_data["MinPrice"]
                                        cnt += 1
                                        continue;
                                if "OutboundLeg" in json_data:
                                    if json_data["OutboundLeg"] is not None:
                                        dep_price += json_data["MinPrice"]
                                        cnt_d += 1
                                if "InboundLeg" in json_data:
                                    if json_data["InboundLeg"] is not None:
                                        ret_price += json_data["MinPrice"]
                                        cnt_r += 1
                                    
                            except:
                                print(json_files[i])
                                
                        base = basename(json_files[i])
                        weeks.append(str(d.year)+ '-' +splitext(base)[0])
                        if cnt_d > 0 and cnt_r > 0 and cnt_d == cnt_r:
                            min_price += (dep_price/cnt_d) + (ret_price/cnt_r)
                            cnt += ((cnt_d + cnt_r)/ 2)
                        if cnt != 0:
                            avg_price.append((min_price/cnt))
                        else:
                            avg_price.append(0)
                            
        d += datetime.timedelta(days=31)
    
    df = pd.DataFrame({"Weekend_Date" : weeks, "Average_Price" : avg_price, "Source" : rows.Source_Airport,
                       "Destination" : rows.Destination_Airport})
    quotes_df = quotes_df.append(df)


# In[ ]:

quotes_df.to_csv("../Output/QuotesOnUSDestinations.csv", index=False)
quotes_df.head()


# - Now we can plot this Data from Boston to Top US cities
# - Get data from Boston to Denver and plot

# In[ ]:

bos_den = quotes_df[quotes_df['Destination'] == 'DEN']
bos_den['Weekend_Date'] = bos_den.apply(lambda x: datetime.datetime.strptime(x.Weekend_Date + '-0', "%Y-%W-%w"), axis=1)
bos_den['Average_Price'] = bos_den.apply(lambda x: bos_den['Average_Price'].mean() 
                                         if x.Average_Price == 0 else x.Average_Price, axis=1)


# - Get data from Boston to Las Vegas and plot

# In[ ]:

bos_lax = quotes_df[quotes_df['Destination'] == 'LAX']
bos_lax['Weekend_Date'] = bos_lax.apply(lambda x: datetime.datetime.strptime(x.Weekend_Date + '-0', "%Y-%W-%w"), axis=1)
bos_lax['Average_Price'] = bos_lax.apply(lambda x: bos_lax['Average_Price'].mean() 
                                         if x.Average_Price == 0 else x.Average_Price, axis=1)


# - Get data from Boston to San Francisco and plot

# In[ ]:

bos_sfo = quotes_df[quotes_df['Destination'] == 'SFO']
bos_sfo['Weekend_Date'] = bos_sfo.apply(lambda x: datetime.datetime.strptime(x.Weekend_Date + '-0', "%Y-%W-%w"), axis=1)
bos_sfo['Average_Price'] = bos_sfo.apply(lambda x: bos_sfo['Average_Price'].mean() 
                                         if x.Average_Price == 0 else x.Average_Price, axis=1)


# Get data from Boston to Houston and plot

# In[ ]:

bos_iah = quotes_df[quotes_df['Destination'] == 'IAH']
bos_iah['Weekend_Date'] = bos_iah.apply(lambda x: datetime.datetime.strptime(x.Weekend_Date + '-0', "%Y-%W-%w"), axis=1)
bos_iah['Average_Price'] = bos_iah.apply(lambda x: bos_iah['Average_Price'].mean() 
                                         if x.Average_Price == 0 else x.Average_Price, axis=1)


# - Get data from Boston to Phoenix and plot

# In[ ]:

bos_phx = quotes_df[quotes_df['Destination'] == 'PHX']
bos_phx['Weekend_Date'] = bos_phx.apply(lambda x: datetime.datetime.strptime(x.Weekend_Date + '-0', "%Y-%W-%w"), axis=1)
bos_phx['Average_Price'] = bos_phx.apply(lambda x: bos_phx['Average_Price'].mean() 
                                         if x.Average_Price == 0 else x.Average_Price, axis=1)


# - Plotting all trip prices from Boston to Major US cities and observe the prices

# In[ ]:

data = [
        go.Scatter(
            x = bos_den.Weekend_Date,
            y = bos_den.Average_Price,
            name = 'Denver'
        ),
        go.Scatter(
            x = bos_lax.Weekend_Date,
            y = bos_lax.Average_Price,
            name = 'Los Angeles'
        ),
        go.Scatter(
            x = bos_sfo.Weekend_Date,
            y = bos_sfo.Average_Price,
            name = 'San Francisco'
        ),
        go.Scatter(
            x = bos_iah.Weekend_Date,
            y = bos_iah.Average_Price,
            name = 'Houston'
        ),
        go.Scatter(
            x = bos_phx.Weekend_Date,
            y = bos_phx.Average_Price,
            name = 'Phoenix'
        )]

layout = go.Layout(             
    title="Weekend Return Trip Prices for major US cities from Boston", 
    xaxis=dict(                 
        title="Weekend dates"            
    ),
    yaxis= dict(
        title="Return Ticket price in USD"
    ),
)

figure = go.Figure(data=data, layout=layout)

offline.iplot(figure, filename='Weekend Return Trip Prices for major US cities from Boston')


# - From this graph I can plan my weekend trips to each of these cities and save on cost.
# - For instance I will plan my trip to Denver before 28 May 2017 to be able to save on the high prices at any later date.
# - Similarly for San Francisco 11 June 2017 is the cheapest date to travel.

# In[ ]:



