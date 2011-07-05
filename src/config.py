#Configuration file for IRC Bot
import os
import time

#some commands can be executed only if the user's nick is found in this list
owner = [
        'paullik',
        'foobarfoo',
        ]

#the link provided on !search
search = "http://google.ro"

#connection and authentication
server = 'chat.freenode.net'
port = 6667

#bot's nickname and real name
nick = 'PPyBot'
realName = 'Paul Python Bot'

channels = [
    '#ppybot',
    '#pppybot',
    '#pybbot',
    ]

#commands list
cmds_list = [
        'wiki',
        'quit',
        'answer',
        'about',
        'help',
        'weather',
        'join',
        'channels',
        'google',
        'mball',
        'uptime',
        'so',
        ]

#### Users should NOT modify below!
#log directory, logs will be stored at this location
log = os.getcwd() + os.sep + '..' + os.sep + 'logs' + os.sep

#protocol-required messages/signals
nick_auth = 'NICK ' + nick + '\r\n'
user_auth = 'USER ' + nick + ' ' + nick + ' ' + nick + ' :' + realName + '\r\n'

channel_join = 'JOIN ' #notice the space
channel_part = 'PART'

privmsg = 'PRIVMSG ' #notice the space

quit = 'QUIT\r\n'

close_link = 'ERROR :Closing Link: ' #notice the space

kick = ' KICK ' #notice the spaces

start_time = time.time()
