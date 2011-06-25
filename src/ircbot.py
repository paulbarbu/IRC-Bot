#Main file for IRC Bot

from config import *
from functions import *
import socket

#Preparing standard messages{
nick_auth = 'NICK ' + nick + '\r\n'
user_auth = 'USER ' + nick + ' ' + nick + ' ' + nick + ' :' + realName + '\r\n'

channel_join = 'JOIN ' + channel + '\r\n'
channel_part = 'PART ' + channel + ' :' + quit_msg + '\r\n'

privmsg = 'PRIVMSG ' + channel + ' :'
quit = 'QUIT\r\n'
#}

dt = get_datetime()

logfile = log + dt['date'] + '.log'
content = 'Started on {0}:{1}, channel: {2}, with nick: {3}'.format(server,
        port, channel, nick)

log_write(logfile, dt['time'], ' <> ', content + '\n')

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
        content = 'Could not connect to {0}{1}'.format(server, port)
        log_write(logfile, dt['time'], ' <> ', content + '\n')
        print content
    else:
        buff = ""
        content = 'Connected to {0}:{1}'.format(server, port)
        log_write(logfile, dt['time'], ' <> ', content + '\n')
        print content

        #Join server & authenticate
        irc.send(nick_auth)
        irc.send(user_auth)

        #Join channel
        irc.send(channel_join)
        content = 'Joined: {0}'.format(channel)
        log_write(logfile, dt['time'], ' <> ', content + '\n')
        print content

        while True:
            receive = irc.recv(4096)
            buff = buff + receive

            if -1 != buff.find('\n'):
                command = buff[0 : buff.find('\n')]
                buff = buff[buff.find('\n')+1:]

                if -1 != command.find('PING'): #PING PONG between server and client
                    response = 'PONG ' + command.split()[1] + '\r\n'
                    irc.send(response)

                    dt = get_datetime()
                    log_write(logfile, dt['time'], ' <> ', command + '\n')
                    log_write(logfile, dt['time'], ' <> ', response)

                elif -1 != command.find('!search'): # !google <nick>
                    nick = command.split()

                    if 4 == len(nick): #no nick given
                        response = privmsg + 'Usage: !search <nick>\r\n'
                    else:
                        response = privmsg + str(nick[-1]) + ', please search on: ' + search + '\r\n'

                    irc.send(response)

                    dt = get_datetime()
                    log_write(logfile, dt['time'], ' <> ', command + '\n')
                    log_write(logfile, dt['time'], ' <> ', response)

                elif -1 != command.find('!wiki'): # !wiki <search term>
                    wlink = command.split('!wiki ')
                    if 1 == len(wlink): #no search term given
                        response = privmsg + 'Usage: !wiki <search term>\r\n'
                    else:
                        response = privmsg + 'http://en.wikipedia.org/wiki/' + wlink[1].lstrip().replace(' ', '_') + '\r\n'

                    irc.send(response)

                    dt = get_datetime()
                    log_write(logfile, dt['time'], ' <> ', command + '\n')
                    log_write(logfile, dt['time'], ' <> ', response)

                elif -1 != command.find('!quit'): # !quit
                    dt = get_datetime()
                    sender = get_sender(command)
                    if sender in owner:
                        response = channel_part
                        irc.send(response)
                        log_write(logfile, dt['time'], ' <> ', command + '\n')
                        log_write(logfile, dt['time'], ' <> ', response)
                        break;
                    else:
                        response = privmsg + 'This command can be run only by the' + ' owner(s)!\r\n'
                        irc.send(response)
                        log_write(logfile, dt['time'], ' <> ', command + '\n')
                        log_write(logfile, dt['time'], ' <> ', response)

                elif -1 != command.find('!answer') or -1 != command.find('!42'): # !answer
                    response = privmsg + 'The Answer to the Ultimate Question of Life, the Universe, and Everything is 42\r\n'
                    irc.send(response)

                else:
                    buff = ""

        #Leave(part) channel
        irc.send(quit)
        dt = get_datetime()
        log_write(logfile, dt['time'], ' <> ', quit)

        irc.close()

        content = 'Exited with message: {0}'.format(quit_msg)
        log_write(logfile, dt['time'], ' <> ', content + '\n')
        print content

