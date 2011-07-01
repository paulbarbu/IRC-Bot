#! /usr/bin/env python2.7
#Main file for IRC Bot

import socket
import sys
import re

#these modules must exist in cwd
try:
    import config
    from functions import *
    import err
except ImportError:
    sys.exit(err.load_module)


cfg = check_cfg(config.owner, config.search, config.server, config.nick,
        config.realName, config.channel, config.log, config.cmds_list, config.quit)

if not cfg:
    sys.exit('Config error!')

if not check_channel(config.channel):
    sys.exit('Invalid channel!')

#name the log file to write into
dt = get_datetime()
logfile = config.log + dt['date'] + '.log'

content = 'Started on {0}:{1}, channel: {2}, with nick: {3}'.format(config.server,
        config.port, config.channel, config.nick)

try:
    log_write(logfile, dt['time'], ' <> ', content + '\n')
except IOError:
    print err.log_failure

#Start connecting
try:
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.socket:
    content = 'Could not create a socket!'
    try:
        log_write(logfile, dt['time'], ' <> ', content + '\n')
    except IOError:
        print err.log_failure

    print content
else:
    try:
        irc.connect((config.server, config.port))
        receive = irc.recv(4096) #TODO debug with this line commented and remove buff = ""
    except IOError:
        content = 'Could not connect to {0}:{1}'.format(config.server, config.port)

        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.log_failure

        print content

    else:
        buff = ""

        content = 'Connected to {0}:{1}'.format(config.server, config.port)
        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.log_failure

        print content

        #Join server & authenticate
        irc.send(config.nick_auth)
        irc.send(config.user_auth)

        #Join channel
        irc.send(config.channel_join)
        content = 'Joined: {0}'.format(config.channel)

        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.log_failure

        print content

        while config.alive:
            receive = irc.recv(4096)
            buff = buff + receive
            response = ''

            if -1 != buff.find('\n'):
                command = buff[0 : buff.find('\n')]
                buff = buff[buff.find('\n')+1 : ]

                if -1 != command.find('PING'): #PING PONG
                    response = []
                    response.append('PONG')
                    response.append(command.split()[1])

                elif 1 < len(re.findall('!', command)) and \
                    ':' == command[command.rfind('!') - 1] and \
                    ' ' == command[command.rfind('!') - 2]:
                    #search in commands list only if the message from server
                    #contains two '!'(exclamation marks) in it
                    #one from command, the other from the user's nick
                    for k in config.cmds_list:
                        if -1 != command.find('!' + k) and \
                            (' ' == command[command.rfind('!' + k) + len(k) + 1] \
                            or '\r' == command[command.rfind('!' + k) + len(k) +1]):
                            try:
                                mod = 'cmds.' + k
                                mod = __import__(mod, globals(), locals(), [k])
                            except ImportError: #inexistent module
                                    response = err.c_inexistent.format(k)
                            else:

                                try:
                                    get_response = getattr(mod, k)
                                except AttributeError: #function not defined in module
                                    response = err.c_invalid.format(k)
                                else:

                                    response = get_response(command)
                                    break

                #send the response and log it
                if len(response):
                    if type(response) == type(str()):
                        response = config.privmsg + response
                    else:
                        response = ' '.join(response)

                    response = response + '\r\n'
                    irc.send(response)

                    try:
                        dt = get_datetime()
                        log_write(logfile, dt['time'], ' <> ', command + '\n')
                        log_write(logfile, dt['time'], ' <> ', response)
                    except IOError:
                        print err.log_failure

                buff = ""
        #}while config.alive

        #Quit server
        irc.send(config.quit)
        dt = get_datetime()
        try:
            log_write(logfile, dt['time'], ' <> ', config.quit)
        except IOError:
            print err.log_failure

        irc.close()

        content = 'Disconnected from {0}:{1}'.format(config.server, config.port)
        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.log_failure

        print content

