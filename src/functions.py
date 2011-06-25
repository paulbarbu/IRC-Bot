def get_sender(msg):
    """Returns the user(string) that sent the message

    Searches the string to find the user that sent it
    """
    return msg.split(":")[1].split('!')[0]
