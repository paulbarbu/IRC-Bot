from BeautifulSoup import BeautifulStoneSoup
import urllib
from datetime import datetime

def twitter(components):
    '''Gets latest tweet from a specified user (via his nickname)'''

    apiURL = 'http://api.twitter.com/1/users/show.xml?screen_name='
    response = ''

    screenName = components['arguments'].split('!twitter ') # notice the space

    if 1 == len(screenName):
        # no screen name specified, getting last tweet for the sender
        apiURL = apiURL + components['sender']
        screenName = components['sender']

    elif 2 == len(screenName):
        apiURL = apiURL + screenName[1]
        screenName = screenName[1]
    else:
        return 'Usage: !twitter <screen name>'

    status = getStatus(apiURL)

    if type(status) == type(str()):
        response = status
    else:
        response = '{0}\'s latest tweet was made on: {1}\r\n{2}'\
                .format(screenName, status['date'], status['text'])

    return response

def getStatus(apiURL):
    '''Gets a user's status (latest tweet) using the XML provided by the API

    Status will be a dictionary containing the date and the text of the user's
    status

    The date will have the following format: DD/MM/YYYY HH:MM
    '''
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

        user = soup.find('user')

        if user is None:
            status = "This user doesn't exist!"
        else:
            xmlStatus = user.find('status')

            if xmlStatus is None:
                status = 'This user has no tweets!'
            else:
                date = xmlStatus.find('created_at').contents[0]

                # strip the timezone offset
                minus = date.find('-')
                plus = date.find('+')
                if -1 != minus:
                    date = date[:minus] + date[minus+6:]
                else:
                    date = date[:plus] + date[plus+6:]

                date = datetime.strptime(date, '%a %b %d %H:%M:%S %Y')

                status['date'] = date.strftime('%d/%m/%Y %H:%S')
                status['text'] = xmlStatus.find('text').contents[0]

        xml.close()

    return status
