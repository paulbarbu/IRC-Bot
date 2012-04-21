import os
import time

# Some commands can be executed only if the user's nick is found in this list
owner = [
    'paullik',
    'foobarfoo',
    ]

# server to connect to
server = 'chat.freenode.net'
# server's port
port = 6667

# bot's nicknames
nicks = ['PPyBot']
# bot's real name
realName = 'Paul Python Bot'

# channels to join on startup
channels = [
    '#ppybbot',
    '#test-chan',
    ]

# commands list
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
log = os.getcwd() + os.sep + '..' + os.sep + 'logs' + os.sep
start_time = time.time()
