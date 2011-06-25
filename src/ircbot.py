import socket

#Config {
server = 'chat.freenode.net'
port = 6667

nick = 'PPyBot'
realName = 'Paul Python Bot'

quit_msg = 'QUIT :Bye!\r\n'

channel = '#yet-another-project'
#}

#Preparing standard messages{
nick_auth = 'NICK ' + nick + '\r\n'
user_auth = 'USER ' + nick + ' ' + nick + ' ' + nick + ' :' + realName + '\r\n'

channel_join = 'JOIN ' + channel + '\r\n'
channel_part = 'PART ' + channel + '\r\n'
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

        irc.send('PRIVMSG ' + channel + ' :Hello world!\r\n')

        while True:
            response = irc.recv(4096)
            buff = buff + response

            if -1 != buff.find('\n'):
                command = buff[0 : buff.find('\n')]
                buff = buff[buff.find('\n')+1:]

                print 'C: {0}'.format(command)
                print 'B: {0}'.format(buff)

                if -1 != command.find('PING'): #PING PONG between server and client
                    irc.send('PONG ' + command.split()[1] + '\r\n')

                elif -1 != command.find('!google'): # !google <nick>
                    irc.send('PRIVMSG ' + channel + ' :' + str(command.split()[-1])
                            + ', cauta te rog pe Google: http://google.ro\r\n')

                elif -1 != command.find('!wiki'): # !wiki <search term>
                    irc.send('PRIVMSG ' + channel + ' :http://en.wikipedia.org/wiki/'
                            + command.split('!wiki')[1].lstrip().replace(' ', '_')
                            + '\r\n')

                elif -1 != command.find('!quit'): # !quit
                    irc.send(quit_msg)
                    break;
                else:
                    buff = ""

        #Leave(part) channel
        irc.send(channel_part)

        irc.close()
