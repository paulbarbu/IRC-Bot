import config

def help(components): # !help
    'Returns a string containing all the available commands'

    response = ''

    if components['arguments'] == '!help':
        # the user sent just the command, no garbage
        response = str(len(config.cmds_list)) + ' available commands: '

        for command in config.cmds_list:
            response = response + command + ' '

    return response
