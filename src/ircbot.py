#! /usr/bin/env python2.7
import socket
import sys
import string
import random
import signal

import config
import parser
import err
from functions import *

signal.signal(signal.SIGINT, sigint_handler)

# none of these configuration directives can be empty, so they are checked
valid_cfg = check_cfg(config.owner, config.server, config.nicks,
        config.realName, config.log, config.cmds_list)

if not valid_cfg:
    sys.exit(err.INVALID_CFG)

# no duplicates in channels and commands list
config.channels = list(set(config.channels))
config.cmds_list = list(set(config.cmds_list))

# any valid channel starts with a '#' character and has no spaces
if not check_channel(config.channels):
    sys.exit(err.INVALID_CHANNELS)

dt = get_datetime()
logfile = config.log + dt['date'] + '.log'

nick_generator = get_nick()
config.current_nick = nick_generator.next()

content = 'Started on {0}:{1}, with nick: {2}'.format(config.server,
        config.port, config.current_nick)

log_write(logfile, dt['time'], ' <> ', content + '\n')

# start connecting
try:
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.socket:
    log_write(logfile, dt['time'], ' <> ', err.NO_SOCKET + '\n')
    print content
else:
    try:
        irc.connect((config.server, config.port))
    except IOError:
        content = 'Could not connect to {0}:{1}'.format(config.server,
                config.port)

        log_write(logfile, dt['time'], ' <> ', content + '\n')
        print content

    else:
        content = 'Connected to {0}:{1}'.format(config.server, config.port)
        log_write(logfile, dt['time'], ' <> ', content + '\n')
        print content

        # try to authenticate
        irc.send('NICK ' + config.current_nick + '\r\n')
        irc.send('USER ' + config.current_nick + ' ' + config.current_nick + \
                ' ' + config.current_nick + ' :' + config.realName + '\r\n')

        while True:
            receive = irc.recv(4096)

            if 'Nickname is already in use' in receive: # try another nickname
                try:
                    config.current_nick = nick_generator.next()
                except StopIteration: # if no nick is available just make one up
                    config.current_nick = get_nick().next() + \
                            ''.join(random.sample(string.ascii_lowercase, 5))

                irc.send('NICK ' + config.current_nick + '\r\n')

                content = 'Changing nick to: ' + config.current_nick
                log_write(logfile, dt['time'], ' <> ', content + '\n')
            elif config.current_nick in receive or 'motd' in receive.lower():
                # successfully connected
                break

        # join the configured channels
        channel_list = ','.join(config.channels)
        irc.send('JOIN ' + channel_list + '\r\n')

        content = 'Joined: {0}'.format(channel_list)
        log_write(logfile, dt['time'], ' <> ', content + '\n')
        print content

        # buffer for some command received
        buff = ''

        while len(config.channels):
            receive = irc.recv(4096)
            buff = buff + receive
            response = ''

            log_write(logfile, get_datetime()['time'], ' <> ', receive + \
                    ('' if '\n' == receive[len(receive)-1] else '\n'))

            if -1 != buff.find('\n'):
                # get a full command from the buffer
                command = buff[0 : buff.find('\n')]
                buff = buff[buff.find('\n')+1 : ]

                # command's components after parsing
                components = parser.parse_command(command)

                if 'PING' == components['action']:
                    response = []
                    response.append('PONG')
                    response.append(components['arguments'])

                elif 'PRIVMSG' == components['action'] and \
                        '!' == components['arguments'][0]:
                    # search in commands list only if the message from the user
                    # starts with an exclamation mark

                    for k in config.cmds_list:
                        if 0 == components['arguments'].find('!' + k):
                            # commands are valid if they are the beginning of
                            # the message

                            try: # the needed module is imported from 'cmds/'

                                # module that needs to be loaded after finding a
                                # valid user command
                                mod = 'cmds.' + k
                                mod = __import__(mod, globals(), locals(), [k])
                            except ImportError: # inexistent module
                                    response = err.C_INEXISTENT.format(k)
                            else:

                                try: # the module is 'executed'

                                    # the name of the command is translated into
                                    # a function's name, then called
                                    get_response = getattr(mod, k)
                                except AttributeError:
                                    # function not defined in module
                                    response = err.C_INVALID.format(k)
                                else:

                                    response = get_response(components)
                                    break

                elif 'KICK' == components['action']:
                    if config.current_nick == components['optional_args'][1]:
                        config.channels.remove(components['optional_args'][0])

                elif 'QUIT' == components['action'] and \
                        -1 != components['arguments'].find('Ping timeout: '):
                    config.channels = []

                if len(response): # send the response and log it
                    if type(response) == type(str()):
                        # the module sent just a string so
                        # I have to compose the command

                        # get the sender
                        sendto = send_to(command)

                        # a multi-line command must be split
                        crlf_pos = response[:-2].find('\r\n')
                        if -1 != crlf_pos:
                            crlf_pos = crlf_pos + 2 # jump over '\r\n'
                            response = response[:crlf_pos] + \
                                    sendto + response[crlf_pos:]

                        response = sendto + response
                    else: # the module sent a command like WHOIS or KICK
                        response = ' '.join(response)

                    response = response + '\r\n'
                    irc.send(response)

                    log_write(logfile, get_datetime()['time'], ' <> ', response)

                buff = ''

        # quit the server
        irc.send('QUIT\r\n')
        log_write(logfile, get_datetime()['time'], ' <> ', 'QUIT\r\n')

        irc.close()

        content = 'Disconnected from {0}:{1}'.format(config.server, config.port)
        log_write(logfile, get_datetime()['time'], ' <> ', content + '\n')
        print content
