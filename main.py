import pymongo
import os
import chunking
import pytz
import enrollment_periods
from datetime import datetime

from course import Course


def get_pst_date():
    date = datetime.now(pytz.timezone('America/Los_Angeles'))
    return date.strftime("%Y-%m-%d")


def term_to_readable(term: str) -> (str, str):
    year_code = term[-2:]

    year = term[0:4]
    quarter = None

    if year_code == '92':
        quarter = 'fall'
    elif year_code == '03':
        quarter = 'winter'
    elif year_code == '14':
        quarter = 'spring'

    return (year, quarter)


def get_update_object(course: Course, term: str) -> pymongo.UpdateOne:
    year, quarter = term_to_readable(term)

    doc = {'quarter': quarter, 'year': year, 'sectionCode': course.code}

    data = {'date': get_pst_date(),
            'maxCapacity': course.max,
            'numCurrentlyEnrolled': course.enr,
            'numOnWaitlist': course.wl,
            'numRequested': course.req,
            'restrictions': course.res}

    return pymongo.UpdateOne(doc, {'$push': {'data': data}}, upsert=True)


def main(event, context):
    TERM = os.environ.get('SOCSPIDER_TERM')
    MONGODB_URI = os.environ.get('SOCSPIDER_MONGODB_URI')
    MONGODB_USERNAME = os.environ.get('SOCSPIDER_MONGODB_USERNAME')
    MONGODB_PASSWORD = os.environ.get('SOCSPIDER_MONGODB_PASSWORD')
    DB_NAME = os.environ.get('SOCSPIDER_DB_NAME')
    ENROLLMENT_COLLECTION_NAME = os.environ.get('SOCSPIDER_ENROLLMENT_COLLECTION_NAME')

    # Do not run if the day is not within the current enrollment period
    current_term = ' '.join(term_to_readable(TERM))
    if not enrollment_periods.should_run(current_term):
        return

    connection_uri = MONGODB_URI.format(MONGODB_USERNAME, MONGODB_PASSWORD, sep='\r\n')

    db = pymongo.MongoClient(connection_uri)[DB_NAME]

    print('Retrieving course data')

    updates = [get_update_object(course, TERM) for course in chunking.yield_all_courses(TERM)]

    print('Updating data')
    print(f'Data added for {len(updates)} courses')
    db[ENROLLMENT_COLLECTION_NAME].bulk_write(updates)
    print('Data update complete')


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv(verbose=True)
    main(None, None)
