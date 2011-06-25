import socket

#Config {
server = 'chat.freenode.net'
port = 6667

nick = 'PPyBot'
realName = 'Paul Python Bot'

channel = '#botwar'

quit_msg = 'Bye bye'
#}

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

                elif -1 != command.find('!google'): # !google <nick>
                    command = command.split()

                    if 4 == len(command): #no nick given
                        irc.send(privmsg + 'Usage: !google <nick>\r\n')
                    else:
                        irc.send(privmsg + str(command[-1]) +
                            ', please search on google: http://google.ro\r\n')

                elif -1 != command.find('!wiki'): # !wiki <search term>
                    command = command.split('!wiki ')
                    if 1 == len(command): #no search term given
                        irc.send(privmsg + 'Usage: !wiki <search term>\r\n')
                    else:
                        irc.send(privmsg + 'http://en.wikipedia.org/wiki/' +
                            command[1].lstrip().replace(' ', '_')
                            + '\r\n')

                elif -1 != command.find('!quit'): # !quit
                    irc.send(channel_part)
                    break;

                else:
                    buff = ""

        #Leave(part) channel
        irc.send('QUIT\r\n')

        irc.close()

        print "Exitied with message: {0}".format(quit_msg)
