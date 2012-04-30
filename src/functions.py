import config
import err
import datetime
import socket

def get_sender(msg):
    "Returns the user's nick (string) that sent the message"
    return msg.split(":")[1].split('!')[0]

def log_write(log, pre, separator, content):
    '''Writes a log line into the logs

    Opens file 'log' and appends the 'content' preceded by 'pre' and 'separator'
    '''
    with open(log, 'a') as log_file:
        try:
            log_file.write(pre + separator + content)
        except Exception as e:
            print err.LOG_FAILURE + '\n' + str(e)

def get_datetime():
    '''Returns a dictionary containing the date and time

    dt['time'] - contains current time in hh:mm format(24 hrs)
    dt['date'] - contains current date as dd-mm-yyyy format
    '''
    dt = {}

    now = datetime.datetime.now()
    dt['time'] = now.strftime('%H:%M')
    dt['date'] = now.strftime('%d-%m-%Y')

    return dt

def check_cfg(*items):
    '''Checks configuration directives to be non-empty

    Returns True if all configuration directives are not empty, else returns False
    '''
    for arg in items:
        if not len(arg):
            return False

    return True

def check_channel(channels):
    '''Check the channels' name to start with a '#' and not to contain any spaces

    Returns True if all channels' name are valid, else False
    '''
    for channel in channels:
        if '#' != channel[0] or -1 != channel.find(' '):
            return False

    return True

def send_to(command):
    '''Get the location where to send the message back

    This function returns a string containing all the protocol related
    information needed by the server to send the command back to the
    user/channel that sent it
    '''
    sendto = '' # can be a user's nick(/query) or a channel

    if -1 != command.find('PRIVMSG ' + config.current_nick + ' :'):
        # the command comes from a query
        sendto = get_sender(command)
    else: # the command comes from a channel
        command = command[command.find('PRIVMSG #'):]
        command = command[command.find(' ')+1:]
        sendto = command[:command.find(' ')]

    return 'PRIVMSG ' + sendto + ' :'

def is_registered(user_nick):
    'Creates a client to find if the user issuing the command is registered'

    import socket
    import random
    import string

    logfile = config.log + get_datetime()['date'] + '.log'

    try:
        mini_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        log_write(logfile, get_datetime()['time'], ' <miniclient> ',
                err.NO_SOCKET + '\n')
    else:
        try:
            mini_client.connect((config.server, config.port))
        except IOError:
            content = 'Could not connect to {0}:{1}'.format(config.server,
                    config.port)

            log_write(logfile, get_datetime()['time'], ' <miniclient> ',
                    content + '\n')
        else:
            sample = ''.join(random.sample(string.ascii_lowercase, 5))
            nick = config.current_nick + sample

            mini_client.send('NICK ' + nick + '\r\n')
            mini_client.send('USER ' + nick + ' ' + nick + ' ' + nick + ' :' + \
                    config.real_name + sample + '\r\n')
            mini_client.send('PRIVMSG nickserv :info ' + user_nick + '\r\n')

            while True:
                receive = mini_client.recv(4096)

                if 'NickServ' in receive: # this is the NickServ info response
                    if 'Last seen  : now' in receive: # user registered and online
                        return True
                    elif 'Information on' in receive: # wait for the response
                    # containing the information about the user
                        pass
                    else:
                        return False

        mini_client.close()

    return None

def get_nick():
    for nick in config.nicks:
        yield nick

def sigint_handler(signalnum, frame):
    'This function handles the CTRL-c KeyboardInterrupt'

    if 'irc' in frame.f_globals.keys():
        try:
            frame.f_globals['irc'].close()
        except:
            pass

    dt = get_datetime()
    content = 'Closing: CTRL-c pressed!'

    logfile = config.log + dt['date'] + '.log'
    log_write(logfile, dt['time'], ' <> ', content + '\n')
    print '\n' + content

def name_bot(irc, real_name, logfile):
    '''Try to name the bot in order to be recognised on IRC

    irc - an opened socket
    real_name - bot's real name
    logfile - the name of the logfile to write to

    Return the name of the bot
    '''

    import random
    import string

    nick_generator = get_nick()
    nick = nick_generator.next()
    log_write(logfile, get_datetime()['time'], ' <> ',
        'Set nick to: {0}\n'.format(nick))

    irc.send('NICK ' + nick + '\r\n')
    irc.send('USER ' + nick + ' ' + nick + \
            ' ' + nick + ' :' + real_name + '\r\n')

    while True:
        receive = irc.recv(4096)

        if 'Nickname is already in use' in receive: # try another nickname
            try:
                nick = nick_generator.next()
            except StopIteration: # if no nick is available just make one up
                nick = nick + ''.join(random.sample(string.ascii_lowercase, 5))

            irc.send('NICK ' + nick + '\r\n')

            content = 'Changing nick to: {0}\n'.format(nick)
            log_write(logfile, get_datetime()['time'], ' <> ', content)
        elif nick in receive or 'motd' in receive.lower():
            # successfully connected
            return nick

def create_socket(logfile, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
    '''Returns an unix socket
    or logs the failure message otherwise and returns None
    '''
    try:
        irc = socket.socket(family, type, proto)
    except IOError as e:
        message =  '{0}\n{1}'.format(err.NO_SOCKET, e)
        log_write(logfile, get_datetime()['time'], ' <> ', message + '\n')
        print message

        return None

    return irc

def connect_to(address, s, logfile):
    '''Connect to the specified address through s (a socket object)

    Returns True on success else False and it will log the error in logfile
    '''
    try:
        s.connect(address)
    except IOError as e:
        content = 'Could not connect to {0}\n{1}'.format(address, e)

        log_write(logfile, get_datetime()['time'], ' <> ', content + '\n')
        print content

        return False

    return True

def join_channels(channels, s, logfile):
    '''Send a JOIN command to the server through the s socket
    The variable 'channels' is a list of strings that represend the channels to
    be joined (including the # character)

    Returns True if the command was sent, else False, either way the error or
    the channels joined are logged into the file specified by logfile
    '''
    clist = ','.join(channels)

    try:
        s.send('JOIN ' + clist + '\r\n')
    except IOError as e:
        content = 'Unexpected error while joining {0}: {1}'.format(clist, e)
        log_write(logfile, get_datetime()['time'], ' <> ', content + '\n')
        print content

        return False

    content = 'Joined: {0}'.format(clist)
    log_write(logfile, get_datetime()['time'], ' <> ', content + '\n')
    print content

    return True

def quit_bot(s, logfile):
    '''Send the QUIT commmand through the socket s
    The errors (if they occur) or the quit command is logged in the file
    specified by logfile

    Return True if the command was sent, else False
    '''

    try:
        s.send('QUIT\r\n')
    except IOError as e:
        content = 'Unexpected error while quitting: {0}'.format(e)
        log_write(logfile, get_datetime()['time'], ' <> ', content + '\n')
        print content

        return False

    log_write(logfile, get_datetime()['time'], ' <> ', 'QUIT\r\n')

    return True

def run_cmd(cmd, args, cmds_list):
    '''Search the command (cmd), eg. !twitter in the commands list (cmds_list)
    and try to import its module and run it passing the args to the function
    args will be mostly the irc command components (sender, action, etc.)

    The return value of the imported function is returned from this function too
    '''
    response = None

    if cmd in cmds_list:
        try: # the needed module is imported from 'cmds/'

            # module that needs to be loaded after finding a
            # valid user command
            mod = 'cmds.' + cmd
            mod = __import__(mod, globals(), locals(), [cmd])
        except ImportError: # inexistent module
                response = err.C_INEXISTENT.format(cmd)
        else:

            try: # the module is 'executed'
                # the name of the command is translated into
                # a function's name, then called
                get_response = getattr(mod, cmd)
            except AttributeError:
                # function not defined in module
                response = err.C_INVALID.format(cmd)
            else:
                response = get_response(args)

    return response

def send_response(response, destination, s, logfile):
    '''Attempt to send the response to destination through the s socket
    The response can be either a list or a string, if it's a list then it
    means that the module sent a command on its own (eg. PART)

    The destination can be passed using the send_to function

    The response is logged into the file specified by logfile

    True is returned upon sending the response, None if the response was empty
    or False if an error occurred while sending the response
    '''
    if response is not None and len(response): # send the response and log it
        if type(response) == type(str()):
            # the module sent just a string so
            # I have to compose the command

            # a multi-line command must be split
            crlf_pos = response[:-2].find('\r\n')
            if -1 != crlf_pos:
                crlf_pos = crlf_pos + 2 # jump over '\r\n'
                response = response[:crlf_pos] + \
                        destination + response[crlf_pos:]

            response = destination + response
        else: # the module sent a command like WHOIS or KICK
            response = ' '.join(response)

        # append CRLF if not already appended
        if '\r\n' != response[-2:]:
            response = response + '\r\n'

        try:
            s.send(response)
        except IOError as e:
            log_write(logfile, get_datetime()['time'], ' <> ',
                'Unexpected error while sending the response: {0}\n'.format(e))

            return False

        log_write(logfile, get_datetime()['time'], ' <> ', response)

        return True

    return None
