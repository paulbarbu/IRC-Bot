import config
from functions import *
import err

def join(command): # !join <#channel>+
    """Joins the given channel(s)

    Joins a list of channels, only if the sender is an owner
    """

    response = ''

    pos = command.find('!join ')

    if -1 != pos: #notice the space
        sender = get_sender(command)

        if sender in config.owner: #this command can be run only by the owner(s)
            response = []
            join_chans = []
            response.append('JOIN ')

            arg_channels = command[pos:].split(' ')

            for channel in arg_channels[1:]:
                channel = channel.strip('\r')
                if channel not in config.channels and len(channel) and '#' == channel[0] \
                        and -1 == channel.find(' '): # valid channel name
                    join_chans.append(channel)
                    config.channels.append(channel)

            if len(join_chans):
                response.append(','.join(join_chans))
            else:
                response = 'Invalid channels names, usage: !join <#channel >+'

        else:
            response = 'This command can be run only by the owner(s)!'
    else:
        response = 'Usage: !join <#channel >+'

    return response
