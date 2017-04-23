# Final Exam - Spring 2017 

- I am using [SkyScanner API](https://www.skyscanner.com/) to get data for Airports and Airline Routes of the world. I am enriching this data even further by getting Airports, Routes and Airlines that fly on these routes from [Openflights](http://openflights.org/data.html).

- [Skyscanner Travel APIs](https://skyscanner.github.io/slate/#getting-started) connect you to access Quotes on Flights, Schedule and Routes data of Future flights. The free version of Skyscanner Business APIs lets you access cache data(Cached weekly from actual data), which is close to live data.

- [OpenFlights](http://openflights.org/data.html) is a tool that lets you map your flights around the world, search and filter them in all sorts of interesting ways. It's also the name of the open-source project to build the tool.
  - As of January 2017, the OpenFlights Airports Database contains over 10,000 airports.
  - As of January 2012, the OpenFlights Airlines Database contains 5888 airlines.
  - As of January 2012, the OpenFlights/Airline Route Mapper Route Database contains 59036 routes between 3209 airports on 531 airlines spanning the globe
---
## Major Goals:
- I have performed 3 major analysis on this combined data. They are briefly described as below.
  1) Explore all the unique air routes of the world and which airline served most of these routes.
  2) Explore which Airports are the busiest in terms of number of routes they serve
  3) Perfrom a cost analysis on return trips over every weekend planned from Boston to major US cities for next 6 months.  

---

## Section 1: Collect Data
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;[Data Collection.py](Extras/PyFiles/Data%2BCollection%2Band%2BStore.py)&emsp;[Data Collection.ipynb](Analysis/Data%20Collection%20and%20Store.ipynb)
- **Step 1**
  - I need to have a list of Airports first to meet my end goals of this exercise.
  - Skyscanner Geo API gives data for all the airports when we query
  - `API ENDPOINT`
  ```sh
  GET "http://partners.api.skyscanner.net/apiservices/geo/v1.0?apiKey={apiKey}"
  ```
  - Response expected is like

  ```json
  {
    "Continents": [
      {
        "Countries": [
          {
            "CurrencyId": "AFN",
            "Regions": [],
            "Cities": [
              {
                "SingleAirportCity": true,
                "Airports": [
                  {
                    "CityId": "BINA",
                    "CountryId": "AF",
                    "Location": "67.823611, 34.804167",
                    "Id": "BIN",
                    "Name": "Bamiyan"
                  }
                ],
                "CountryId": "AF",
                "Location": "67.823611, 34.804167",
                "IataCode": "BIN",
                "Id": "BINA",
                "Name": "Bamiyan"
              },
              ...
            ]
          },
          ...
        ]
      },
      ...
    ]
   }
  ```

  - I have combined [Airports Data](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat) from OpenFlights with these Airports and removed duplicate records.
  - This will result in following

  Airport | City | Continent | Country | IATA/FAA | Latitude | Longitude | Airports_ID
  --- | --- | --- | --- | --- | --- | --- | ---
  Bamiyan | Bamiyan | Asia | Afghanistan | BIN | 34.804167 | 67.823611 | 1
  Bost | Bost | Asia | Afghanistan | BST | 31.55 | 64.366667 | 2
  Chakcharan | Chakcharan | Asia | Afghanistan | CCN | 34.533333 | 65.266667 | 3
  Farah | Farah | Asia | Afghanistan | FAH | 32.366667 | 62.116667 | 4

- **Step 2**
  - Using these airports we can query skyscanner API to get routes originating from these airports 
  - `API ENDPOINT`
  ```sh
  GET   /browseroutes/v1.0/{country}/{currency}/{locale}/{originPlace}/{destinationPlace}/{outboundPartialDate}/{inboundPartialDate}
  ```
  - Response expected is like

  ```
  {
    "Routes": [
      {
        "OriginId": 1811,
        "DestinationId": 1845,
        "QuoteIds": [
          1,
          2
        ],
        "Price": 326,
        "QuoteDateTime": "2016-11-13T01:30:00"
      },
      {
        "OriginId": 1811,
        "DestinationId": 929,
        "QuoteIds": [
          3
        ],
        "Price": 150,
        "QuoteDateTime": "2016-11-09T17:44:00"
      },
    ...
    ],
  ```

  - I have combined [Airline Routes](https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat) from OpenFlights with Skyscanner routes and removed duplicate routes.
  - This will result in following

  Airline_Code | Airline_ID | Airline_Name | Destination_Airport | Destination_Airport_ID | Source_Airport | Source_Airport_ID
  --- | --- | --- | --- | --- | --- | ---
  AI | 218 | Air India | DEL | 3093 | BBI | 3042
  AI | 218 | Air India | IXZ | 3146 | BBI | 3042
  AI | 218 | Air India | DEL | 3093 | BDQ | 3001
  AI | 218 | Air India | BOM | 2997 | BHO | 3002
  AI | 218 | Air India | DEL | 3093 | BHO | 3002

- **Step 3**
  - I have used [Airlines Data](https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat) from OpenFlights.
  - This will result in following

  Airline_ID | Airline_Name | IATA | Airline_HQ | Active
  --- | --- | --- | --- | ---
  1 | Air India | AI | India | Y
  2 | Delta Airways | nan | United States | Y
  3 | British Airways | BA | United Kingdom | Y
  4 | 2 Sqn No 1 Elementary Flying Training School | nan | United Kingdom | N
  5 | Nippon Airways | nan | Japan | Y

  **`The combined data from all these small datasets is used henceforth for all the Analysis.`**

---
## Section 2: Storing Data
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;[Data Store.py](Extras/PyFiles/Data%2BCollection%2Band%2BStore.py)&emsp;[Data Store.ipynb](Analysis/Data%20Collection%20and%20Store.ipynb)
- Airports Data
  - The Airports data from SkyScanner API is a static data which will rarely change.
  - I have stored this data in a folder named `Places_<YYYY-mm-WW>`. For current week once the data is downloaded no new data will be fetched.
  - While reading this data only current week folder will be read from and combined with Open Flights airport.csv dataset as stated earlier
  
- Routes Data
  - The Routes for each Airport in the previous dataset are accessed from SkyScanner API and stored in a folder named `Routes_<YYYY-mm-WW>`. For current week once the data is downloaded no new data will be fetched.
  - While reading this data only current week folder will be read from and combined with Open Flights routes.csv dataset as stated earlier
  
- Data From Open Flight Airlines is a static CSV file. All these small datasets are combined to generate huge dataset with 25 columns and 100k plus rows and is stored as `MultiRoutesData.csv` and `UniqueRoutesData.csv`

---

## Section 3: Analysis 1
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;[Analysis 1.py](Extras/PyFiles/Analysis%2B1.py)&emsp;[Analysis 1.ipynb](Analysis/Analysis%201.ipynb)
- Explore all the unique air routes of the world and which airline served most of these routes.
  - I have plotted all the unique international routes using Matplotlib
  - This gives clear understanding of how Europe is at the heart of International aviation.![All International routes](Output/images/All%20International%20routes.png)
  - Plotting all Europian Routes ![Europe Flights](Output/images/Europe%20flight%20routes.png)
  - Layover airports and Independent destination airports are shown distinctly 
  - Plotting all Domestic routes of United States ![United States domestic flights](Output/images/United%20States%20Domestic%20Flight%20Routes.png)
  - Bar plot of airlines that serve highest routes among all the routes ![Airlines and Routes they serve](Output/images/Airlines%20and%20Number%20of%20Routes%20they%20serve.png)
  
---

## Section 4: Analysis 2
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;[Analysis 2.py](Extras/PyFiles/Analysis%2B2.py)&emsp;[Analysis 2.ipynb](Analysis/Analysis%202.ipynb)
- Explore which Airports are the busiest in terms of number of routes they serve
  - This plot has circular markers proportional to the number of routes those airports serve. ![Airports serving major routes](Output/images/Major%20Airports%20According%20to%20Serving%20Routes.png)
  - This is an interactive plot of marker sizes arranged according to the the number of routes they serve. ![Interactive Representation of number of routes served by an airport](Output/images/Major%20hub%20airports%20of%20the%20world.png)
  - Interaction can be observed on the Jupyter notebook
  - This bar plot shows airports and routes they serve. ![Airports and Routes they serve](Output/images/Airports%20and%20Routes%20they%20serve.png)
  
---

## Section 5: Analysis 3
&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;[Analysis 3.py](Extras/PyFiles/Analysis%2B3.py)&emsp;[Analysis 3.ipynb](Analysis/Analysis%203.ipynb)
- Perfrom a cost analysis on return trips over every weekend planned from Boston to major US cities for next 6 months.
  - We need to fetch Quote prices in order to perform this analysis.
  - `API ENDPOINT`
  ```sh
  GET /browsequotes/v1.0/{country}/{currency}/{locale}/{originPlace}/{destinationPlace}/{outboundPartialDate}/{inboundPartialDate}
  ```
  - Response expected is like
  ```JSON
  {
  "Quotes": [
    {
      "QuoteId": 1,
      "MinPrice": 381,
      "Direct": true,
      "OutboundLeg": {
        "CarrierIds": [
          470
        ],
        "OriginId": 68033,
        "DestinationId": 42833,
        "DepartureDate": "2017-02-03T00:00:00"
      },
      "InboundLeg": {
        "CarrierIds": [
          470
        ],
        "OriginId": 42833,
        "DestinationId": 68033,
        "DepartureDate": "2017-02-06T00:00:00"
      },
      "QuoteDateTime": "2016-11-09T21:20:00"
    },
  ...
  ],
  ```
  - This JSON data is read and added into existing dataframe to get prices for every route.
  
  Average_Price | Destination | Source | Weekend_Date
  --- | --- | --- | ---
  434.5 | DEN | BOS | 2017-04-30 00:00:00
  354.0 | DEN | BOS | 2017-05-07 00:00:00
  350.0 | DEN | BOS | 2017-05-14 00:00:00
  430.0 | DEN | BOS | 2017-05-21 00:00:00
  437.5 | DEN | BOS | 2017-05-28 00:00:00

  - This is a plot of weekend return trip prices from Boston to Major cities of United states
  - Prices used in this plot has close resemblance with actual prices of that trip, since the cached data is just weeks old.
  - Using the observations from this line plot we can safely establish that it matters when we plan plan weekend trips to which cities.
  - We can see that flying to Denver, United States from Boston should be planned on either `May 14 2017` or `June 04 2017` to utilise the cheapest fare opportunity.![Weekend Trips to major cities of United States](Output/images/Weekend%20Return%20Trip%20Prices.png)
  - Similary on `June 11 2017` we can plan a trip to San Francisco than any other destination. The rates for San Francisco are cheapest on this weekend and though we are flying farther we will pay the least to have a trip there. 
---




#### Addtional Instructions to Run the code in this repository
- Plotly graphs that are not rendered can be viewed after clicking the external nbviewer link dispalyed at the top right corner of the Jupyter Notebook.
- This code has dependecy on following libraries
  - mpl_toolkits.basemap, matplotlib, plotly, geopandas, geopy, shapelyhjfdfjdhf
  - conda install basemap
  - pip install plotly
  - pip install geopandas
  - pip install geopy
  - upgrade matplotlib

- All the scripts in this repository by default check for `<YYYY-MM-{Current Weeknumber of the given year}>` folder. If that is found no new downloading starts but if it is not there it will automatically start downloading the required data.
- Airports Data downloading process does not take more than few seconds to download.
- Routes data downloading from SkyScanner API takes considerable amount of time(30 to 45 minutes).
- Quotes data downloading in Analysis 3 from SkyScanner API takes about (10 to 15 minutes) to download all the data for routes originating at Boston.
  - One hack that you can do to save time in downloading is to rename the existing folder `<YYYY-MM-WW>` (where WW is week number of the year.) to `<YYYY-MM-{Current Weeknumber of the given year}>`
  - The cached data from SkyScanner rarely changes within one week, so you will not lose much with this hack.
