#! /usr/bin/env python2.7
import sys
import signal
import futures

import config
import parser
import err
from functions import *

def run(socket, channels, cmds, nick, logfile):
    # buffer for some command received
    buff = ''
    num_workers = sum(len(v) for k, v in cmds.iteritems())

    #TODO: what happens if I use all the workers?

    #TODO: don't let commands to run for more than one minute

    with futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
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
                to = send_to(command)

                if 'PING' == components['action']:
                    response = []
                    response.append('PONG')
                    response.append(':' + components['arguments'])

                elif 'PRIVMSG' == components['action']:
                    if '!' == components['arguments'][0]:
                        # a command from a user only makes sense if it starts
                        # with an exclamation mark

                        pos = components['arguments'].find(' ')
                        if -1 == pos:
                            pos = len(components['arguments'])

                        # get the command issued to the bot without the "!"
                        cmd = components['arguments'][1:pos]

                        callable_cmd = get_cmd(cmd, cmds['user'], logfile)
                        if callable_cmd:
                            run_cmd(socket, executor, to, callable_cmd,
                                    components, logfile)
                        else:
                            callable_cmd = get_cmd(cmd, cmds['core'], logfile)

                            if callable_cmd:
                                try:
                                    response = callable_cmd(socket, components)
                                except Exception as e:
                                    response = err.C_EXCEPTION.format(
                                    callable_cmd.__name__)

                                    log_write(logfile, response, ' <> ',
                                            str(e) + '\n')

                    # run auto commands
                    for cmd in config.cmds['auto']:
                        callable_cmd = get_cmd(cmd, cmds['auto'], logfile)
                        if callable_cmd:
                            run_cmd(socket, executor, to, callable_cmd,
                                    components, logfile)

                elif 'KICK' == components['action'] and \
                    nick == components['action_args'][1]:
                        channels.remove(components['action_args'][0])

                elif 'QUIT' == components['action'] and \
                        -1 != components['arguments'].find('Ping timeout: '):
                    channels[:] = []

                # this call is still necessary in case that a PONG response or a
                # core command response should be sent, every other response is
                # sent when the futures finish working from their respective
                # thread
                send_response(response, to, socket, logfile)

                buff = ''


def main():
    valid_cfg = check_cfg(config.owner, config.server, config.nicks,
            config.real_name, config.log, config.cmds)

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

        config.current_nick = name_bot(socket, config.nicks, config.real_name,
            logfile)
        joined = join_channels(config.channels, socket, logfile)

        if joined:
            run(socket, config.channels, config.cmds, config.current_nick, logfile)

        quit_bot(socket, logfile)
        socket.close()

        content = 'Disconnected from {0}:{1}'.format(config.server, config.port)
        log_write(logfile, get_datetime()['time'], ' <> ', content + '\n')
        print content

if __name__ == '__main__': #pragma: no cover
    main()
