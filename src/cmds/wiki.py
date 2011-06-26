try:
    from BeautifulSoup import BeautifulSoup
    import urllib2
    import config
    import err
except ImportError:
    sys.exit(err.load_module)

def wiki(command):
    """Replies a wiki link with the searched term

    Tries to return a link to the wiki page for the <search term> and the first
    paragraph of the page
    """
    wlink = command.split('!wiki ') #notice the trailing space
    if 1 == len(wlink): #no search term given
        response = 'Usage: !wiki <search term>\r\n'
    else:
        response = 'http://en.wikipedia.org/wiki/' + wlink[1].lstrip().replace(' ', '_')
        response = response + '\r\n' + config.privmsg + get_para(response) + '\r\n'

    return config.privmsg + response

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

    return msg
