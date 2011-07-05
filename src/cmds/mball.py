import err
import config
import random

def mball(command):
    """Tells you what your future is

    Shuffles the answers list and then randomly picks one
    """
    answers = ['It is certain', 'It is decidedly so', 'Without a doubt', \
            'Yes - definitely', 'You may rely on it', 'As I see it, yes',\
            'Most likely', 'Outlook good', 'Signs point to yes', 'Yes', \
            'Reply hazy, try again', 'Ask again later', 'Better not tell you now', \
            'Cannot predict now', 'Concentrate and ask again', 'Don\'t count on it', \
            'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful']

    random.shuffle(answers)
    response = 'Magic Ball says: ' + random.choice(answers)

    return response

