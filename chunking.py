import bs4 as bs
import urllib.request
from math import floor, sqrt
from course import Course

BASE_URL = 'https://www.reg.uci.edu/perl/WebSoc?'

def average_chunk_size(chunks: list) -> float:
    """
        function to get average chunk size for analysis
    """
    sizes = [len(chunk) for chunk in chunks]
    return sum(sizes) / len(sizes)


def _createAllChunks(_course_codes, _interval) -> [[int]]:
		"""
			Takes all codes and chunks them into lists that fit our interval
		"""
		chunks = []

		start = None
		end = None
		# I don't remember the explanation but it works
		# TODO: refactor and make code readable
		for idx, code in enumerate(_course_codes):
			code = int(code)

			if start is None:
				end = start = (idx, code)
			elif code - start[1] <= _interval:
				end = (idx, code)
			else:
				chunks.append(_course_codes[start[0]:idx])
				start = end = (idx, code)

		# capture final chunk if not caught by for loop
		if end[0] == len(_course_codes) - 1:
			chunks.append(_course_codes[start[0]:end[0] + 1])

		return chunks


def _departmentCourses(url) -> [Course]:
    """
        Given a WebSoc search URL, creates a generator over each Course in the results page
    """
    
    # Get the page that lists the courses in a table
    with urllib.request.urlopen(url) as source:
        soup = bs.BeautifulSoup(source, "html.parser")
    
    # Iterate over each course, which is each row in the results
    for row in soup.find_all("tr"):
        # Get the values of each column
        cells = [ td.string for td in row.find_all("td") ]

        # Convert this row to a Course object
        if(len(cells) in {16, 17}):
            yield Course(cells)


def _departmentURLs(term) -> [str]:
    """
        Creates a generator over the URLs of each department's WebSOC search results page
    """

    # Get the page that lists all the departments
    with urllib.request.urlopen(BASE_URL) as source:
        soup = bs.BeautifulSoup(source, "html.parser")

    # Extract the department codes from the department menu
    for deptOption in soup.find("select", {"name": "Dept"}).find_all("option"):
        urlFields = [ ("YearTerm", term), ("ShowFinals", '1'), ("ShowComments", '1'), ("Dept", deptOption.get("value")) ]
        
        # Encode the URL that shows courses in this department
        yield BASE_URL + urllib.parse.urlencode(urlFields)


def getAllCodes(term, includeDiscussions = False) -> [int]:
		"""
			Generates all of the codes currently on WebSoc
		"""

		codes = []

		for url in _departmentURLs(term):
			for course in _departmentCourses(url):
				if(course.units != '0' or includeDiscussions):
					codes.append(int(course.code))

		return codes


def _end_interval(interval: int, start_idx: int, code: int, codes: [int]) -> (int, int):
    """
        Grabs the end of an interval from a specific starting code

        Args:
            interval: interval we are testing against
            start_idx: start idx of our interval
            code: starting code of our interval
            codes: list of all codes
    """
    # grab the absolutely highest code in the list
    max_idx = len(codes) - 1
    max_code = codes[-1]

    # create potential end code of interval
    end_of_interval = code + interval
    if end_of_interval > max_code:
        return max_code, max_idx 
    else:
        # search for the highest code below the end interval
        for idx, c in enumerate(codes):
            if c >= end_of_interval:
                return codes[idx - 1], idx - 1
    # TODO: Clean up function, return conditional on if's that should always be reached but not edge case tested throughly, potential bugs
    assert False, 'Interval function broke'


def optimizeCodeInterval(_course_codes: [int], _interval: int, _limit: int) -> int:
    """
        This function takes all codes and finds an interval that keeps the amount of codes on any interval less than the max amount of returned entries on a websoc search

        For any code A_i and code B_i the total amount of codes from A_i to B_i < websoc search max (900)

        Linear function:
        > length(interval[A_i, B_i]) < 900
    """
    # take the sqrt of the total amount of codes to search at a determined safe but faster rate
    increment = floor( sqrt(len(_course_codes)) )
    good_interval = True

    # keep checking increments until we have found optimal interval for increments of 1
    while increment > 0:
        while good_interval:
            # Iterate every code
            for idx, code in enumerate(_course_codes):
                # Grab the end of the interval and test our linear function is true
                end_of_interval = _end_interval(_interval, idx, code, _course_codes)
                if len(_course_codes[idx:end_of_interval[1]]) >= 900:
                    good_interval = False
                    break
            # If we found a bad interval we want to roll back to the last good interval
            if good_interval:
                _interval += increment
            else:
                _interval -= increment
                break
        # If our current "optimal" interval is less that then limit reset to the limit
        # The limit is the bare minimum optimal interval
        if _interval < _limit:
            _interval = _limit
        # Round down and subtract 1 for when increment reaches 1
        # sqrt(1) = 1, force below 1 to break loop increment
        increment = floor(sqrt(increment)) - 1
        # reset to good interval and to continue searching
        good_interval = True

    return _interval

def getChunks(term):
    course_codes = sorted(getAllCodes(term))
    interval = optimizeCodeInterval(course_codes, 900, 900)
    return _createAllChunks(course_codes, interval)