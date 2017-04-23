# Final Exam - Spring 2017 

- I am using [SkyScanner API](https://www.skyscanner.com/) to get data for Airports and Airline Routes of the world. I am enriching this data even further by getting Airports, Routes and Airlines that fly on these routes from [Openflights](http://openflights.org/data.html).

- [Skyscanner Travel APIs](https://skyscanner.github.io/) connect you to access Quotes on Flights, Schedule and Routes data of Future flights. The free version of Skyscanner Business APIs lets you access cache data(Cached weekly from actual data), which is close to live data.

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
- Explore all the unique air routes of the world and which airline served most of these routes.
  - I have plotted all the unique international routes using Matplotlib
  - This gives clear understanding of how Europe is at the heart of International aviation.![All International routes](Output/images/All%20International%20routes.png)
  - Plotting all Europian Routes ![Europe Flights](Output/images/Europe%20flight%20routes.png)
  - Layover airports and Independent destination airports are shown distinctly 
  - Plotting all Domestic routes of United States ![United States domestic flights](Output/images/United%20States%20Domestic%20Flight%20Routes.png)




#### Addtional Instructions to Run the code
- This code has dependecy on following libraries
  - mpl_toolkits.basemap, matplotlib, plotly, geopandas, geopy, shapelyhjfdfjdhf
  - conda install basemap
  - pip install plotly
  - pip install geopandas
  - pip install geopy
  - upgrade matplotlib
