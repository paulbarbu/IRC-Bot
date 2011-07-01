try:
    import config
    import err
    from functions import *
except ImportError:
    sys.exit(err.load_module)

def quit(command): # !quit -> PART #channel
    """Quits the bot

    If the user is found in the owners list then the bot is closed, otherwise a
    message is sent to the channel
    """
    response = ''
    sender = get_sender(command)
    if sender in config.owner:
        response = []
        response.append(config.channel_part)
        response.append(config.quit_msg)
        config.alive = False
    else:
        response = 'This command can be run only by the owner(s)!'

    return response
