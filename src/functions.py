import datetime

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

