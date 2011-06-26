try:
    import config
    import err
    from functions import *
except ImportError:
    sys.exit(err.load_module)

def quit(command):# !quit -> PART #channel
    sender = get_sender(command)
    if sender in config.owner:
        response = config.channel_part
        config.alive = False
    else:
        response = config.privmsg + 'This command can be run only by the owner(s)!\r\n'

    return response
