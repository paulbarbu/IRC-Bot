import os
import os.path
import time

# some commands can be executed only if the user's nick is found in this list
owner = list(set([
    'paullik',
    'foobarfoo',
    'paullik-test',
]))

owner_email = {
    'foobarfoo': 'foobar@gmail.com',
}

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
    'task',
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

# commands list that the bot will execute even if a human didn't request an
# action
auto_cmds_list = list(set([
    'email_alert',
]))

# smtp server for email_alert
smtp_server = 'smtp.gmail.com'
smtp_port = 25
from_email_address = 'changeme@gmail.com'
from_email_password = 'p@s$w0rd'

# users should NOT modify below!
log = os.path.join(os.getcwd(), '..', 'logs', '')
start_time = time.time()
current_nick = ''
