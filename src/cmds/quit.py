##@file quit.py
#@brief !quit [chan_name]+
#@author paullik
#@ingroup moduleFiles

import config
from functions import *

def quit(components): # !quit [chan_name]+ -> PART #channel
    """Returns a string for quitting the bot from a channel(or more) or from all
    channels if no argument(s) supplied

    If the user is found in the owners list then the bot is closed, otherwise a
    message is sent to the channel
    If an argument is an invalid channel name it is simply ignored
    If there are no more channels active the bot closes
    """
    response = ''
    leave = []

    if components['sender'] in config.owner: #only the owner(s) can run this command
        response = []
        response.append('PART')

        quit_command = components['arguments'].split('!quit ')

        if 2 == len(quit_command): #argument(s) supplied
            arg_channels = quit_command[1].lstrip().split(' ')

            for chan in arg_channels:
                chan = chan.strip('\r')
                if chan in config.channels: #valid channel
                    leave.append(chan)
                    config.channels.remove(chan)

            if len(leave):
                response.append(','.join(leave))
            else:
                response = 'Invalid channel name(s)!'

        else: #no arguments supplied, quitting all channels
            response.append(','.join(config.channels))
            config.channels = []

    else:
        response = 'This command can be run only by the owner(s)!'

    return response
