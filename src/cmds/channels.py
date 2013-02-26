import config
from functions import is_registered

def channels(socket, components): # !channels
    '''Returns a string containing the channels the bot is connected to'''
    response = ''

    if components['arguments'] == '!channels':
        # the user sent just the command, no garbage
        if components['sender'] in config.owner and \
                is_registered(socket, components['sender']):
            # this command can be run only by the owners
            response = ', '.join(config.channels)
            response = config.current_nick + ' is connected to: ' + response
        else:
            response = 'This command can be run only by the owners!'

    return response
