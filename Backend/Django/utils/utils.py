from datetime import datetime

def today_date():
    return datetime.today().date().strftime('%Y-%m-%d')
