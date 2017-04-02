
# coding: utf-8

# In[1]:

import pandas as pd
import os
df = pd.read_csv("Data/movies_awards.csv")


# In[2]:

df = pd.concat([df['Awards']],axis=1)
df = df.dropna(how='any')


# In[3]:

#Extracting only the numbers in corresponding columns using specific regex
df['Awards_won'] = df['Awards'].str.extract('(\d*) win',expand=False)
df['Awards_nom'] = df['Awards'].str.extract('(\d*) nomination',expand=False)
df['Prime_awards_nom'] = df['Awards'].str.extract('Nominated for (\d*) Primetime Emmy',expand=False)
df['Oscar_awards_nom'] = df['Awards'].str.extract('Nominated for (\d*) Oscar',expand=False)
df['GoldenGlobe_awards_nom'] = df['Awards'].str.extract('Nominated for (\d*) Golden Globe',expand=False)
df['BAFTA_awards_nom'] = df['Awards'].str.extract('Nominated for (\d*) BAFTA Film',expand=False)
df['Prime_awards_won'] = df['Awards'].str.extract('Won (\d*) Primetime Emmy',expand=False)
df['Oscar_awards_won'] = df['Awards'].str.extract('Won (\d*) Oscar',expand=False)
df['GoldenGlobe_awards_won'] = df['Awards'].str.extract('Won (\d*) Golden Globe',expand=False)
df['BAFTA_awards_won'] = df['Awards'].str.extract('Won (\d*) BAFTA Film',expand=False)
df = df.fillna(0)


# In[4]:

# Convert the data types of columns to integer
df[['Awards_won','Awards_nom', 'Prime_awards_nom', 'Oscar_awards_nom', 'GoldenGlobe_awards_nom',
   'BAFTA_awards_nom', 'Prime_awards_won', 'Oscar_awards_won', 'GoldenGlobe_awards_won',
   'BAFTA_awards_won']] = df[['Awards_won','Awards_nom', 'Prime_awards_nom', 'Oscar_awards_nom', 'GoldenGlobe_awards_nom',
   'BAFTA_awards_nom', 'Prime_awards_won', 'Oscar_awards_won', 'GoldenGlobe_awards_won',
   'BAFTA_awards_won']].apply(pd.to_numeric)
#Aggregate awards from all columns and add to the first   
df['Awards_won'] = df['Awards_won'] + df['Prime_awards_won'] + df['Oscar_awards_won'] + df['GoldenGlobe_awards_won'] + df['BAFTA_awards_won']
df['Awards_nom'] = df['Awards_nom'] + df['Prime_awards_nom'] + df['Oscar_awards_nom'] + df['GoldenGlobe_awards_nom'] + df['BAFTA_awards_nom']
df.head()


# In[5]:

# Dump output to a CSV file
if not os.path.exists("Output"):
    os.makedirs("Output")
df.to_csv('Output/Movies_awards_Part1.csv',index=False)

