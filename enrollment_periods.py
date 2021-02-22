import datetime
import pytz

def localized_datetime_object(date_str: str) -> datetime.datetime:
    date_time_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return pytz.timezone('America/Los_Angeles').localize(date_time_obj)

DATES_TO_RUN = {'2021 spring': {'start': localized_datetime_object('2021-02-22'), 'end': localized_datetime_object('2021-04-09')}}

def should_run(term: str) -> bool:
    now = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
    return now >= DATES_TO_RUN[term]['start'] and now <= DATES_TO_RUN[term]['end']