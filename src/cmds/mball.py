import random

def mball(components):
    '''Return a random entry from the shuffled list'''

    answers = ['It is certain', 'It is decidedly so', 'Without a doubt', \
        'Yes - definitely', 'You may rely on it', 'As I see it, yes',\
        'Most likely', 'Outlook good', 'Signs point to yes', 'Yes', \
        'Reply hazy, try again', 'Ask again later', 'Better not tell you now', \
        'Cannot predict now', 'Concentrate and ask again', 'Don\'t count on it', \
        'My reply is no', 'My sources say no', 'Outlook not so good', \
        'Very doubtful'
    ]
    response = ''

    if components['arguments'] == '!mball':
        # the user sent just the command, no garbage
        random.shuffle(answers)
        response = 'Magic Ball says: ' + random.choice(answers)

    return response

