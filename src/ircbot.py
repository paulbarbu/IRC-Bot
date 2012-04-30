#! /usr/bin/env python2.7
import sys
import signal

import config
import parser
import err
from functions import *

#TODO: change is_registered to use the newly created functions (same as run)
#TODO: change is_registered to use the exactly the same socket as the "main" one
#TODO: join and quit can send themselves the commands using the "main" socket
#TODO: if doing the above then a message is possible on the channel

def run(socket, channels, cmds, nick, logfile):
    # buffer for some command received
    buff = ''

    while len(channels):
        receive = socket.recv(4096)
        buff = buff + receive
        response = ''

        if receive:
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

                pos = components['arguments'].find(' ')
                if -1 == pos:
                    pos = len(components['arguments'])

                #get the command issued to the bot without the exclamation mark
                cmd = components['arguments'][1:pos]
                response = run_cmd(cmd, components, cmds)

            elif 'KICK' == components['action'] and \
                nick == components['action_args'][1]:
                    channels.remove(components['action_args'][0])

            elif 'QUIT' == components['action'] and \
                    -1 != components['arguments'].find('Ping timeout: '):
                channels[:] = []

            send_response(response, send_to(command), socket, logfile)

            buff = ''

if __name__ == '__main__':
    valid_cfg = check_cfg(config.owner, config.server, config.nicks,
            config.real_name, config.log, config.cmds_list)

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

        config.current_nick = name_bot(socket, config.real_name, logfile)
        joined = join_channels(config.channels, socket, logfile)

        if joined:
            run(socket, config.channels, config.cmds_list, config.current_nick,
                logfile)

            quit_bot(socket, logfile)
            socket.close()

            content = 'Disconnected from {0}:{1}'.format(
                config.server, config.port)
            log_write(logfile, get_datetime()['time'], ' <> ', content + '\n')
            print content
