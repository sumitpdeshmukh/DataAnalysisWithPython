
# coding: utf-8

# In[1]:

import pandas as pd
import os
df = pd.read_csv("Data/employee_compensation.csv")


# In[2]:

# Filtering records containing Calendar only 
df = df[df['Year Type'] == 'Calendar']


# In[3]:

# Keeping only required columns in this part
df = pd.concat([df['Job Family'], df['Employee Identifier'], df['Salaries'], 
                df['Overtime'], df['Total Benefits'], df['Total Compensation']], axis=1)


# In[4]:

#Grouping records and calculating avereage 
grouped = df.groupby(['Employee Identifier'])
df_out = pd.DataFrame({'Avg_Salaries' : grouped['Salaries'].mean(),
                      'Avg_Overtime':grouped['Overtime'].mean(),}).reset_index()
df_out = df_out[df_out['Avg_Overtime'] >= (df_out['Avg_Salaries'] * 0.05)]


# In[5]:

df_out.head()


# In[6]:

df = pd.merge(df,df_out, how='inner', on='Employee Identifier')
grouped = df.groupby(['Job Family'])
df_out = pd.DataFrame({'Avg_Total_Benefits' : grouped['Total Benefits'].mean(),
                      'Avg_Total_Compensation':grouped['Total Compensation'].mean()}).reset_index()
df_out['Percent_Total_Benefit'] = (df_out['Avg_Total_Benefits'] * 100) / df_out['Avg_Total_Compensation']
df_out = df_out.sort_values(by=['Percent_Total_Benefit'], ascending=False)
df_out.head(5)


# In[7]:

# Dump output to a CSV file
if not os.path.exists("Output"):
    os.makedirs("Output")
df_out.to_csv('Output/employee_compensation_Part2.csv',index=False)

