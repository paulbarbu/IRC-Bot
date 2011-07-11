##@file channels.py
#@brief !channels
#@author paullik
#@ingroup moduleFiles

import config

def channels(components): # !channels
    """Returns a string containing the channels the bot is currently connected to
    """

    response = ''

    if components['arguments'] == '!channels':
        #the user sent just the command, no garbage
        if components['sender'] in config.owner:
            #command can be run only by the owner(s)
            response = ', '.join(config.channels)
            response = config.nick + ' is connected to: ' + response
        else:
            response = 'This command can be run only by the owner(s)!'

    return response
