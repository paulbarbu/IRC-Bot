# coding: latin-1

from BeautifulSoup import BeautifulStoneSoup
import urllib
import config
import err

def weather(command): # !weather <city> or !weather <city>, <state or country>
    """Returns a message containing the weather conditions from a location

    """
    response = ''
    conditions = ''
    try:
        location = command.split('!weather ')[1]
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


    return str(response)

def get_weather(location):
    """Return a dictionary with the <weather>, <full>, <temperature_string> tags
    from the XML provided by http://api.wunderground.com

    The dictionary 'conditions' will hold 3 values at the end(location, weather,
    temperature)
    """
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
            return 'Inexistent location!'
        else:
            #weather
            conditions['weather'] = soup.find('weather').contents[0]

            #temperature
            conditions['temp'] = soup.find('temperature_string').contents[0]
            conditions['temp'] = conditions['temp'].encode("latin-1")

            #pos = conditions['temp'].find(' ')
            #conditions['temp'] = conditions['temp'][:pos] + '°' + \
                    #conditions['temp'][pos:]

            #pos = conditions['temp'].rfind(' ')
            #conditions['temp'] = conditions['temp'][:pos] + '°' + \
                    #conditions['temp'][pos:]

        page.close()

    return conditions
