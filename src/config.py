##@file config.py
#@brief Configuration file
#@author paullik
#@ingroup kernelFiles

import os
import time

##Some commands can be executed only if the user's nick is found in this list
owner = [
        'paullik',
        'foobarfoo',
        ]

##Server to connect to
server = 'chat.freenode.net'
##Server's port
port = 6667

##Bot's nickname
nick = 'PPyBot'
##Bot's real name
realName = 'Paul Python Bot'

##Channels to join on startup
channels = [
    '#ppybot',
    '#ppybbot',
    ]

##Commands list
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
        'twitter',
        ]

#### Users should NOT modify below!
##log directory, logs will be stored in this location
log = os.getcwd() + os.sep + '..' + os.sep + 'logs' + os.sep

##Time the bot was started
start_time = time.time()
