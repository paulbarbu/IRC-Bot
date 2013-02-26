import config

def help(components): # !help
    '''Returns a string containing all the available commands'''

    response = ''

    if components['arguments'] == '!help':
        # the user sent just the command, no garbage
        response = (str(len(config.cmds['user'] + config.cmds['core'])) +
                    ' available commands: ')

        for command in config.cmds['user'] + config.cmds['core']:
            response = response + command + ' '

    return response
