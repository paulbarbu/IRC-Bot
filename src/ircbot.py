#! /usr/bin/env python2.7
import sys
import signal
import futures

import config
import parser
import err
from functions import *

def run(socket, channels, cmds, auto_cmds, nick, logfile):
    # buffer for some command received
    buff = ''
    jobs = {}

    #TODO: what happens if I use all the workers?
    #TODO: now the bot is VERY unresponsive
    #TODO: check what happens on exceptions and when the commands do
    #something that might kill the bot

    #I cannot send socket to a ProcessPoolExecutor since it isn't
    #pickable, so for now I'm stuck with ThreadPoolExecutor
    with futures.ThreadPoolExecutor(max_workers=len(cmds) + len(auto_cmds)) as executor:
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
                        # search in commands list only if the message from the
                        # user starts with an exclamation mark

                        pos = components['arguments'].find(' ')
                        if -1 == pos:
                            pos = len(components['arguments'])

                        # get the command issued to the bot without the "!"
                        cmd = components['arguments'][1:pos]
                        run_cmd(socket, executor, jobs, to, cmd, components, cmds)

                    # run auto commands
                    for cmd in config.auto_cmds_list:
                        run_cmd(socket, executor, jobs, to, cmd,
                                components, auto_cmds)

                elif 'KICK' == components['action'] and \
                    nick == components['action_args'][1]:
                        channels.remove(components['action_args'][0])

                elif 'QUIT' == components['action'] and \
                        -1 != components['arguments'].find('Ping timeout: '):
                    channels[:] = []

                # this call is still necessary in case that a PONG response
                # should be sent and a job has finished working
                send_response(response, to, socket, logfile)

                buff = ''

            for job in futures.wait(jobs, 0).done:
                send_response(job.result(), jobs[job], socket,
                        logfile)
                del jobs[job]



def main():
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

        config.current_nick = name_bot(socket, config.nicks, config.real_name,
            logfile)
        joined = join_channels(config.channels, socket, logfile)

        if joined:
            run(socket, config.channels, config.cmds_list,
                    config.auto_cmds_list, config.current_nick, logfile)

        quit_bot(socket, logfile)
        socket.close()

        content = 'Disconnected from {0}:{1}'.format(
            config.server, config.port)
        log_write(logfile, get_datetime()['time'], ' <> ', content + '\n')
        print content

if __name__ == '__main__': #pragma: no cover
    main()
