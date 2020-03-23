'''
Scrapes UCI course enrollment information from WebSOC.

@author: thanasibakis, andrewwself
'''

import bs4 as bs
import urllib.request
from math import floor, sqrt

import warnings

class Course:

	"""
	Initializes the Course with a sequence of the cells from the WebSOC
	search results table. Note that these column numbers may change over
	each quarter.
	"""
	def __init__(self, columns):
		self.code   = columns[0]
		self.max    = columns[8]
		self.enr    = columns[9].split(" / ")[-1]
		self.wl     = columns[10]
		self.req    = columns[11]
		self.res    = ' '.join(chunk for chunk in columns[-4].split() if chunk != "and")
		self.units  = columns[3]

	def __str__(self):
		return f'Course code: {self.code}'

	def __repr__(self):
		return f'Course code: {self.code}'

	def __lt__(self, right):
		return int(self.code) < int(right.code)

class SOCSpider:
	"""
		SOCSpider class is used to crawl all courses on websoc
	"""
	def __init__(self, term: str, optimize: bool=False):
		"""
			Initialize the spider for a specified term
			Term can be found by inspect the following page
			https://www.reg.uci.edu/perl/WebSoc

			Do all functions need to be generators????
		"""
		self.TERM = term
		self.BASE_URL = 'https://www.reg.uci.edu/perl/WebSoc?'
		self._interval = 900
		self._limit = 900
		if optimize:
			self._course_codes = sorted(self.getAllCodes(includeDiscussions=True))
			self.optimizeCodeInterval()
		else:
			warnings.warn('Without optimizing SOCSpider will issue an unoptimal amount of webrequests')

	def _end_interval(self, interval: int, start_idx: int, code: int, codes: list) -> (int, int):
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

	def optimizeCodeInterval(self) -> None:
		"""
			This function takes all codes and finds an interval that keeps the amount of codes on any interval less than the max amount of returned entries on a websoc search

			For any code A_i and code B_i the total amount of codes from A_i to B_i < websoc search max (900)

			Linear function:
			> length(interval[A_i, B_i]) < 900
		"""
		# take the sqrt of the total amount of codes to search at a determined safe but faster rate
		increment = floor( sqrt(len(self._course_codes)) )
		good_interval = True

		# keep checking increments until we have found optimal interval for increments of 1
		while increment > 0:
			while good_interval:
				# Iterate every code
				for idx, code in enumerate(self._course_codes):
					# Grab the end of the interval and test our linear function is true
					end_of_interval = self._end_interval(self._interval, idx, code, self._course_codes)
					if len(self._course_codes[idx:end_of_interval[1]]) >= 900:
						good_interval = False
						break
				# If we found a bad interval we want to roll back to the last good interval
				if good_interval:
					self._interval += increment
				else:
					self._interval -= increment
					break
			# If our current "optimal" interval is less that then limit reset to the limit
			# The limit is the bare minimum optimal interval
			if self._interval < self._limit:
				self._interval = self._limit
			# Round down and subtract 1 for when increment reaches 1
			# sqrt(1) = 1, force below 1 to break loop increment
			increment = floor(sqrt(increment)) - 1
			# reset to good interval and to continue searching
			good_interval = True

	def getInterval(self) -> int:
		"""
			Returns the interval of SOCSpider requests
		"""
		return self._interval

	def _createAllChunks(self) -> [[int]]:
		"""
			Takes all codes and chunks them into lists that fit our interval
		"""
		chunks = []

		start = None
		end = None
		# I don't remember the explanation but it works
		# TODO: refactor and make code readable
		for idx, code in enumerate(self._course_codes):
			code = int(code)

			if start is None:
				end = start = (idx, code)
			elif code - start[1] <= self._interval:
				end = (idx, code)
			else:
				chunks.append(self._course_codes[start[0]:idx])
				start = end = (idx, code)

		# capture final chunk if not caught by for loop
		if end[0] == len(self._course_codes) - 1:
			chunks.append(self._course_codes[start[0]:end[0] + 1])

		return chunks

	def fetchAllChunks(self) -> [Course]:
		"""
			Fetches every course code in chunks to optimize the number of requests made
			Less is better
		"""
		chunks = self._createAllChunks()

		for chunk in chunks:
			urlFields = [
				('YearTerm', self.TERM),
				('ShowFinals', '1'),
				('ShowComments', '1'),
				('CourseCodes', f'{chunk[0]}-{chunk[len(chunk) - 1]}')
			]
			url = self.BASE_URL + urllib.parse.urlencode(urlFields)

			with urllib.request.urlopen(url) as sauce:
				soup = bs.BeautifulSoup(sauce, "html.parser")
			
			# Iterate over each course, which is each row in the results
			for row in soup.find_all("tr"):

				# Get the values of each column
				cells = [ td.string for td in row.find_all("td") ]

				# Convert this row to a Course object
				if(len(cells) in {16, 17}):
					yield Course(cells)

	def getAllCourses(self, includeDiscussions = False) -> [Course]:
		"""
			Generates all of the codes currently on WebSoc
		"""
		for course in self.fetchAllChunks():
			yield course

	def getAllCodes(self, includeDiscussions = False) -> [int]:
		"""
			Generates all of the codes currently on WebSoc
		"""

		codes = []
		department_urls = [item for item in self._departmentURLs()]
		print('Department count:', len(department_urls))
		for url in department_urls:
			department_courses = [item for item in self._departmentCourses(url)]
			for course in department_courses:
				if(course.units != '0' or includeDiscussions):
					codes.append(int(course.code))
		return codes

	def _departmentCourses(self, url) -> [Course]:
		"""
			Given a WebSoc search URL, creates a generator over each Course in the results page
		"""
		
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

	def _departmentURLs(self) -> [str]:
		"""
			Creates a generator over the URLs of each department's WebSOC search results page
		"""

		# Get the page that lists all the departments
		with urllib.request.urlopen(self.BASE_URL) as sauce:
			soup = bs.BeautifulSoup(sauce, "html.parser")

		# Extract the department codes from the department menu
		for deptOption in soup.find("select", {"name": "Dept"}).find_all("option"):
			urlFields = [ ("YearTerm", self.TERM), ("ShowFinals", '1'), ("ShowComments", '1'), ("Dept", deptOption.get("value")) ]
			
			# Encode the URL that shows courses in this department
			yield self.BASE_URL + urllib.parse.urlencode(urlFields)

if __name__ == '__main__':
	spider = SOCSpider('2020-14', optimize=True)

	chunks = spider._createAllChunks()
	courses = [item for item in spider.getAllCourses()]
	print('Chunks:', len(chunks))
	print('Courses:\n', courses)
