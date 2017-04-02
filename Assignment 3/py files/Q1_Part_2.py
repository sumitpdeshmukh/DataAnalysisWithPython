
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import os
df = pd.read_csv("Data/vehicle_collisions.csv")


# In[2]:

# Dropping columns that are not required in this part
df.drop(df.columns[24:29], axis=1, inplace=True)
df.drop(df.columns[4:19], axis=1, inplace=True)
df.drop(df.columns[0:3], axis=1, inplace=True)
df.head()


# In[3]:

#Filling all NaN values with 0 and anything else with 1
# This will help in collating results to a single column Vehicles_Involved
df = df.fillna({'VEHICLE 1 TYPE': 0, 'VEHICLE 2 TYPE': 0, 'VEHICLE 3 TYPE': 0, 'VEHICLE 4 TYPE': 0, 
                'VEHICLE 5 TYPE': 0, 'BOROUGH' : 'UNKNOWN'})
df['VEHICLE 1 TYPE'] = df['VEHICLE 1 TYPE'].apply(lambda x: 1 if x != 0 else 0)
df['VEHICLE 2 TYPE'] = df['VEHICLE 2 TYPE'].apply(lambda x: 1 if x != 0 else 0)
df['VEHICLE 3 TYPE'] = df['VEHICLE 3 TYPE'].apply(lambda x: 1 if x != 0 else 0)
df['VEHICLE 4 TYPE'] = df['VEHICLE 4 TYPE'].apply(lambda x: 1 if x != 0 else 0)
df['VEHICLE 5 TYPE'] = df['VEHICLE 5 TYPE'].apply(lambda x: 1 if x != 0 else 0)


# In[4]:

# Create this new column corresponding to number of vehicles invlved in each collision incident
df['Vehicles_Involved'] = df['VEHICLE 1 TYPE'] + df['VEHICLE 2 TYPE'] + df['VEHICLE 3 TYPE'] + df['VEHICLE 4 TYPE'] + df['VEHICLE 5 TYPE']


# In[5]:

df.head()


# In[6]:

wholedf = pd.DataFrame() #Emtpy DataFrame

#For every unique BOROUGH
for location in df['BOROUGH'].unique():
    myseries = df[df['BOROUGH'] == location].groupby('Vehicles_Involved').size() # Get a series of vehicles involved for each borough
    mydf = myseries.to_frame()
    mydf = mydf.transpose() # Converting series to frame and taking transpose
    mydf.columns = ['UNKNOWN_VEHICLES_INVOLVED', 'ONE_VEHICLE_INVOLVED', 'TWO_VEHICLES_INVOLVED', 'THREE_VEHICLES_INVOLVED', 'FOUR_VEHICLES_INVOLVED', 'FIVE_VEHICLES_INVOLVED']
    mydf['MORE_VEHICLES_INVOLVED'] = mydf['FOUR_VEHICLES_INVOLVED'] + mydf['FIVE_VEHICLES_INVOLVED']
    mydf.drop(['FOUR_VEHICLES_INVOLVED', 'FIVE_VEHICLES_INVOLVED'], axis=1, inplace=True)
    mydf['BOROUGH'] = location
    mydf = mydf[['BOROUGH','ONE_VEHICLE_INVOLVED', 'TWO_VEHICLES_INVOLVED', 'THREE_VEHICLES_INVOLVED', 'MORE_VEHICLES_INVOLVED', 'UNKNOWN_VEHICLES_INVOLVED']]
    wholedf = wholedf.append(mydf) # Add this dataframe to final data frame
wholedf.head()


# In[7]:

# Dump output to a CSV file
if not os.path.exists("Output"):
    os.makedirs("Output")
wholedf.to_csv('Output/Vehicle_collisions_Part2.csv',index=False)

