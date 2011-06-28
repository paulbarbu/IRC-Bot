try:
    from BeautifulSoup import BeautifulStoneSoup
    import urllib
    import config
    import err
except ImportError:
    sys.exit(err.load_module)

def weather(command):
    """Returns a message containing the weather conditions from a location

    A message ready to be sent on IRC containing weather informations
    """
    response = ""
    conditions = {}

    try:
        location = command.split('!weather ')[1]
    except:
        response = 'Usage: !weather <city>, <state>'
    else:
        location = location.replace(' ', '') # space is removed
        conditions = get_weather(location)
        #TODO check conditions type to see if there was an error or it contains
        #temperature and so on


    return config.privmsg + response

def get_weather(location):
    conditions = {}
    base_url = 'http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?query='

    try:
        page = urllib.urlopen(base_url + location)
    except:
        return 'Could not open the page!'
    else:
        soup = BeautifulStoneSoup(page)
        # TODO city exists?
        conditions['location'] = soup.find('full').contents[0]

        if 2 >= len(conditions['location']):
            return 'Inexistent location!'
        else:
            pass #TODO check the others

        page.close()

    return conditions
