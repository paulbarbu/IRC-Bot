try:
    import config
    import err
except ImportError:
    sys.exit(err.load_module)

def answer(command): # !answer
    """Replies the ultimate answer to the user

    """
    response = 'The Answer to the Ultimate Question of Life, the Universe, and Everything is 42!'
    return response
