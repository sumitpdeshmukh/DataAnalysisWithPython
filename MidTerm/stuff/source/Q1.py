
# coding: utf-8

# In[ ]:

---
# Visual Analysis of Enron Dataset

#### Abstract :
- [Enron Scandal Summary](http://www.investopedia.com/updates/enron-scandal-summary/) - Link to Investopedia article to get a brief summary about what the scandal was.
- The enron data-set is available at [CMU Enron data 1.82 GB tgz file](https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tgz) .
---


# In[1]:

import os
from email.parser import Parser
import matplotlib.pyplot as plt
import operator
import wordcloud
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS # Better collection than NLTK stopwords
from datetime import datetime
import codecs
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist


# ## 1. Check random email file

# In[2]:

current_dir = os.getcwd() # Gets the current directory of this file
download_dir = current_dir + "/data/enron/maildir/"
with open(download_dir + "allen-p/_sent_mail/1.", 'r') as file:
    maildata = Parser().parse(file)
    # A sample email looks like
    print(maildata) 


# ## 2. Email schema and some helper methods

# In[3]:

# For a typical email file lets define an email schema

class EmailFrame:
    def __init__(self, efrom):
        self.efrom = efrom
        self.subject = ""
        self.content = ""
        self.date = datetime.today()
        self.eto = []
    def __repr__(self):
        return repr((self.efrom, self.subject, self.date))


# In[4]:

# All emails for a specific id
def get_emails(emailid):
    emails = set()
    for key, amail in AllEmails.items():
        if amail.efrom == emailid:
            emails.add(key)
    
    return list(emails)

# To get the content from email objects
def get_content(msg):
    parts = []
    for part in msg.walk(): # to walk on all parts of MIME message and grab content if its an Email Chain
        if part.get_content_type() == 'text/plain':
            parts.append( part.get_payload() )
    return ''.join(parts)

# To separate multiple email addresses
def get_email_ids(line):
    if line:
        addrs = line.split(',')
        addrs = set(map(lambda x: x.strip(), addrs))
        return list(addrs)
    else:
        return None


# ## 3. Load email files and parse them 

# In[5]:

AllEmails = {} # A dictionary to Hold all EmailFrame objects

for dirname, dirnames, filenames in os.walk(download_dir):
    for filename in filenames:
        if '.DS_Store' in filename: # to skip traversing OS specific folders
            continue
        emfile = os.path.join(dirname, filename)
        with codecs.open(emfile, 'r', encoding='utf-8', errors='ignore') as file: # Ignoring non unicode encoding files
            try:
                maildata = Parser().parse(file)
                obj = EmailFrame(maildata["From"])
                obj.subject = maildata["Subject"]
                obj.content = get_content(maildata)
                obj.date = datetime.strptime(maildata["Date"][0:-6], '%a, %d %b %Y %H:%M:%S %z')
                obj.eto = get_email_ids(maildata["To"])
                AllEmails[maildata["Message-ID"]] = obj
            except Exception as ex:
                print(ex +" in reading "+ emfile)
# This block takes a while to generate AllEmails data structure 


# ## 4. Distribution of Emails according to year, day and hour
# #### Analysis - 1

# In[6]:

NYearEmails = {} # Key -> Year and value  -> Number of emails
NHourEmails = {} # Key -> Hour and value  -> Number of emails
NDayEmails = {}  # Key -> Day and value  -> Number of emails

for key, amail in AllEmails.items():
    count = NYearEmails.get(amail.date.year)
    if count is None:
        NYearEmails[amail.date.year] = 1
    else:
        NYearEmails[amail.date.year] = count + 1
    
    count = NHourEmails.get(amail.date.hour)
    if count is None:
        NHourEmails[amail.date.hour] = 1
    else:
        NHourEmails[amail.date.hour] = count + 1
        
    count = NDayEmails.get(amail.date.weekday())
    if count is None:
        NDayEmails[amail.date.weekday()] = 1
    else:
        NDayEmails[amail.date.weekday()] = count + 1

sorted_tuple = sorted(NYearEmails.items(), key=operator.itemgetter(0))
years = []
mailyrs = []
for t in sorted_tuple:
    years.append(t[0])
    mailyrs.append(t[1])

sorted_tuple = sorted(NHourEmails.items(), key=operator.itemgetter(0))
hours = []
mailhrs = []
for t in sorted_tuple:
    hours.append(t[0])
    mailhrs.append(t[1])

sorted_tuple = sorted(NDayEmails.items(), key=operator.itemgetter(0))
days = []
maildays = []
for t in sorted_tuple:
    days.append(t[0])
    maildays.append(t[1])


# In[7]:

#Plot 1
plt.subplot(1, 3, 1)
plt.plot(years, mailyrs,color='b')
plt.axis([1995, 2005, 0, 400000])
plt.xlabel('Years', fontsize=18)
plt.ylabel('N emails', fontsize=18)
plt.title('Years vs Number of Emails', fontsize=18)
plt.grid(True)

#Plot 2
plt.subplot(1, 3, 2)
plt.plot(hours, mailhrs, color='g')
plt.xlabel('Hours', fontsize=18)
plt.title('Hours vs Number of Emails', fontsize=18)
plt.grid(True)

#Plot 3
plt.subplot(1, 3, 3)
plt.plot(days, maildays, color='r')
plt.xlabel('Days', fontsize=18)
plt.title('Days vs Number of Emails', fontsize=18)
plt.grid(True)

fig = plt.gcf()
fig.set_size_inches(20, 10.5)
#plt.show()
plt.savefig("Q1img/CountNemails.png")


# ![Number of Emails vs DateTime Parameters](Q1img/CountNemails.png)

# ## 5. Answer some questions like
# #### Analysis - 2
# - How many emails in Total?
# - Who sends most Emails?
# - Who sends most personal emails? (One to One)

# In[8]:

print("Total number of Emails in Enron Database: ", len(AllEmails))


# In[9]:

MostEmails = {}
PersEmails = {}
SuspEmails = {} # _ids of emails that are personal
for key, amail in AllEmails.items():
    count = MostEmails.get(amail.efrom)
    if count is None:
        MostEmails[amail.efrom] = 1
    else:
        MostEmails[amail.efrom] = count + 1
    
    if amail.eto and len(amail.eto) is 1 and not amail.efrom in amail.eto[0] and not "announcements" in amail.efrom:
        #Removing self emails and announcement emails and keeping only personal emails
        count = PersEmails.get(amail.efrom + " --> " + amail.eto[0])
        if count is None:
            PersEmails[amail.efrom + " --> " + amail.eto[0]] = 1
        else:
            PersEmails[amail.efrom + " --> " + amail.eto[0]] = count + 1

sorted_tuple = sorted(MostEmails.items(), key=operator.itemgetter(1), reverse=True)

print("Top 10 employees who sent most emails")
print(*sorted_tuple[:10], sep="\n") # Unpacking top 10 tuples and printing with the seperator


# In[10]:


sorted_tuple = sorted(PersEmails.items(), key=operator.itemgetter(1), reverse=True)

print("Top 10 employees who sent most personal (One --> One) emails")
print(*sorted_tuple[:10], sep="\n") # Unpacking top 10 tuples and printing with the seperator

employeelist = [emp[0] for emp in sorted_tuple if emp[1] >= 738]
alist = [i.split(" --> ")[0] for i in employeelist]

suspemp = set(alist) # Evaluate these employee emails manually to find any suspcious topic discussion


# ## 6. What do they write in top personal Emails? 
# #### Analysis - 3
# - Frequently used words in these personal emails
# - The wordcloud representation of frequently used words

# In[11]:

subjects = ""
contents = ""
# Get all subject and email content data of these employees under radar
for eid in suspemp:
    persemails = get_emails(eid)

    for mailid in persemails:
        mails = AllEmails.get(mailid)
        allwords = word_tokenize(mails.subject)
        sents =  [word.lower() for word in allwords if word.lower() not in ENGLISH_STOP_WORDS and word.isalpha()]
        subjects = subjects + ' '.join(sents)
        
        allwords = word_tokenize(mails.content)
        sents =  [word.lower() for word in allwords if word.lower() not in ENGLISH_STOP_WORDS and word.isalpha()]
        contents = contents + ' '.join(sents)

# This block takes a while to execute, can be optimized with some different strategy


# In[12]:

#Most common words in Email Subjects for These Employees
fdist1 = FreqDist(word_tokenize(subjects))
print("10 Most common words in Email Subjects for These Employees")
print(*fdist1.most_common(10), sep="\n")

print("", sep="\n\n")
#Most common words in Email Contents for These Employees
fdist1 = FreqDist(word_tokenize(contents))
print("10 Most common words in Email Contents for These Employees")
print(*fdist1.most_common(10), sep="\n")


# In[13]:

#WordCloud representation of subject words
fig, ax = plt.subplots(figsize=(16, 12))
wc = wordcloud.WordCloud(width=800, 
                         height=600, 
                         max_words=200,
                         stopwords=ENGLISH_STOP_WORDS).generate(subjects)
ax.imshow(wc)
ax.axis("off")
fig.savefig("Q1img/subjectcloud.png")


# ![WordCloud representation of subject words](Q1img/subjectcloud.png)
# 

# In[ ]:

#WordCloud representation of content words
fig, ax = plt.subplots(figsize=(16, 12))
wc = wordcloud.WordCloud(width=800, 
                         height=600, 
                         max_words=200,
                         stopwords=ENGLISH_STOP_WORDS).generate(contents)
ax.imshow(wc)
ax.axis("off")
fig.savefig("Q1img/contentcloud.png")


# ![WordCloud representation of subject words](Q1img/contentcloud.png)

# In[ ]:



