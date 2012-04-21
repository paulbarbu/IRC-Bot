from functions import *

def parse_command(command):
    '''Returns an IRC command's components

    A dictionary will be filled by the data of the command, the command is as
    follows:
    :sender ACTION [optional_args] :arguments

    sender(string) is the user who sent the command

    ACTION(string) can be one of the following: PING, KICK, PRIVMSG, QUIT, JOIN, etc.
    For more info on this check: http://www.irchelp.org/irchelp/rfc/chapter4.html#c4_2

    optional_args(list of strings) depends on the ACTION, they are usually the
    channel or the user whom is the command for(see KICK, PRIVMSG, etc.), this
    will be a list and the items in the list will be the words that form the
    optional arguments

    arguments(string) depends on the ACTION

    eg: ':foo KICK #chan user :reason'
        sender: ':foo'
        ACTION: 'KICK'
        optional_args: ['#chan', 'user']
        arguments: 'reason'
    '''
    components = {
            'sender' : '',
            'action' : '',
            'optional_args' : [],
            'arguments' : '',

    }

    if ':' == command[0]: # a user sent a command
        components['sender'] = get_sender(command)

        space_pos = command.find(' ') + 1
        command = command[space_pos:]
        space_pos = command.find(' ')

        components['action'] = command[:space_pos]

        command = command[space_pos + 1:]

        if ':' != command[0]: # optional_args are present
            colon_pos = command.find(':')
            components['optional_args'] = command[:colon_pos-1].split()
            command = command[colon_pos + 1:]

        if ':' == command[0]: # no optional_args
            components['arguments'] = command[1:]
        else: # optional_args were present
            components['arguments'] = command

    else: # the server sent a command
        space_pos = command.find(' ')
        components['action'] = command[:space_pos]
        components['arguments'] = command[space_pos+1:]

    components['arguments'] = components['arguments'].rstrip('\r')

    return components
