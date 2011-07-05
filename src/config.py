#Configuration file for IRC Bot
import os
import time

#some commands can be executed only if the user's nick is found in this list
owner = [
        'paullik',
        'foobarfoo',
        ]

#connection and authentication
server = 'chat.freenode.net'
port = 6667

#bot's nickname and real name
nick = 'PPyBot'
realName = 'Paul Python Bot'

channels = [
    '#ppybot',
    '#ppybbot',
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

start_time = time.time()
