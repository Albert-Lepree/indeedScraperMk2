import csv
import requests
from bs4 import BeautifulSoup
import re
import urllib.request


def main():
    # getJobLinks('https://www.indeed.com/jobs?q=data%20analyst&l&vjk=42384986658311ac')

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
    for i in range(5):
        with urllib.request.urlopen(f'https://www.indeed.com{nextPage[-1]}') as f:
            source = f.read()

            # decode source and get links
            source = source.decode('utf-8')
            webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
            links = webpage_regex.findall(source)

            # get link to next page
            nextPage = [k for k in links if re.search('[\/](jobs\?q=data\+analyst&start=)', k)]

            nextPages.append(nextPage[-1])

    # calls the get job links method to get each page link
    theLinks = []

    for j in range(len(nextPages)):
        theLinks = theLinks + getJobLinks(nextPages[j])

    countSQL = 0 # initializes counter variable
    # loops k times for k links and sums number of times target word was found in each link
    for k in range(len(theLinks)):
       countSQL+= readLinks(theLinks[k])

    print(f'SQL is required in {countSQL} of the jobs out of {len(theLinks)} ')


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
    list = requests.get(jobURL).text.split()
    newList = [w for w in list if re.findall('(.*)(SQL)(.*)', w)]

    if newList:
        return 1

    return 0


if __name__ == '__main__':
    main()


