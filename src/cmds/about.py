try:
    import config
    import err
except ImportError:
    sys.exit(err.load_module)

def about(command):
    response = config.privmsg + 'Simple IRC Bot\r\n' + \
    config.privmsg + 'Written in: Python\r\n' + \
    config.privmsg + 'Author: Paullik @ http://github.com/paullik\r\n'
    return response
