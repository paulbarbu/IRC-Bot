#! /usr/bin/env python2.7

#Main file for IRC Bot

import socket
import sys
import re

import config
import parser
from functions import *
import err

#None of these configuration directives can be empty, so they are checked
cfg = check_cfg(config.owner, config.server, config.nick,
        config.realName, config.log, config.cmds_list)

if not cfg: #Some config-directives were empty
    sys.exit(err.INVALID_CFG)

#No duplicates in channels and commands list
config.channels = list(set(config.channels))
config.cmds_list = list(set(config.cmds_list))

#Any valid channel starts with a '#' character and has no spaces
if not check_channel(config.channels):
    sys.exit(err.INVALID_CHANNELS)

#name the log file to write into
dt = get_datetime()
logfile = config.log + dt['date'] + '.log'

content = 'Started on {0}:{1}, with nick: {2}'.format(config.server, config.port,
        config.nick)

try:
    log_write(logfile, dt['time'], ' <> ', content + '\n')
except IOError:
    print err.LOG_FAILURE

#Start connecting
try:
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.socket:
    content = err.NO_SOCKET
    try:
        log_write(logfile, dt['time'], ' <> ', content + '\n')
    except IOError:
        print err.LOG_FAILURE

    print content
else:
    try:
        irc.connect((config.server, config.port))
        receive = irc.recv(4096)
    except IOError:
        content = 'Could not connect to {0}:{1}'.format(config.server, config.port)

        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.LOG_FAILURE

        print content

    else:
        buff = ""

        content = 'Connected to {0}:{1}'.format(config.server, config.port)
        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.LOG_FAILURE

        print content

        #Authenticate
        irc.send('NICK ' + config.nick + '\r\n')
        irc.send('USER ' + config.nick + ' ' + config.nick + ' ' + config.nick + ' :' + \
                config.realName + '\r\n')

        #Join channel(s)
        channel_list = ','.join(config.channels)
        irc.send('JOIN ' + channel_list + '\r\n')
        content = 'Joined: {0}'.format(channel_list)

        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.LOG_FAILURE

        print content

        while len(config.channels):
            receive = irc.recv(4096)
            buff = buff + receive
            response = ''

            if -1 != buff.find('\n'):
                command = buff[0 : buff.find('\n')]
                buff = buff[buff.find('\n')+1 : ]

                components = parser.parse_command(command)

                if 'PING' == components['action']: #PING PONG
                    response = []
                    response.append('PONG')
                    response.append(components['arguments'])

                elif 'PRIVMSG' == components['action'] and \
                        '!' == components['arguments'][0]:
                    #search in commands list only if the message from the user
                    #starts with an exclamation mark

                    for k in config.cmds_list:
                        if 0 == components['arguments'].find('!' + k):
                            #a command is valid only if it's at the beginning of
                            #the message

                            try: #the needed module is imported from 'cmds/'
                                mod = 'cmds.' + k
                                mod = __import__(mod, globals(), locals(), [k])
                            except ImportError: #inexistent module
                                    response = err.C_INEXISTENT.format(k)
                            else:

                                try: #the module is 'executed'
                                    get_response = getattr(mod, k)
                                except AttributeError: #function not defined in module
                                    response = err.C_INVALID.format(k)
                                else:

                                    response = get_response(components)
                                    break

                elif 'KICK' == components['action']: #KICK command issued
                    if config.nick == components['optional_args'][1]:
                        config.channels.remove(components['optional_args'][0])

                elif 'QUIT' == components['action'] and \
                        -1 != components['arguments'].find('Ping timeout: '): #Ping timeout
                    config.channels = []

                if len(response): #send the response and log it
                    if type(response) == type(str()):
                        #the module sent just a string so
                        #I have to compose the command

                        sendto = send_to(command)

                        crlf_pos = response[:-2].find('\r\n')
                        if -1 != crlf_pos: #a multi response command
                            crlf_pos = crlf_pos + 2 #jump over '\r\n'
                            response = response[:crlf_pos] + \
                                    sendto + response[crlf_pos:]

                        response = sendto + response
                    else: #the module send a command itself
                        response = ' '.join(response)

                    response = response + '\r\n'
                    irc.send(response)

                    try:
                        dt = get_datetime()
                        log_write(logfile, dt['time'], ' <> ', response)
                    except IOError:
                        print err.LOG_FAILURE

                try: #log the command
                    dt = get_datetime()
                    log_write(logfile, dt['time'], ' <> ', command + '\n')
                except IOError:
                    print err.LOG_FAILURE


                buff = ""
        #}while len(config.channels)

        #Quit server
        irc.send('QUIT\r\n')
        dt = get_datetime()
        try:
            log_write(logfile, dt['time'], ' <> ', 'QUIT\r\n')
        except IOError:
            print err.LOG_FAILURE

        irc.close()

        content = 'Disconnected from {0}:{1}'.format(config.server, config.port)
        try:
            log_write(logfile, dt['time'], ' <> ', content + '\n')
        except IOError:
            print err.LOG_FAILURE

        print content

