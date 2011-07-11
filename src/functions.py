##@file functions.py
#@brief Functions file
#@author paullik
#@ingroup kernelFiles

import config
import err
import datetime

def get_sender(msg):
    """Returns the user(string) that sent the message

    Parses the string to find the user that sent a command and returns the
    user's nickname
    """

    return msg.split(":")[1].split('!')[0]

def log_write(log, pre, separator, content):
    """Writes a log line into the logs

    Opens file 'log' and appends the 'content' preceded by 'pre' and 'separator'
    """

    with open(log, 'a') as log_file:
        try:
            content = pre + separator + content
            log_file.write(content)
        except:
            print 'Error writing to log file!'

def get_datetime():
    """Returns a dictionary containing the date and time

    dt['time'] - contains current time in hh:mm format(24 hrs)
    dt['date'] - contains current date as dd-mm-yyyy format
    """

    dt = {}

    now = datetime.datetime.now()
    dt['time'] = now.strftime('%H:%M')
    dt['date'] = now.strftime('%d-%m-%Y')

    return dt

def check_cfg(*items):
    """Checks configuration directives to be non-empty

    Returns True if all configuration directives are not empty, else returns False
    """
    for arg in items:
        if not len(arg):
            return False

    return True

def check_channel(channels):
    """Check the channels' name to start with a '#' and not contain any spaces

    Returns True if all channels' name are valid, else False
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

    if -1 != command.find('PRIVMSG ' + config.nick + ' :'):
        #command comes from a query
        sendto = get_sender(command)
    else:
        command = command[command.find('PRIVMSG #'):]
        command = command[command.find(' ')+1:]
        sendto = command[:command.find(' ')]

    return 'PRIVMSG ' + sendto + ' :'
