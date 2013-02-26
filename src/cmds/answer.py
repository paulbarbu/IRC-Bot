def answer(components): # !answer
    '''Returns the ultimate answer'''
    response = ''

    if components['arguments'] == '!answer':
        # the user sent just the command, no garbage
        response = 'The Answer to the Ultimate Question of Life, the Universe, and Everything is 42!'

    return response
