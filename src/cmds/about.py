try:
    import config
    import err
except ImportError:
    sys.exit(err.load_module)

def about(command):
    response = 'Author: Paullik @ http://github.com/paullik'
    return response
