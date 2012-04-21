##@file channels.py
#@brief !channels
#@author paullik
#@ingroup moduleFiles

import config
from functions import is_registered
import ircbot

def channels(components): # !channels
    """Returns a string containing the channels the bot is currently connected to
    """

    response = ''

    if components['arguments'] == '!channels':
        #the user sent just the command, no garbage
        if components['sender'] in config.owner and is_registered(components['sender']):
            #command can be run only by the owner(s)
            response = ', '.join(config.channels)
            response = config.nick + ' is connected to: ' + response
        else:
            response = 'This command can be run only by the owner(s)!'

    return response
