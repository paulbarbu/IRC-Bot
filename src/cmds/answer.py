def answer(components): # !answer
    """Replies the ultimate answer to the user

    """
    response = ''

    if components['arguments'] == '!answer':
        #the user sent just the command, no garbage
        response = 'The Answer to the Ultimate Question of Life, the Universe, and Everything is 42!'

    return response
