# from django.test import TestCase

# Create your tests here.

import re
from datetime import datetime

x = "02/02/23"
x = re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1 ', x) 
x = re.sub(r'([a-z])(\d)', r'\1 \2', x)

st = x.split()

if(len(st) == 3):
    temp = st[1]
    temp = temp.upper()
    if(temp.startswith('J')):
        temp = "JANUARY"
    elif(temp.startswith('F')):
        temp = "FEBRUARY"
    elif(temp.startswith('MAR')):
        temp = "MARCH"
    elif(temp.startswith('AP')):
        temp = "APRIL"
    elif(temp.startswith('MAY')):
        temp = "MAY"
    elif(temp.startswith('JUNE')):
        temp = "JUNE"
    elif(temp.startswith('JUL')):
        temp = "JULY"
    elif(temp.startswith('AU')):
        temp = "AUGUST"
    elif(temp.startswith('S')):
        temp = "SEPTEMBER"
    elif(temp.startswith('O')):
        temp = "OCTOBER"
    elif(temp.startswith('N')):
        temp = "NOVEMBER"
    elif(temp.startswith('D')):
        temp = "DECEMBER"
    st[1] = temp

date_obj = " ".join(st)
formats = ["%d %B %Y", "%d %B %y", "%d/%m/%y", "%d-%m-%y", "%d/%m/%Y", "%d-%m-%Y"]

for format in formats:
    try:
        date = datetime.strptime(date_obj, format)
        break
    except ValueError:
        date = "-1"

date_obj = date.date()
date = date.strftime("%d-%m-%Y")
print(date)
