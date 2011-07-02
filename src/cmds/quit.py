try:
    import config
    import err
    from functions import *
except ImportError:
    sys.exit(err.LOAD_MODULE)

def quit(command): # !quit [chan_name]+ -> PART #channel
    """Quits the bot from a channel(or more) or from all channels if no
    argument(s) supplied

    If the user is found in the owners list then the bot is closed, otherwise a
    message is sent to the channel
    If an argument is an invalid channel name it is simply ignored
    If there are no more channels active the bot closes
    """
    response = ''
    leave = []

    sender = get_sender(command)

    if sender in config.owner: #only the owner(s) can run this command
        response = []
        response.append(config.channel_part)

        pos = command.find('!quit ')

        if -1 != pos: #argument(s) supplied
            arg_channels = command[pos:].split(' ')

            for chan in arg_channels[1:]:
                chan = chan.strip('\r')
                if chan in config.channels: #valid channel
                    leave.append(chan)
                    config.channels_left = config.channels_left - 1

            if len(leave):
                response.append(','.join(leave))
            else:
                response = 'Invalid channel name(s)!'

        else: #no arguments supplied, quitting all channels
            response.append(','.join(config.channels))
            config.channels_left = 0

    else:
        response = 'This command can be run only by the owner(s)!'

    return response
