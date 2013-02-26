import config
import err
import datetime
import socket
import threading

def get_sender(msg):
    "Returns the user's nick (string) that sent the message"
    return msg.split(":")[1].split('!')[0]

log_lock = threading.Lock()
def log_write(log, pre, separator, content):
    '''Writes a log line into the logs

    Opens file 'log' and appends the 'content' preceded by 'pre' and 'separator'
    '''
    with open(log, 'a') as log_file, log_lock:
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

def is_registered(s, user_nick):
    '''Determines if the user_nick is online and registered to NickServ

    Returns true if user_nick is registered and online, else False
    '''
    s.send('PRIVMSG nickserv :info ' + user_nick + '\r\n')

    while True:
        receive = s.recv(4096)

        if 'NickServ' in receive: # this is the NickServ info response
            if 'Last seen  : now' in receive: # user registered and online
                return True
            elif 'Information on' in receive: # wait for the response
            # containing the information about the user
                pass
            else:
                return False

def get_nick(nicks):
    for nick in nicks:
        yield nick

def sigint_handler(signalnum, frame):
    '''This function handles the CTRL-c KeyboardInterrupt

    Getting the name of the logfile here could have been avoided, but it isn't
    because avoiding it would increase the complexity of a code (a factory
    should have been used to create a sigint_handler that uses the proper
    logfile)
    '''

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

def name_bot(irc, nicks, real_name, logfile):
    '''Try to name the bot in order to be recognised on IRC

    irc - an opened socket
    nicks - a list of strings to choose the nick from
    real_name - bot's real name
    logfile - the name of the logfile to write to


    Return the name of the bot
    '''

    import random
    import string

    nick_generator = get_nick(nicks)
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
    '''Returns an unix socket or logs the failure message and returns None'''
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


def get_cmd(cmd, cmds_list, logfile):
    '''Search the command (cmd), eg. !twitter in the commands list (cmds_list)
    and try to import its module

    The return value is the function that represents the command or None if the
    command doesn't exist or it's not defined properly
    '''
    if cmd not in cmds_list:
        return None

    try: # the command's module needs to be imported from 'cmds/'
        mod = 'cmds.' + cmd
        mod = __import__(mod, globals(), locals(), [cmd])
    except ImportError as e: # inexistent module
        log_write(logfile, err.C_INEXISTENT.format(cmd), ' <> ', str(e) + '\n')
        return None

    try:
        # the name of the command is translated into a function's name,
        # then returned
        callable_cmd = getattr(mod, cmd)
    except AttributeError as e:
        # function not defined in module
        log_write(logfile, err.C_INVALID.format(cmd), ' <> ', str(e) + '\n')
        return None

    return callable_cmd


def run_cmd(socket, executor, to, cmd, arguments, logfile):
    '''Create a future object for running a command asynchronously and add a
    callback to send the response of the command back to irc
    '''
    def cb(f):
        try:
            response = f.result()
        except Exception as e:
            response = err.C_EXCEPTION.format(cmd.__name__)
            log_write(logfile, response, ' <> ', str(e) + '\n')

        send_response(response, to, socket, logfile)

    future = executor.submit(cmd, arguments)
    future.add_done_callback(cb)


send_response_lock = threading.Lock()
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
            while -1 != crlf_pos:
                crlf_pos = crlf_pos + 2 # jump over '\r\n'
                response = response[:crlf_pos] + \
                        destination + response[crlf_pos:]

                next_crlf_pos = response[crlf_pos:-2].find('\r\n')
                if -1 != next_crlf_pos:
                    crlf_pos = crlf_pos + next_crlf_pos
                else:
                    crlf_pos = -1

            response = destination + response
        else: # the module sent a command like WHOIS or KICK
            response = ' '.join(response)

        # append CRLF if not already appended
        if '\r\n' != response[-2:]:
            response = response + '\r\n'

        try:
            with send_response_lock:
                s.send(response)
        except IOError as e:
            log_write(logfile, get_datetime()['time'], ' <> ',
                'Unexpected error while sending the response: {0}\n'.format(e))

            return False

        log_write(logfile, get_datetime()['time'], ' <> ', response)

        return True

    return None
