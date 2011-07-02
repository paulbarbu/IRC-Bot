try:
    import config
    from functions import *
    import err
except ImportError:
    sys.exit(err.LOAD_MODULE)

def join(command): # !join <#channel>+
    """Joins the given channel(s)

    Joins a list of channels, only if the sender is an owner
    """

    response = ''

    pos = command.find('!join ')

    if -1 != pos: #notice the space
        sender = get_sender(command)

        if sender in config.owner:
            response = []
            join_chans = []
            response.append(config.channel_join)

            arg_channels = command[pos:].split(' ')

            for channel in arg_channels[1:]:
                channel = channel.strip('\r')
                if len(channel) and '#' == channel[0] and -1 == channel.find(' '):
                    join_chans.append(channel)
                    config.channels.append(channel)

            if len(join_chans):
                response.append(','.join(join_chans))
                config.channels_left = config.channels_left + len(join_chans)
            else:
                response = 'Usage: !join <#channel>+'

        else:
            response = 'This command can be run only by the owner(s)!'
    else:
        response = 'Usage: !join <#channel>+'

    return response
