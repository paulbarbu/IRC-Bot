##@file twitter.py
#@brief !twitter [username]
#@author paullik
#@ingroup moduleFiles

from BeautifulSoup import BeautifulStoneSoup
import urllib

#TODO: get description, name, screenName, location, etc

def twitter(components):
    """Gets latest tweet from a specified user(via his nickname)

    """
    apiURL = 'http://api.twitter.com/1/users/show.xml?screen_name='
    response = ''

    screenName = components['arguments'].split('!twitter ')

    if 1 == len(screenName):
        #no screen name specified, getting last tweet for the sender
        apiURL = apiURL + components['sender']
        screenName = components['sender']

    elif 2 == len(screenName):
        apiURL = apiURL + screenName[1]
        screenName = screenName[1]

    status = getStatus(apiURL)

    if type(status) == type(str()):
        response = status
    else:
        response = '{0}\'s latest tweet was made on: {1}\r\n{2}'\
                .format(screenName, status['date'], status['text'])

    return response

def getStatus(apiURL):
    """Gets a user's status(latest tweet) using the XML provided by the API

    status will be a dictionary containing the date and the text of the user's
    status
    """
    status = ''

    try:
        xml = urllib.urlopen(apiURL)
    except:
        return 'Error getting the status!'
    else:
        status = {'date': '',
                  'text': '',
                }
        soup = BeautifulStoneSoup(xml)

        xmlStatus = soup.find('user').find('status')
        status['date'] = xmlStatus.find('created_at').contents[0]
        status['text'] = xmlStatus.find('text').contents[0]

    return status
