import config
import err
import datetime

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
        except:
            print err.LOG_FAILURE

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
    else:
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
    except socket.socket:
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
                    config.realName + sample + '\r\n')
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
    finally:
        mini_client.close()

    return None

def get_nick():
    for nick in config.nicks:
        yield nick

def sigint_handler(signalnum, frame):
    'This function handles the CTRL-c KeyboardInterrupt'

    dt = get_datetime()
    content = 'Closing: CTRL-c pressed!'

    logfile = config.log + dt['date'] + '.log'
    log_write(logfile, dt['time'], ' <> ', content + '\n')
    print '\n' + content
