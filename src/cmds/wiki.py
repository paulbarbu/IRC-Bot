try:
    import config
    import err
except ImportError:
    sys.exit(err.load_module)

def wiki(command):
    """Replies a wiki link with the searched term

    Tries to return a link to the wiki page for the <search term>
    """
    wlink = command.split('!wiki ') #notice the trailing space
    if 1 == len(wlink): #no search term given
        response = config.privmsg + 'Usage: !wiki <search term>\r\n'
    else:
        response = config.privmsg + 'http://en.wikipedia.org/wiki/' + wlink[1].lstrip().replace(' ', '_') + '\r\n'

    return response
