# -*- coding: utf-8 -*-

##@file weather.py
#@brief !weather \<city\> or !weather \<city\>, \<state or country\>
#@author paullik
#@ingroup moduleFiles

from BeautifulSoup import BeautifulStoneSoup
import urllib

def weather(components): # !weather <city> or !weather <city>, <state or country>
    """Returns a string containing the weather conditions from a location"""

    response = ''
    conditions = ''

    try:
        location = components['arguments'].split('!weather ')[1]
    except:
        response = 'Usage: !weather <city>, <state>'
    else:
        location = location.replace(' ', '') # space is removed
        conditions = get_weather(location)
        if type(conditions) == type(str()):
            response = conditions
        else:
            response = conditions['location'] + ' - ' + conditions['temp'] + \
                    ' - ' + conditions['weather'] + ' - Provided by: ' + \
                    'Weather Underground, Inc.'


    return response.encode('utf8')

def get_weather(location):
    """Return a dictionary with the <weather>, <full>, <temperature_string> tags
    from the XML provided by http://api.wunderground.com

    The dictionary 'conditions' will hold 3 values at the end(location, weather,
    temperature)
    Depends on BeautifulStoneSoup
    """

    degree = '°'.decode('utf8')
    conditions = {}
    base_url = 'http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?query='

    try:
        page = urllib.urlopen(base_url + location)
    except:
        return 'Could not open the page!'
    else:
        soup = BeautifulStoneSoup(page)

        conditions['location'] = soup.find('full').contents[0]

        if 2 >= len(conditions['location']):
            return 'Inexistent location: ' + location
        else:
            #weather
            conditions['weather'] = soup.find('weather').contents[0]

            #temperature
            conditions['temp'] = soup.find('temperature_string').contents[0]

            pos = conditions['temp'].find(' ')
            conditions['temp'] = conditions['temp'][:pos] + degree + \
                    conditions['temp'][pos:]

            pos = conditions['temp'].rfind(' ')
            conditions['temp'] = conditions['temp'][:pos] + degree + \
                    conditions['temp'][pos:]
    finally:
        page.close()

    return conditions
