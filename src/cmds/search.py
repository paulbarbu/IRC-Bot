try:
    import config
    import err
except ImportError:
    sys.exit(err.LOAD_MODULE)

def search(command): # !search <nick>
    """Tells <nick> to use a search engine

    Uses config.search to give the user an URL representing the search engine
    """
    nick = command.split()

    if 4 == len(nick) or -1 == str(nick[-2]).find('!search'): #no nick given
        response = 'Usage: !search <nick>'
    else:
        response = str(nick[-1]) + ', please search on: ' + config.search

    return response

