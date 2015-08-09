#! /usr/bin/env python2.7
import sys
import signal
import concurrent.futures
import logging
import os

import config
import parser
import err
from functions import *

def run(socket, channels, cmds, nick):
    # buffer for some command received
    buff = ''
    num_workers = sum(len(v) for k, v in cmds.iteritems())

    # TODO: what happens if I use all the workers?

    # TODO: don't let commands to run for more than one minute

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        while len(channels):
            receive = socket.recv(4096)
            buff = buff + receive
            response = ''

            if receive:
                logging.debug(receive + \
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

                        callable_cmd = get_cmd(cmd, cmds['user'])
                        if callable_cmd:
                            run_cmd(socket, executor, to, callable_cmd,
                                    components)
                        else:
                            callable_cmd = get_cmd(cmd, cmds['core'])

                            if callable_cmd:
                                try:
                                    response = callable_cmd(socket, components)
                                except Exception as e:
                                    response = err.C_EXCEPTION.format(
                                    callable_cmd.__name__)

                                    logging.error(str(e))

                    # run auto commands
                    for cmd in config.cmds['auto']:
                        callable_cmd = get_cmd(cmd, cmds['auto'])
                        if callable_cmd:
                            run_cmd(socket, executor, to, callable_cmd,
                                    components)

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
                send_response(response, to, socket)

                buff = ''


def main():
    valid_cfg = check_cfg(config.owner, config.server, config.nicks,
            config.real_name, config.log, config.cmds)

    if not valid_cfg:
        sys.exit(err.INVALID_CFG)

    if not os.path.isdir(config.log):
        try:
            os.makedirs(config.log)
        except os.error as e:
            print "Log directory creation failed: " + str(e)
            sys.exit(1)
        else:
            print "Log directory created"

    logfile = get_datetime()['date'] + '.log'

    try:
        logging.basicConfig(filename=os.path.join(config.log, logfile),
            level=config.logging_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
    except IOError as e:
        print "Couldn't set up logging: " + str(e)
        sys.exit(1)

    if not check_channel(config.channels):
        sys.exit(err.INVALID_CHANNELS)

    signal.signal(signal.SIGINT, sigint_handler)

    socket = create_socket()

    if socket and connect_to((config.server, config.port), socket):
        content = 'Connected to {0}:{1}'.format(config.server, config.port)
        logging.info(content)
        print content

        config.current_nick = name_bot(socket, config.nicks, config.real_name)
        joined = join_channels(config.channels, socket)

        if joined:
            run(socket, config.channels, config.cmds, config.current_nick)

        quit_bot(socket)
        socket.close()

        content = 'Disconnected from {0}:{1}'.format(config.server, config.port)
        logging.info(content)
        print content

if '__main__' == __name__: #pragma: no cover
    main()
