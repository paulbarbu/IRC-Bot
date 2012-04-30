#! /usr/bin/env python2.7
import sys
import signal

import config
import parser
import err
from functions import *

#TODO: change is_registered to use the exactly the same socket as the "main" one
#TODO: join and quit can send themselves the commands using the "main" socket
#TODO: if doing the above then a message is possible on the channel

def run(socket, channels, logfile):
    # buffer for some command received
    buff = ''

    while len(channels):
        receive = socket.recv(4096)
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
                response.append(':' + components['arguments'])

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
                if config.current_nick == components['action_args'][1]:
                    channels.remove(components['action_args'][0])

            elif 'QUIT' == components['action'] and \
                    -1 != components['arguments'].find('Ping timeout: '):
                channels[:] = []

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
                socket.send(response)

                log_write(logfile, get_datetime()['time'], ' <> ', response)

            buff = ''

if __name__ == '__main__':
    valid_cfg = check_cfg(config.owner, config.server, config.nicks,
            config.realName, config.log, config.cmds_list)

    if not valid_cfg:
        sys.exit(err.INVALID_CFG)

    if not check_channel(config.channels):
        sys.exit(err.INVALID_CHANNELS)

    signal.signal(signal.SIGINT, sigint_handler)

    logfile = config.log + get_datetime()['date'] + '.log'

    socket = create_socket(logfile)

    if socket and connect_to((config.server, config.port), socket, logfile):
        content = 'Connected to {0}:{1}'.format(config.server, config.port)
        log_write(logfile, get_datetime()['time'], ' <> ', content + '\n')
        print content

        name_bot(socket, logfile)
        joined = join_channels(config.channels, socket, logfile)

        if joined:
            run(socket, config.channels, logfile)

            # quit the server
            socket.send('QUIT\r\n')
            log_write(logfile, get_datetime()['time'], ' <> ', 'QUIT\r\n')

            socket.close()

            content = 'Disconnected from {0}:{1}'.format(config.server, config.port)
            log_write(logfile, get_datetime()['time'], ' <> ', content + '\n')
            print content
