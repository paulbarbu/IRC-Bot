# -*- coding: utf-8 -*-

try:
    import config
    import err
    from apiclient.discovery import build
except ImportError:
    sys.exit(err.LOAD_MODULE)

def google(command): # !google <search term>
    """Gets the first result from a google search

    Is dependant on Google API(custom search)
    """

    response = ''

    terms = command.split('!google ') #notice the trailing space
    if 1 == len(terms): #no search term given
        response = 'Usage: !google <search term>'
    else:
        service = build("customsearch", "v1",
                developerKey="AIzaSyCy6tveUHlfNQDUtH0TJrF6PtU0h894S2I")

        res = service.cse().list(
            q = terms[1].lstrip(),
            cx = '005983647730461686104:qfayqkczxfg',
        ).execute()

        result = res['items'][0]

        response = result['link'] + '\r\n' + result['snippet']

    return str(response)
