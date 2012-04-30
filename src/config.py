import os
import os.path
import time

# some commands can be executed only if the user's nick is found in this list
owner = list(set([
    'paullik',
    'foobarfoo',
]))

# server to connect to
server = 'chat.freenode.net'
# server's port
port = 6667

# bot's nicknames
nicks = list(set(['PPyBot']))
# bot's real name
real_name = 'Paul Python Bot'

# channels to join on startup
channels = list(set([
    '#ppybbot',
    '#test-chan',
]))

# commands list
cmds_list = list(set([
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
]))

# users should NOT modify below!
log = os.path.join(os.getcwd(), '..', 'logs', '')
start_time = time.time()
current_nick = ''
