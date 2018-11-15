#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import time

# Directivas de formato: https://docs.python.org/3/library/datetime.html?highlight=datetime#strftime-strptime-behavior

'''
import datetime, time
dt = datetime.datetime.fromtimestamp(time.time())
dt.date()
datetime.date(2018, 11, 15)
dt.time()
datetime.time(18, 53, 40, 16392)
'''

def get_datetime_now():
    return datetime.datetime.fromtimestamp(time.time())

def get_date(_datetime):
    return _datetime.date()

def get_time(_datetime):
    return _datetime.time()

def get_date_as_string(_datetime, format='%y-%m-%d'):
    return _datetime.strftime(format)

def get_time_as_string(_datetime, format='%H-%M'):
    return _datetime.strftime(format)
