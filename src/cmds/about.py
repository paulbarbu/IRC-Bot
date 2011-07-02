try:
    import config
    import err
except ImportError:
    sys.exit(err.LOAD_MODULE)

def about(command): # !about
    """Returns a string containing infos about the bot

    """

    response = 'Author: Paullik @ http://github.com/paullik'
    return response
