import config
from functions import is_registered

def join(socket, components): # !join <#channel>+
    '''Returns a string for joining the given channel(s)

    Joins a list of channels, only if the sender is an owner
    '''
    response = ''

    join_command = components['arguments'].split('!join ') # notice the space

    if 2 == len(join_command):

        if components['sender'] in config.owner and is_registered(socket,
                                                        components['sender']):
            response = []
            join_chans = []
            response.append('JOIN ')

            arg_channels = join_command[1].lstrip().split(' ')

            for channel in arg_channels:
                channel = channel.strip('\r')
                if channel not in config.channels and len(channel) and \
                '#' == channel[0] \
                and -1 == channel.find(' '): # valid channel name
                    join_chans.append(channel)
                    config.channels.append(channel)

            if len(join_chans):
                response.append(','.join(join_chans))
                response.append('\r\nPRIVMSG ' + components['action_args'][0] + \
                    ' :Joined: {0}'.format(', '.join(join_chans)))
            else:
                response = 'Invalid channels names, usage: !join <#channel >+'

        else:
            response = 'This command can be run only by the owners!'
    else:
        response = 'Usage: !join <#channel >+'

    return response
