#Configuration file for IRC Bot
import os

#internals
owner = [
        'paullik',
        'foobarfoo',
        ]
search = "http://google.ro"

#connection and authentication
server = 'chat.freenode.net'
port = 6667

nick = 'PPyBot'
realName = 'Paul Python Bot'

channels = [
    '#ppybot',
    '#pppybot',
    '#pybot',
    ]

#commands list
cmds_list = [
        'search',
        'wiki',
        'quit',
        'answer',
        'about',
        'help',
        'weather',
        ]

#### Users should NOT modify below!
#log directory
log = os.getcwd() + os.sep + '..' + os.sep + 'logs' + os.sep

#standard messages
nick_auth = 'NICK ' + nick + '\r\n'
user_auth = 'USER ' + nick + ' ' + nick + ' ' + nick + ' :' + realName + '\r\n'

channel_join = 'JOIN '#notice the space
channel_part = 'PART'

privmsg = 'PRIVMSG '

quit = 'QUIT\r\n'

#connection should stay alive
alive = True

#needed by !quit module
channels_left = len(channels)
