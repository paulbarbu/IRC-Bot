from config import *
from functions import *
import socket

#Preparing standard messages{
nick_auth = 'NICK ' + nick + '\r\n'
user_auth = 'USER ' + nick + ' ' + nick + ' ' + nick + ' :' + realName + '\r\n'

channel_join = 'JOIN ' + channel + '\r\n'
channel_part = 'PART ' + channel + ' :' + quit_msg + '\r\n'

privmsg = 'PRIVMSG ' + channel + ' :'
#}

try:
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.socket:
    print 'Could not create a socket!'
else:
    try:
        irc.connect((server, port))
        response = irc.recv(4096)
    except IOError:
        print 'Could not connect to {0}{1}'.format(server, port)
    else:
        buff = ""
        print 'Connected to {0}:{1}'.format(server, port)

        #Join server & authenticate
        irc.send(nick_auth)
        irc.send(user_auth)

        #Join channel
        irc.send(channel_join)
        print 'Joined: {0}'.format(channel)

        while True:
            response = irc.recv(4096)
            buff = buff + response

            if -1 != buff.find('\n'):
                command = buff[0 : buff.find('\n')]
                buff = buff[buff.find('\n')+1:]

                if -1 != command.find('PING'): #PING PONG between server and client
                    irc.send('PONG ' + command.split()[1] + '\r\n')

                elif -1 != command.find('!search'): # !google <nick>
                    command = command.split()

                    if 4 == len(command): #no nick given
                        irc.send(privmsg + 'Usage: !search <nick>\r\n')
                    else:
                        irc.send(privmsg + str(command[-1]) +
                            ', please search on: ' + search + '\r\n')

                elif -1 != command.find('!wiki'): # !wiki <search term>
                    command = command.split('!wiki ')
                    if 1 == len(command): #no search term given
                        irc.send(privmsg + 'Usage: !wiki <search term>\r\n')
                    else:
                        irc.send(privmsg + 'http://en.wikipedia.org/wiki/' +
                            command[1].lstrip().replace(' ', '_')
                            + '\r\n')

                elif -1 != command.find('!quit'): # !quit
                    sender = get_sender(command)
                    if sender in owner:
                        irc.send(channel_part)
                        break;
                    else:
                        irc.send(privmsg + 'This command can be run only by the'
                                + ' owner(s)!\r\n')

                else:
                    buff = ""

        #Leave(part) channel
        irc.send('QUIT\r\n')

        irc.close()

        print "Exited with message: {0}".format(quit_msg)
