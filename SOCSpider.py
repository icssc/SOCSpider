'''
Scrapes UCI course enrollment information from WebSOC.

@author: thanasibakis, andrewwself, Vacneyelk, devsdevsdevs
'''

import bs4 as bs
import urllib.request
from math import floor, sqrt
from course import Course
from constants import _WEBSOC

class SOCSpider:
	"""
		SOCSpider class is used to crawl all courses on websoc
	"""

	def __init__(self, term: str, chunks: [[int]]):
		"""
			Initialize the spider for a specified term
			Term can be found by inspect the following page
			https://www.reg.uci.edu/perl/WebSoc
		"""
		self.term = term
		self.chunks = chunks

	def getAllCourses(self) -> [Course]:
		"""
			Fetches every course code in chunks to optimize the number of requests made.
			Getting less chunks is better/faster.
		"""
		for chunk in self.chunks:
			urlFields = [
				('YearTerm', self.term),
				('ShowFinals', '1'),
				('ShowComments', '1'),
				('CourseCodes', f'{chunk[0]}-{chunk[-1]}'),
				("CancelledCourses", 'Include')
			]
			url = f'{_WEBSOC}?{urllib.parse.urlencode(urlFields)}'

			with urllib.request.urlopen(url) as sauce:
				soup = bs.BeautifulSoup(sauce, "html.parser")
			
			# Iterate over each course, which is each row in the results
			for row in soup.find_all("tr"):

				# Get the values of each column
				cells = [ td.string for td in row.find_all("td") ]

				# Convert this row to a Course object
				if(len(cells) in {15, 16, 17}):
					yield Course(cells)
