import config

def help(components): # !help
    """Returns a string containing all the available commands

    """

    response = ''

    if components['arguments'] == '!help':
        #the user sent just the command, no garbage
        response = str(len(config.cmds_list)) + ' available commands: '

        for i in config.cmds_list:
            response = response + '!' + i + ' '

    return response
