try:
    import config
except ImportError:
    sys.exit('Could not load all modules!')

def search(command): # !google <nick>
    nick = command.split()

    if 4 == len(nick) or -1 == str(nick[-2]).find('!search'): #no nick given
        response = config.privmsg + 'Usage: !search <nick>\r\n'
    else:
        response = config.privmsg + str(nick[-1]) + ', please search on: ' + config.search + '\r\n'

    return response

