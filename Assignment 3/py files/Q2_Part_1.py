
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np
import os
df = pd.read_csv("Data/employee_compensation.csv")


# In[2]:

# Keeping only required columns in this part
df = pd.concat([df['Organization Group'], df['Department'], df['Total Compensation']], axis=1)
df.head()


# In[3]:

grouped = df.groupby(['Organization Group','Department']) # Grouping by specific columns
df_out = pd.DataFrame({'Total Compensation' : grouped['Total Compensation'].mean()}).reset_index() # Calculating mean of
df_out = df_out.sort_values(by=['Organization Group','Total Compensation'], ascending=[True,False]) # Sort Ascending on Group but descending on Compensation 
df_out.head()


# In[4]:

# Dump output to a CSV file
if not os.path.exists("Output"):
    os.makedirs("Output")
df_out.to_csv('Output/employee_compensation_Part1.csv',index=False)

