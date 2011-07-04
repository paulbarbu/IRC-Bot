try:
    import err
    import config
    import time
    import datetime
except ImportError:
    sys.exit(err.load_module)

def uptime(command):
    """computes the uptime of the bot

    The function uses config.start_time as point of start
    """

    response = ''
    end_time = time.time()

    uptime = end_time - config.start_time

    uptime = str(datetime.timedelta(seconds=int(uptime)))

    response = 'Uptime: ' + uptime

    return response
