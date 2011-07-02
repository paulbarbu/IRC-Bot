try:
    from BeautifulSoup import BeautifulSoup
    import urllib2
    import config
    import err
except ImportError:
    sys.exit(err.LOAD_MODULE)

def wiki(command): # !wiki <search term>
    """Returns a wiki link and the first paragraph of the page

    Tries to return a link to the wiki page for the <search term> and the first
    paragraph of the page
    """

    wlink = command.split('!wiki ') #notice the trailing space
    if 1 == len(wlink): #no search term given
        response = 'Usage: !wiki <search term>'
    else:
        response = 'http://en.wikipedia.org/wiki/' + \
                wlink[1].lstrip().replace(' ', '_')
        response = response + '\r\n' + get_para(response)

    return str(response)

def get_para(wlink):
    """Gets the first paragraph from a wiki link

    """

    msg = ''
    try:
        page_request = urllib2.Request(wlink)
        page_request.add_header('User-agent', 'Mozilla/5.0')
        page = urllib2.urlopen(page_request)
    except IOError:
        msg = 'Cannot acces link!'
    else:

        soup = BeautifulSoup(page)
        msg = ''.join(soup.find('div', { 'id' : 'bodyContent'}).p.findAll(text=True))

        while (500 - len(config.privmsg)) < len(msg): #the paragraph cannot be
            #longer than 510 characters including the protocol command
            pos = msg.rfind('.')
            msg = msg[:pos]

    return msg
