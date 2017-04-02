
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import os
df = pd.read_csv("Data/cricket_matches.csv")


# In[2]:

df = pd.concat([df['home'], df['winner'], df['innings1'], df['innings2'], 
                df['innings1_runs'], df['innings2_runs']], axis=1)


# In[3]:

df = df[df['home'] == df['winner']] # if host team won the game
df1 = df[df['home'] == df['innings1']] # df1 with innings 1 winners
df2 = df[df['home'] == df['innings2']] # df2 with innings 2 winners


# In[4]:

#Calculate average per team
grouped1 = df1.groupby(['home'])
df1_out = pd.DataFrame({'Avg_Score' : grouped1['innings1_runs'].mean()}).reset_index()


# In[5]:

#Calculate average per team
grouped2 = df2.groupby(['home'])
df2_out = pd.DataFrame({'Avg_Score' : grouped2['innings2_runs'].mean()}).reset_index()


# In[6]:

# Add both dataframes and do the same operation again
grouped = df1_out.append(df2_out).groupby('home') 
df_out = pd.DataFrame({'Avg_Score' : grouped['Avg_Score'].mean()}).reset_index()
df_out.head()


# In[7]:

# Dump output to a CSV file
if not os.path.exists("Output"):
    os.makedirs("Output")
df_out.to_csv('Output/cricket_matches_Part1.csv',index=False)

