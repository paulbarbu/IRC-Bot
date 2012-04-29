from functions import *

def parse_command(command):
    '''Returns an IRC command's components

    A dictionary will be filled by the data of the command, the command is as
    follows:
    :sender ACTION action_args :arguments

    sender(string) is the user who sent the command (only the user's nick)

    action(string) can be one of the following: PING, KICK, PRIVMSG, QUIT, etc.
    Check: http://www.irchelp.org/irchelp/rfc/chapter4.html#c4_2

    action_args(list of strings) depends on the ACTION, they are usually the
    channel or the user whom is the command for(see KICK, PRIVMSG, etc.), this
    will be a list and the items in the list will be the words that form the
    actual arguments

    arguments(string) depends on the ACTION

    eg: the command ':foo!foo@domain.tld KICK #chan user :reason' will become:
        sender: 'foo'
        action: 'KICK'
        action_args: ['#chan', 'user']
        arguments: 'reason'
    '''
    components = {
            'sender' : '',
            'action' : '',
            'action_args' : [],
            'arguments' : '',

    }

    if ':' == command[0]: # a user sent a command
        components['sender'] = get_sender(command)

        space_pos = command.find(' ') + 1
        command = command[space_pos:]
        space_pos = command.find(' ')

        components['action'] = command[:space_pos]

        command = command[space_pos + 1:]

        if ':' != command[0]: # action_args are present
            colon_pos = command.find(':')

            if -1 == colon_pos:
                colon_pos = len(command)+1

            components['action_args'] = command[:colon_pos-1].split()
            command = command[colon_pos:]

        if command and ':' == command[0]: # arguments are present
            components['arguments'] = command[1:]

    else: # the server sent a command
        space_pos = command.find(' ')
        components['action'] = command[:space_pos]
        components['arguments'] = command[space_pos+2:]

    components['arguments'] = components['arguments'].rstrip('\r')

    return components
