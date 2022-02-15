import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer

bowList = []

def main():
    with urllib.request.urlopen('https://www.indeed.com/jobs?q=data%20analyst&l&vjk=42384986658311ac') as f:
        source = f.read()

    # decode source and get links
    source = source.decode('utf-8')
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    links = webpage_regex.findall(source)

    # get link to next page
    nextPage = [k for k in links if re.search('[\/](jobs\?q=data\+analyst&start=)', k)]

    nextPages = []
    nextPages.append(nextPage[-1])

    #get links to first i pages
    for i in range(0):
        with urllib.request.urlopen(f'https://www.indeed.com{nextPage[-1]}') as f:
            source = f.read()

            # decode source and get links
            source = source.decode('utf-8')
            webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
            links = webpage_regex.findall(source)

            # get link to next page
            nextPage = [k for k in links if re.search('[\/](jobs\?q=data\+analyst&start=)', k)]

            # appends last index of list to another list (right most button => next page button)
            nextPages.append(nextPage[-1])

    # calls the get job links method to get each page link
    theLinks = []

    # gets each job link from each page of job links
    for j in range(len(nextPages)):
        theLinks = theLinks + getJobLinks(nextPages[j])


    counter = [0,0,0,0,0,0] # initializes counter variable
    # loops k times for k links and sums number of times target word was found in each link
    for k in range(len(theLinks)):
        # adds index of the array to its corresponding index: [1, 2, 3] + [1, 1, 1] = [2, 3, 4]
        for index, integer in enumerate(readLinks(theLinks[k])):
            counter[index] += integer

    numLinks = len(theLinks)

    print(counter)
    print(numLinks)

    bow(bowList)


    # plots the data to a bar graph
    df = pd.DataFrame({'Qualification': ['SQL', 'AWS', 'Tableau', 'Python', 'Excel'], '%OfDataAnalystJobs': [(counter[0]/numLinks)*100,
                                                                                                              (counter[1]/numLinks) * 100,
                                                                                                              (counter[2]/numLinks) * 100,
                                                                                                              (counter[3]/numLinks) * 100,
                                                                                                              (counter[4]/numLinks) * 100]})
    ax = df.plot.bar(x='Qualification', y='%OfDataAnalystJobs', rot=0, )
    plt.show()




# scrapes individual job links from each page and returns them
def getJobLinks(url):
    url = 'https://www.indeed.com' + url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = soup.find_all('a', re.compile('(job_)(.*)')) # get jobs using regex

    theJobs=[]
    for k in range(len(jobs)):
        theJobs.append('https://www.indeed.com' + jobs[k].get('href'))

    return theJobs


# reads the links and counts how many times SQL is said in each one
def readLinks(jobURL):
    #print(jobURL)

    counter=[]

    # split and clean
    list = requests.get(jobURL).text

    bowList.append(list)

    list = list.split()


    # counts each skill from the job description
    sqlList = [w for w in list if re.findall('(.*)([Ss][Qq][Ll])(.*)', w)]
    awsList = [w for w in list if re.findall('^([Aa][Ww][Ss])$', w)]
    tbluList = [w for w in list if re.findall('(.*)([tT]ableau)(.*)', w)]
    pthnList = [w for w in list if re.findall('(.*)([Pp]ython,)(.*)', w)]
    xlList = [w for w in list if re.findall('(.*)(Excel)(.*)', w)]
    #pbiList = [w for w in list if re.findall('^([Pp]ower[Bb][Ii])$', w)]


    # if skill shows up increment corresponding array index by 1
    if sqlList:
        counter.append(1)
    else:
        counter.append(0)

    if awsList:
        counter.append(1)
    else:
        counter.append(0)

    if tbluList:
        counter.append(1)
    else:
        counter.append(0)

    if pthnList:
        counter.append(1)
        if len(pthnList)>1:
            print(pthnList)
            print(jobURL)
    else:
        counter.append(0)

    if xlList:
        counter.append(1)
    else:
        counter.append(0)

    # if pbiList:
    #     counter.append(1)
    # else:
    #     counter.append(0)

    #print(counter)
    return counter

def bow(bowList):
    text_data = np.array(bowList)

    count = CountVectorizer()
    bag_of_words = count.fit_transform(text_data)

    feature_names = count.get_feature_names_out()

    # pd.set_option("display.max_rows", 202, "display.max_columns", None)
    df = pd.DataFrame(bag_of_words.toarray(), columns=feature_names)


    print(df.loc[:, ['python', 'sql', 'tableau', 'excel']])



if __name__ == '__main__':
    main()


