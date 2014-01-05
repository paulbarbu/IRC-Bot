import config
import err
import datetime
import socket
import threading
import os
import logging

def get_sender(msg):
    "Returns the user's nick (string) that sent the message"
    return msg.split(":")[1].split('!')[0]


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
    '''

    if 'irc' in frame.f_globals.keys():
        try:
            frame.f_globals['irc'].close()
        except:
            pass

    content = 'Closing: CTRL-c pressed!'

    logging.info(content)
    print '\n' + content

def name_bot(irc, nicks, real_name):
    '''Try to name the bot in order to be recognised on IRC

    irc - an opened socket
    nicks - a list of strings to choose the nick from
    real_name - bot's real name

    Return the name of the bot
    '''

    import random
    import string

    nick_generator = get_nick(nicks)
    nick = nick_generator.next()
    logging.info('Set nick to: {0}\n'.format(nick))

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
            logging.info(content)
        elif nick in receive or 'motd' in receive.lower():
            # successfully connected
            return nick


def create_socket(family=socket.AF_INET, t=socket.SOCK_STREAM, proto=0):
    '''Returns an unix socket or logs the failure message and returns None'''
    try:
        irc = socket.socket(family, t, proto)
    except IOError as e:
        message =  '{0}\n{1}'.format(err.NO_SOCKET, e)
        logging.error(message)
        print message

        return None

    return irc


def connect_to(address, s):
    '''Connect to the specified address through s (a socket object)

    Returns True on success else False
    '''
    try:
        s.connect(address)
    except IOError as e:
        content = 'Could not connect to {0}\n{1}'.format(address, e)

        logging.error(content)
        print content

        return False

    return True


def join_channels(channels, s):
    '''Send a JOIN command to the server through the s socket
    The variable 'channels' is a list of strings that represend the channels to
    be joined (including the # character)

    Returns True if the command was sent, else False
    '''
    clist = ','.join(channels)

    try:
        s.send('JOIN ' + clist + '\r\n')
    except IOError as e:
        content = 'Unexpected error while joining {0}: {1}'.format(clist, e)
        logging.error(content)
        print content

        return False

    content = 'Joined: {0}'.format(clist)
    logging.info(content)
    print content

    return True


def quit_bot(s):
    '''Send the QUIT commmand through the socket s

    Return True if the command was sent, else False
    '''

    try:
        s.send('QUIT\r\n')
    except IOError as e:
        content = 'Unexpected error while quitting: {0}'.format(e)
        logging.error(content)
        print content

        return False

    logging.info('QUIT')

    return True


def get_cmd(cmd, cmds_list):
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
        logging.error(err.C_INEXISTENT.format(cmd) + str(e))
        return None

    try:
        # the name of the command is translated into a function's name,
        # then returned
        callable_cmd = getattr(mod, cmd)
    except AttributeError as e:
        # function not defined in module
        logging.error(err.C_INVALID.format(cmd) + str(e))
        return None

    return callable_cmd


def run_cmd(sock, executor, to, cmd, arguments):
    '''Create a future object for running a command asynchronously and add a
    callback to send the response of the command back to irc
    '''
    def cb(f):
        try:
            response = f.result()
        except Exception as e: # TODO: raise a specific exception form the cmds
            response = err.C_EXCEPTION.format(cmd.__name__)
            logging.error(e)

        send_response(response, to, sock)

    future = executor.submit(cmd, arguments)
    future.add_done_callback(cb)


send_response_lock = threading.Lock()
def send_response(response, destination, s):
    '''Attempt to send the response to destination through the s socket
    The response can be either a list or a string, if it's a list then it
    means that the module sent a command on its own (eg. PART)

    The destination can be passed using the send_to function

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
            logging.error('Unexpected error while sending the response: {0}\n'
                .format(e))

            return False

        logging.debug(response)

        return True

    return None
