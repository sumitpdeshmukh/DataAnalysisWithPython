
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import calendar
import os
df = pd.read_csv("Data/vehicle_collisions.csv")


# In[2]:

# Dropping columns that are not required in this part
df.drop(df.columns[4:], axis=1, inplace=True)
df.drop(df.columns[[0,2]], axis=1, inplace=True)


# In[3]:

# Converting string date to datetime object for comparison
df['DATE'] = pd.to_datetime(df['DATE'], format="%m/%d/%y")


# In[4]:

# Trim dataframe rows to the consise year of 2016
# comparison is done using object of dates between '12/31/15' and '1/1/17'
df = df[df['DATE'] > pd.to_datetime('12/31/15', format="%m/%d/%y")]
df = df[df['DATE'] < pd.to_datetime('1/1/17', format="%m/%d/%y")]


# In[5]:

#Convert date representation to Month and rename column
df['DATE'] = pd.DatetimeIndex(df['DATE']).month
df.columns = ['MONTH', 'NYC']


# In[6]:

# Creation of new output Dataframe df_out and calling groupby object's size method to get grouped counts
df_out = pd.DataFrame(df['MONTH'].unique(), columns=['MONTH'], index=np.arange(1,13))
df_out['NYC'] = df.groupby('MONTH').size()


# In[7]:

# A temporary frame to get 'MANHATTAN' only records and their monthwise count
temp_df = df[df['NYC'] == 'MANHATTAN']
df_out['MANHATTAN'] = temp_df.groupby('MONTH').size()
df_out['PERCENTAGE'] = df_out['MANHATTAN'] / df_out['NYC']


# In[8]:

# Reorder of columns and converting numerical month to String representation
df_out = df_out[['MONTH','MANHATTAN', 'NYC','PERCENTAGE']]
df_out['MONTH'] = df_out['MONTH'].apply(lambda x: calendar.month_abbr[x])
df_out.head()


# In[9]:

# Dump output to a CSV file
if not os.path.exists("Output"):
    os.makedirs("Output")
df_out.to_csv('Output/Vehicle_collisions_Part1.csv',index=False)


# In[ ]:



