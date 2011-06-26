try:
    import config
    import err
except ImportError:
    sys.exit(err.load_module)

def search(command): # !google <nick>
    """Tells <nick> to use a search engine

    Uses config.search to give the user an URL representing the search engine
    """
    nick = command.split()

    if 4 == len(nick) or -1 == str(nick[-2]).find('!search'): #no nick given
        response = config.privmsg + 'Usage: !search <nick>\r\n'
    else:
        response = config.privmsg + str(nick[-1]) + ', please search on: ' + config.search + '\r\n'

    return response

