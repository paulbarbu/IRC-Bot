#Functions fro IRC Bot
try:
    import config
    import err
    import datetime
except ImportError:
    sys.exit(err.load_module)

def get_sender(msg):
    """Returns the user(string) that sent the message

    Searches the string to find the user that sent it
    """
    return msg.split(":")[1].split('!')[0]

def log_write(log, pre, separator, content):
    """Writes 'pre separator content' in 'log'

    Opens file 'log' in 'a' mode and appends the 'pre separator content'
    """


    with open(log, 'a') as log_file:
        try:
            content = pre + separator + content
            log_file.write(content)
        except:
            print 'Error writing to log file!'

def get_datetime():
    """Returns dictionary containing date and time

    dt['time'] - contains current time in hh:mm format(24 hrs)
    dt['date'] - contains current date as dd-mm-yyyy format
    """
    dt = {}

    now = datetime.datetime.now()
    dt['time'] = now.strftime('%H:%M')
    dt['date'] = now.strftime('%d-%m-%Y')

    return dt

def check_cfg(*items):
    """Checks configuration directives to be set

    Return True if configuration directives are not empty, else returns False
    """
    for arg in items:
        if not len(arg):
            return False

    return True

def check_channel(channels):
    """Check channels name to start with a '#' and not contain any spaces

    """
    for channel in channels:
        if not ('#' == channel[0]) or -1 != channel.find(' '):
            return False

    return True

def send_to(command):
    """Get the location where to send the message back

    This function returns a string containing all the protocol related
    information needed by the server to send the command back to the
    user/channel that sent it
    """
    sendto = '' #can be a user name(/query) or a channel

    if -1 != command.find(config.privmsg + config.nick + ' :'):
        #command comes from a query
        sendto = get_sender(command)
    else:
        command = command[command.find(config.privmsg + '#'):]
        command = command[command.find(' ')+1:]
        sendto = command[:command.find(' ')]

    return  config.privmsg + sendto + ' :'
