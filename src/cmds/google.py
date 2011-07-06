# -*- coding: utf-8 -*-

from apiclient.discovery import build
import pprint

def google(components): # !google <search term>
    """Gets the first result from a google search

    Is dependant on Google API(custom search)
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

        pprint.pprint(res)

        if 1 <= res['queries']['request'][0]['totalResults']:
            result = res['items'][0]
            response = result['link'] + '\r\n' + result['snippet']

        else:
            response = 'Not found: ' + terms[1]

    else:
        response = 'Usage: !google <search term>'

    return str(response)
