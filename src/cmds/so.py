import stackexchange
import urllib2

api_key = 'TODO: populate this variable'

def so(components): # !so <search term>
    '''Search the Stack Overflow site and returns the first question's title and
    URL
    '''
    response = ''

    terms = components['arguments'].split('!so ') # notice the trailing space

    if 1 == len(terms): # no search term given
        response = 'Usage: !so <search term>'
    else:
        if terms[1].lstrip():
            so = stackexchange.Site(stackexchange.StackOverflow, api_key)

            try:
                qs = so.search(intitle = terms[1].lstrip())
            except urllib2.HTTPError, e:
                response = "The server couldn't fulfill the request!"

                if hasattr(e, 'reason'): # pragma: no branch
                    response = response + '\r\nReason: ' + str(e.reason)

                if hasattr(e, 'code'): # pragma: no branch
                    response = response + '\r\nCode: ' + str(e.code)
            else:

                if 1 <= len(qs):
                    response = qs[0].title + '\r\n' + qs[0].url
                else:
                    response = 'Not found: ' + terms[1]
        else:
            response = 'Usage: !so <search term>'

    return str(response)
