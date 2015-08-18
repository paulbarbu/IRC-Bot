from BeautifulSoup import BeautifulSoup
import urllib2

def wiki(components): # !wiki <search term>
    '''Returns a wiki link and the first paragraph of the page'''

    main_page = 'https://en.wikipedia.org/wiki/Main_Page'

    wlink = components['arguments'].split('!wiki ') # notice the trailing space
    if 1 == len(wlink): # no search term given, the Main_Page is "displayed"
        response = main_page
    else:
        search_term = wlink[1].lstrip().replace(' ', '_')

        if len(search_term) < 1:
            response = main_page
        else:
            response = 'https://en.wikipedia.org/wiki/' + search_term

    response = response + '\r\n' + get_paragraph(response)

    return response.encode('utf8')

def get_paragraph(wlink):
    '''Gets the first paragraph from a wiki link'''

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

        while 460 < len(msg): # the paragraph cannot be longer than 510
            # characters including the protocol command
            pos = msg.rfind('.')
            msg = msg[:pos]

    return msg
