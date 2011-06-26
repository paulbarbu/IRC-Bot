#Main file for IRC Bot

from config import *
from functions import *
import err
import socket
import sys

cfg = check_cfg(owner, search, server, nick, realName, channel,
        log, c_lst, quit)

if not cfg:
    sys.exit('Config error!')

if not check_channel(channel):
    sys.exit('Invalid channel!')

#name the log file to write into
dt = get_datetime()
logfile = log + dt['date'] + '.log'

content = 'Started on {0}:{1}, channel: {2}, with nick: {3}'.format(server,
        port, channel, nick)

log_write(logfile, dt['time'], ' <> ', content + '\n')

#Start connecting
try:
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.socket:
    content = 'Could not create a socket!'
    log_write(logfile, dt['time'], ' <> ', content + '\n')
    print content
else:
    try:
        irc.connect((server, port))
        receive = irc.recv(4096) #TODO debug with this line commented and remove buff = ""
    except IOError:
        content = 'Could not connect to {0}:{1}'.format(server, port)

        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.log_failure

        print content

    else:
        buff = ""

        content = 'Connected to {0}:{1}'.format(server, port)
        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.log_failure

        print content

        #Join server & authenticate
        irc.send(nick_auth)
        irc.send(user_auth)

        #Join channel
        irc.send(channel_join)
        content = 'Joined: {0}'.format(channel)

        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.log_failure

        print content

        while alive:
            receive = irc.recv(4096)
            buff = buff + receive
            response = ""

            if -1 != buff.find('\n'):
                command = buff[0 : buff.find('\n')]
                buff = buff[buff.find('\n')+1 : ]

                if -1 != command.find('PING'): #PING PONG between server and client
                    response = 'PONG ' + command.split()[1] + '\r\n'

                elif -1 != command.find('!search'): # !google <nick>
                    nick = command.split()

                    if 4 == len(nick): #no nick given
                        response = privmsg + 'Usage: !search <nick>\r\n'
                    else:
                        response = privmsg + str(nick[-1]) + ', please search on: ' + search + '\r\n'

                elif -1 != command.find('!wiki'): # !wiki <search term>
                    wlink = command.split('!wiki ') #notice the trailing space
                    if 1 == len(wlink): #no search term given
                        response = privmsg + 'Usage: !wiki <search term>\r\n'
                    else:
                        response = privmsg + 'http://en.wikipedia.org/wiki/' + wlink[1].lstrip().replace(' ', '_') + '\r\n'

                elif -1 != command.find('!quit'): # !quit -> PART #channel
                    sender = get_sender(command)
                    if sender in owner:
                        response = channel_part
                        alive = False
                    else:
                        response = privmsg + 'This command can be run only by the' + ' owner(s)!\r\n'

                elif -1 != command.find('!answer') or -1 != command.find('!42'): # !answer
                    response = privmsg + 'The Answer to the Ultimate Question of Life, the Universe, and Everything is 42!\r\n'

                else:
                    buff = ""

                if len(response):
                    irc.send(response)

                    try:
                        dt = get_datetime()
                        log_write(logfile, dt['time'], ' <> ', command + '\n')
                        log_write(logfile, dt['time'], ' <> ', response)
                    except IOError:
                        print err.log_failure

        #Quit server
        irc.send(quit)
        dt = get_datetime()
        try:
            log_write(logfile, dt['time'], ' <> ', quit)
        except IOError:
            print err.log_failure

        irc.close()

        content = 'Exited with message: {0}'.format(quit_msg)
        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.log_failure

        print content

