import logging
from celery import schedules
import holidays
from datetime import datetime, time, timedelta

logger = logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the current year
current_year = datetime.now().year

# Generate the list of US holidays for the current year and the next year
us_holidays = holidays.US(years=[current_year, current_year + 1])

class Schedules:
    @staticmethod
    def now():
        return datetime.now()
    
    @staticmethod
    def is_holiday():
        return Schedules.now().date() in us_holidays

    @staticmethod
    def is_weekend():
        return Schedules.now().weekday() >= 5 