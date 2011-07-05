import err
import config
from functions import *

def parse_command(command):
    """Returns an IRC command's components

    A dictionary will be filled by the data of the command
    :sender ACTION [optional_args] :args

    sender is the user who sent the command

    ACTION can be one of the following: PING, KICK, PRIVMSG, QUIT, JOIN, etc.

    optional_args depends on the ACTION, they are usually the channel or the
    user whom is the command for(see KICK or PRIVMSG), this will be a list

    arguments again depends on the ACTION(for PRIVMSG here will be stored the
    message sent by sender)
    """

    components = {
            'sender' : '',
            'action' : '',
            'optional_args' : [],
            'arguments' : '',

    }

    if ':' == command[0]: #a user sent a command
        components['sender'] = get_sender(command)

        space_pos = command.find(' ') + 1
        command = command[space_pos:]
        space_pos = command.find(' ')

        components['action'] = command[:space_pos]

        command = command[space_pos + 1:]

        if ':' != command[0]: #optional_args are present
            colon_pos = command.find(':')
            components['optional_args'] = command[:colon_pos-1].split()
            command = command[colon_pos + 1:]

        if ':' == command[0]: #no optional_args
            components['arguments'] = command[1:]
        else: #optional_args were present
            components['arguments'] = command

    else: #the server sent a command
        space_pos = command.find(' ')
        components['action'] = command[:space_pos]
        components['arguments'] = command[space_pos+1:]

    print components #TODO remove
    return components

#TODO remove
#parse_command(':Shumi!~chatzilla@93.122.243.190 JOIN :#yet-another-project')
#parse_command(':Stevethepirate!~LOLCATS@clam.leg.uct.ac.za PRIVMSG #archlinux :Which is like 350 euro')
#parse_command(':paullik!~paullik@unaffiliated/paullik KICK #ppybot foopaul :foopaul')
#parse_command('ERROR :Closing Link: 188.24.237.32 (Ping timeout: 240 seconds)')
