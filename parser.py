# -*- coding: utf-8 -*-
__author__ = 'Alexander Luberg'

import urllib2
import json
from cgi import escape
from BeautifulSoup import BeautifulSoup

REQUIRED = 'Visa required'
NOT_REQUIRED = 'Visa not required'
ON_ARRIVAL = 'Visa on arrival'
ELECTRONIC_VISA = 'Electronic Travel Authorization'

visa_types = [REQUIRED, NOT_REQUIRED, ON_ARRIVAL, ELECTRONIC_VISA]


def normalize(type, types):
    for item in types:
        if item in type:
            return item


def empty(value):
    if value is None:
        return ""
    else:
        return value


req = urllib2.Request(
    "http://en.wikipedia.org/wiki/Visa_requirements_for_United_States_citizens",
    headers={'User-Agent': "Mozilla/5.0"})
#fake agent since wiki returns 403 for default requests
source = urllib2.urlopen(req).read()
lst = []
form = '{"country": "%(country)s", "visa_requirement": "%(visa_requirement)s", "allowed_stay": "%(allowed_stay)s"}'

soup = BeautifulSoup(source)

rows = soup.findAll('table')[0].findAll('tr')
# 0 = Country
# 1 = Visa requirement
# 2 = Allowed stay
# 3 = Notes

for row in rows[1:]:
    items = row.findAll('td')

    try:
        country = items[0].findAll('a')[0].contents[0]
    except IndexError:
        country = ""
    try:
        visa_requirement = items[1].contents[0]
        if "class" in str(visa_requirement):
            visa_requirement = items[1].contents[0].contents[0]
        visa_requirement = normalize(visa_requirement, visa_types)

    except IndexError:
        visa_requirement = ""
    try:
        allowed_stay = items[2].findAll('td')[2].contents[0]
    except IndexError:
        allowed_stay = ""
    try:
        notes = items[3].contents[1]
    except IndexError:
        notes = ""

    json_row = form % {
        "country": escape(str(country), quote=True),
        "visa_requirement": escape(str(visa_requirement), quote=True),
        "allowed_stay": escape(str(allowed_stay), quote=True)
    }
    lst.append(json_row)

string = '[' + ','.join(lst) + ']'
data = json.loads(string)

f = open('usa.json', 'w+')
f.write(json.dumps(data, indent=4))
f.close()


