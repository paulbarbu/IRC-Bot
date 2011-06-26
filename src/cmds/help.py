try:
    import config
    import err
except ImportError:
    sys.exit(err.load_module)

def help(command):
    response = 'Available commands: '
    for i in config.cmds_list:
        response = response + '!' + i + ' '
    return config.privmsg + response + '\r\n'
