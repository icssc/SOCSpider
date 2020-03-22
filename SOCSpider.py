'''
Scrapes UCI course enrollment information from WebSOC.

@author: thanasibakis, andrewwself
'''

import bs4 as bs
import urllib.request

BASE_URL = 'https://www.reg.uci.edu/perl/WebSoc?'
TERM = '2020-14'

'''
A class for convenient, named access to course statistics.
'''
class Course:

    '''
    Initializes the Course with a sequence of the cells from the WebSOC
    search results table. Note that these column numbers may change over
    each quarter.
    '''
    def __init__(self, columns):
        self.code   = columns[0]
        self.max    = columns[8]
        self.enr    = columns[9].split(" / ")[-1]
        self.wl     = columns[10]
        self.req    = columns[11]
        self.res    = ' '.join(chunk for chunk in columns[-4].split() if chunk != "and")
        self.units  = columns[3]

'''
Creates a generator over all available Courses on WebSOC
'''
def getAllCourses(includeDiscussions = False) -> [Course]:
    for url in _departmentURLs():
        for course in _departmentCourses(url):
            if(course.units != '0' or includeDiscussions):
                yield course

'''
Given a WebSoc search URL, creates a generator over each Course in the results page
'''
def _departmentCourses(url) -> [Course]:
    
    # Get the page that lists the courses in a table
    with urllib.request.urlopen(url) as sauce:
        soup = bs.BeautifulSoup(sauce, "html.parser")
    
    # Iterate over each course, which is each row in the results
    for row in soup.find_all("tr"):

        # Get the values of each column
        cells = [ td.string for td in row.find_all("td") ]

        # Convert this row to a Course object
        if(len(cells) in {16, 17}):
            yield Course(cells)

'''
Creates a generator over the URLs of each department's WebSOC search results page
'''
def _departmentURLs() -> [str]:

    # Get the page that lists all the departments
    with urllib.request.urlopen(BASE_URL) as sauce:
        soup = bs.BeautifulSoup(sauce, "html.parser")

    # Extract the department codes from the department menu
    for deptOption in soup.find("select", {"name": "Dept"}).find_all("option"):
        urlFields = [ ("YearTerm", TERM), ("ShowFinals", '1'), ("ShowComments", '1'), ("Dept", deptOption.get("value")) ]
        
        # Encode the URL that shows courses in this department
        yield BASE_URL + urllib.parse.urlencode(urlFields)