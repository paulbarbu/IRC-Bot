import config
import time
import datetime

def uptime(components):
    '''Computes the uptime of the bot

    The function uses config.start_time as the time the bot was started
    '''
    response = ''

    if components['arguments'] == '!uptime':
        # the user sent just the command, no garbage
        end_time = time.time()
        uptime = end_time - config.start_time
        uptime = str(datetime.timedelta(seconds=int(uptime)))
        response = 'Uptime: ' + uptime

    return response
