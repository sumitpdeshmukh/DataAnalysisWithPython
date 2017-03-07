
# coding: utf-8

# # Visual Analysis of NYT data
# - Used NYT API to collect NYT data
# - Link to NYT developer docs : [NYT API Documentation](http://developer.nytimes.com/)
# - You need an API key from NYT that is kept as a environment variable before starting this notebook
# - API key is needed only to download the NYT data
# - Analysis is done on downloaded data

# ## 1. Collect the data
# - Downloading the articles published on NYT from 1852 to 2016 

# In[2]:

#Request to get population data for cities based on the city data gathered
import requests
import os
import json
import glob
import sys 
import operator 
from datetime import datetime, timezone
import matplotlib.pyplot as plt

api_key = "api-key=" + os.getenv("nyt_archive_key")
current_dir = os.getcwd() # Gets the current working directory of this file
download_dir = current_dir + "/data/NYT/archive/"


# #### A sample format of NYT article json data

# In[3]:

nytdata = requests.get("https://api.nytimes.com/svc/archive/v1/1852/1.json?" + api_key).json()
print("A random sample of data in json format: ")
print(json.dumps(nytdata["response"]["docs"][1], indent=4, sort_keys=True))


# ## 2. Store data
# - Stored data in `~/year/month/*` format
# - Do not indent and sort the keys to save on disk space and time to write to disk
# - There is a rate limit for downloading the data. On one day you can atmost make 2000 request with one API key.

# In[4]:

def createdir(path): # Function to create directory if it does not exist already
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except OSError as exception:
        return False


# In[5]:

# Pass from and to values or else function will download all data since 1852
def downloadNYTdata(datatype, fromyear=1852, toyear=2016) :
    for year in range(fromyear,toyear + 1):
        for month in range(1,13):
            year = str(year)
            month = str(month)
            resp = requests.get("https://api.nytimes.com/svc/" + datatype + "/v1/" + year + "/" + month + ".json?" + api_key)
            if resp.status_code is 200:
                outputdir = download_dir + year + "/" + month
                createdir(outputdir)
                try:
                    with open(outputdir + "/" + year + "_" + month + ".json", "w") as jsonfile:
                        json.dump(resp.json(), jsonfile)
                except:
                    print("hits: " + str(data_dict["response"]["meta"]["hits"]) + " and x: " + str(x))
            else:
                print("No data for year:" + year + "and Month:" + month)


# - Keep in mind the number of requests you are making
# - Call following function to start dowloading data. 

# In[6]:

# downloadNYTdata(datatype='archive')


# ## 3. Article schema and helper methods

# In[7]:

# For a typical article lets define an article schema
class Article:
    def __init__(self):
        self.headline = ""
        self.author = ""
        self.weburl = ""
        self.sectname = ""
        self.typeofart = ""
        self.pubdate = datetime.today()
        self.keywords = []
    def __repr__(self):
        return repr((self.headline, self.author, self.weburl))


# In[8]:

# Function to create object of Article class form json data     
def getArtObj(json_data):
    article = Article()
           
    article.weburl = json_data["web_url"]
    article.sectname = json_data["section_name"]
    article.typeofart = json_data["type_of_material"]
    article.pubdate = datetime.strptime(json_data["pub_date"][0:19], '%Y-%m-%dT%H:%M:%S')
    article.keywords = [word for word in json_data["keywords"]]
    
    if json_data["headline"] is not None:
        if "main" in json_data["headline"] and json_data["headline"]["main"]:
            article.headline = json_data["headline"]["main"]
        
    if json_data["byline"] is not None:
        if "original" in json_data["byline"] and json_data["byline"]["original"]:
            article.author = json_data["byline"]["original"][3:]
    
    return article

AllArticles = {} # Dictionary to hold all articles objects

# Function to create Data Structure of All articles
def createDS(data_dict):
    for x in range(0, len(data_dict["response"]["docs"])):
        try:
            json_data = data_dict["response"]["docs"][x]
            AllArticles[json_data["_id"]] = getArtObj(json_data)
        except Exception as ex:
            print(ex)

# Function to load Data in memory
def loadArticlesData(fromyear= 1852, toyear = 2017):
    for year in range(fromyear,toyear):
        for month in range(1,13):
            year = str(year)
            month = str(month)
            if os.path.exists(download_dir + year + '/'+ month + '/'):
                json_files = glob.glob(download_dir + year + '/'+ month + '/*.json')
                if json_files is not None:
                    with open(json_files[0]) as datafile:
                        data_dict = json.load(datafile)
                        createDS(data_dict)


# ## 4. Load the data and find answers to some trivial questions
# #### Analysis - 1
# - Total number of articles
# - What are different News Categories?
# - Number of articles NYT publishes per year?
# - Which author published the most articles?

# In[9]:

loadArticlesData(2011, 2017)
print("Total number of articles: ", len(AllArticles))


# In[10]:

author_dict = {} #{'name': {'Num Articles': <num> , 'Publish Date' : ['', '', '']}}
articletypes = {} #{'<type>' : 'count'}
YrArtilces = {}
for key, article in AllArticles.items():
    count = articletypes.get(article.typeofart)
    if count is None:
        articletypes[article.typeofart] = 1
    else:
        articletypes[article.typeofart] = count + 1
    
    count = YrArtilces.get(article.pubdate.year)
    if count is None:
        YrArtilces[article.pubdate.year] = 1
    else:
        YrArtilces[article.pubdate.year] = count + 1

    if article.author:    
        details = author_dict.get(article.author)
        if details is None:
            author_dict[article.author] = {"Num Articles" : 1, "Publish Date" : [article.pubdate]}
        else:
            count = details.get("Num Articles") 
            details["Num Articles"] = count + 1

            publist = details.get("Publish Date")
            publist.append(article.pubdate)
            details["Publish Date"] = publist

            author_dict[article.author] = details


# In[11]:

sorted_tuple = sorted(articletypes.items(), key=operator.itemgetter(1), reverse=True)
print("Top 20 Article Types are")
print(*sorted_tuple[:20], sep="\n")
print("", sep="\n\n")
sorted_tuple = sorted(author_dict.items(), key=lambda x: x[1]["Num Articles"], reverse=True)
print("Top 20 Reporters according to number of published articles")
for t in sorted_tuple[0:20]: print(t[0] + " --- " + str(t[1]["Num Articles"]), sep="\n")


# In[12]:

# Per year number of articles
sorted_tuple = sorted(YrArtilces.items(), key=operator.itemgetter(0))

years = []
numarts = []
for t in sorted_tuple:
    years.append(t[0])
    numarts.append(t[1])

fig, ax = plt.subplots()
width=0.35
def autolabel(rects):
    """Attach a text label above each bar displaying its height"""
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')

ax.set_ylabel('Number of Published Articles')
ax.set_xlabel('Years')
ax.set_title('Years vs Number of Published Articles')
ax.set_xticks(years)
ax.get_xaxis().get_major_formatter().set_useOffset(False)
rects = ax.bar(years, numarts, width)
autolabel(rects)

#plt.show()
#fig.set_size_inches(20, 10.5)
plt.savefig("Q2img/YearsArticlePlot.png")


# ![Articles published per year](Q2img/YearsArticlePlot.png)

# ## 5. Reporters on President Donald Trump
# #### Analysis - 2
# 
# - I am interested in finding reporters reporting on President Donald Trump and store that count
# - Recently President Trump accused New york times reporters on spreading lies about him.
# - I want to know exactly which reporters reported on him the most

# In[13]:


author_dict = {} #{'reporter name': {'weburls' : [list of weburls for these articles], 'reports': count} }
urllist = []
for key, article in AllArticles.items():
    if article.author:
        for data in article.keywords:
            if 'persons' in data['name'] and 'trump' in data['value'].lower():
                details = author_dict.get(article.author) 
                    
                if details is None:
                    author_dict[article.author] = {"reports" : 1, "weburls" : [article.weburl]}
                else:
                    count = details.get("reports") 
                    details["reports"] = count + 1

                    urls = details.get("weburls")
                    urls.append(article.weburl)
                    details["weburls"] = urls

                    author_dict[article.author] = details

sorted_tuple = sorted(author_dict.items(), key=lambda x: x[1]["reports"], reverse=True)
print("Top Reporters reporting on President Donald Trump and his family are")
for t in sorted_tuple[0:20]:
    print(t[0] + " --- " + str(t[1]["reports"]), sep="\n")
    urllist = urllist + t[1]["weburls"]
    
print("The number of urls we are interested in are: ", len(urllist))


# ## 6. Retrieve user comments and find most frequent words
# #### Analysis - 3
# 
# - I am intersted in finding user comments on articles of these reporters
# - The most frequent words that are used by these commenters might give an insight about the general feeling in the population

# In[14]:

# For all articles in urllist we will fetch comments 
# Because we have limit on number of requests I am storing the comments data in data folder.

outputdir = current_dir + "/comments/"
createdir(outputdir)
def fetchCommentsData():
    i = 0
    for url in urllist:
        resp = requests.get("http://api.nytimes.com/svc/community/v3/user-content/url.json?url="+ url + "&" + api_key)
        if resp.status_code is 200:
            comments = resp.json()["results"]["comments"]
            if len(comments) > 0:
                i = i + 1           
                outputpath = outputdir + "UsComments" + str(i) + ".json"
                with open(outputpath, "w") as jf:
                    json.dump(resp.json(), jf)


# In[15]:

# fetchCommentsData() Call this function to get the comments data


# In[16]:

from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS # Better collection than NLTK stopwords
from nltk.tokenize import word_tokenize

txt_comment = ""
json_files = glob.glob(outputdir +'/*.json')
for file in json_files:
    with open(file) as jsonfile:
        json_data = json.load(jsonfile)
        for i in range(0,len(json_data["results"]["comments"])):
            comment = json_data["results"]["comments"][i]
            allwords = word_tokenize(comment["commentBody"])
            sents =  [word.lower() for word in allwords if word.lower() not in ENGLISH_STOP_WORDS and word.isalpha()]
            txt_comment = txt_comment + ' '.join(sents)
            
        


# In[17]:

#Most common words in Email Subjects for These Employees
from nltk.probability import FreqDist
fdist1 = FreqDist(word_tokenize(txt_comment))
print("20 Most common words in comments for these articles")
print(*fdist1.most_common(20), sep="\n")
words = [t[0] for t in fdist1.most_common(50) if t[1] > 300]


# In[18]:

import wordcloud
#WordCloud representation of comment words
fig, ax = plt.subplots(figsize=(16, 12))
wc = wordcloud.WordCloud(width=800, 
                         height=600, 
                         max_words=200,
                         stopwords=ENGLISH_STOP_WORDS).generate(txt_comment)
ax.imshow(wc)
ax.axis("off")
fig.savefig("Q2img/Articlescloud.png")


# ![WordCloud representation of comment words](Q2img/Articlescloud.png)

# In[19]:

# Bigram words to have a sense of what people had said in comments
from nltk import bigrams
bigwords = [bg for bg in set(bigrams(word_tokenize(txt_comment))) if bg[0] in words and bg[1] in words]


# In[20]:

print(*bigwords[0:20], sep="\n")


# #### These words in comments clearly suggest how charged up people were with election.

# In[ ]:



