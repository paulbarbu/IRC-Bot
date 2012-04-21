# -*- coding: utf-8 -*-

##@file google.py
#@brief !google \<search term\>
#@author paullik
#@ingroup moduleFiles

from apiclient.discovery import build

def google(components): # !google <search term>
    """Returns the link and the description of the first result from a google search

    Depends on Google API(custom search)
    """

    response = ''

    terms = components['arguments'].split('!google ') #notice the trailing space

    if 2 == len(terms) and 1 < terms[1].lstrip():
        service = build("customsearch", "v1",
                developerKey="AIzaSyCy6tveUHlfNQDUtH0TJrF6PtU0h894S2I")

        res = service.cse().list(
            q = terms[1].lstrip(),
            cx = '005983647730461686104:qfayqkczxfg',
        ).execute()

        if 1 <= res['queries']['request'][0]['totalResults']:
            result = res['items'][0]
            response = result['link'] + '\r\n' + result['snippet']

        else:
            response = 'Not found: ' + terms[1]

    else:
        response = 'Usage: !google <search term>'

    return str(response)
