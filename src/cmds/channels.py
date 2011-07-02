try:
    import config
    from functions import *
    import err
except ImportError:
    sys.exit(err.LOAD_MODULE)

def channels(command): # !channels
    """Returns a string containing the channels the bot is currently connected to

    """

    response = ''
    sender = get_sender(command)

    if sender in config.owner: #command can be run only by the owner(s)
        response = ', '.join(config.channels)
        response = config.nick + ' is connected to: ' + response
    else:
        response = 'This command can be run only by the owner(s)!'

    return response
