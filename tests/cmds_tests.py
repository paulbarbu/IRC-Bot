import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../src/')))

import unittest
from mock import patch, MagicMock, Mock
from contextlib import nested

class CmdsTests(unittest.TestCase):
    def test_about(self):
        from cmds.about import about
        s = Mock()

        self.assertEqual(about(s, {'arguments': '!about garbage'}), '')
        self.assertEqual(about(s, {'arguments': '!about'}),
            'Author: Paullik @ http://github.com/paullik')

    def test_answer(self):
        from cmds.answer import answer
        s = Mock()

        self.assertEqual(answer(s, {'arguments': '!answer garbage'}), '')
        self.assertEqual(answer(s, {'arguments': '!answer'}),
            'The Answer to the Ultimate Question of Life, the Universe, and Everything is 42!')

    def test_channels(self):
        from cmds.channels import channels
        s = Mock()

        self.assertEqual(channels(s, {'arguments': '!channels garbage'}), '')

        with nested(
            patch('cmds.channels.is_registered'),
            patch('config.owner', new=[]),
            patch('config.channels', new=[]),
            patch('config.current_nick', new='test'),
        ) as (is_registered, owner, chan, nick):

            chan.append('#foobar')
            owner.append('foo')

            is_registered.return_value = False
            self.assertEqual(channels(s, {'arguments': '!channels',
                'sender': 'baz'}), 'This command can be run only by the owners!')

            is_registered.return_value = True
            self.assertEqual(channels(s, {'arguments': '!channels',
                'sender': 'baz'}), 'This command can be run only by the owners!')

            is_registered.return_value = False
            self.assertEqual(channels(s, {'arguments': '!channels',
                'sender': 'baz'}), 'This command can be run only by the owners!')

            is_registered.return_value = True
            owner.append('baz')
            self.assertEqual(channels(s, {'arguments': '!channels',
                'sender': 'baz'}), 'test is connected to: #foobar')

    def test_google(self):
        from cmds.google import google
        s = Mock()

        result = {
            'queries': {
                'request':
                    [{'totalResults': 0}]
            },
            'items': [{
                'link': 'http://foobar.baz',
                'snippet': 'Details about foobar',
            }]
        }

        def getitem(name):
            return result[name]

        def setitem(name, val):
            result[name] = val

        self.assertEqual(google(s, {'arguments': '!google'}),
            'Usage: !google <search term>')

        self.assertEqual(google(s, {'arguments': '!google   '}),
            'Usage: !google <search term>')

        with patch('cmds.google.build') as build:
            query_result = MagicMock(spec_set=dict)
            query_result.__setitem__.side_effect = setitem
            query_result.__getitem__.side_effect = getitem

            service_mock = Mock()
            service_mock.cse.return_value.list.return_value.execute.return_value = query_result

            build.return_value = service_mock

            self.assertEqual(google(s, {'arguments': '!google foo bar'}),
                'Not found: foo bar')

            result['queries']['request'][0]['totalResults'] = 42
            self.assertEqual(google(s, {'arguments': '!google foo bar'}),
                'http://foobar.baz\r\nDetails about foobar')

    def test_help(self):
        from cmds.help import help
        s = Mock()

        self.assertEqual(help(s, {'arguments': '!help garbage'}), '')

        with patch('config.cmds_list', new=[]) as config:
            config.extend(['foo', 'bar'])

            self.assertEqual(help(s, {'arguments': '!help'}),
                '2 available commands: foo bar ') #notice the space

    def test_join(self):
        from cmds.join import join
        s = Mock()

        self.assertEqual(join(s, {'arguments': '!join', 'sender': 'foo'}),
            'Usage: !join <#channel >+')

        with nested(
            patch('cmds.join.is_registered'),
            patch('config.owner', new=[]),
            patch('config.channels', new=[]),
        ) as (is_registered, owner, chan):

            is_registered.return_value = False
            owner.extend(['baz', 'bar'])
            self.assertEqual(join(s, {'arguments': '!join #chan',
                'sender': 'foo'}),
                'This command can be run only by the owners!')

            is_registered.return_value = True
            self.assertEqual(join(s, {'arguments': '!join #chan',
                'sender': 'foo'}),
                'This command can be run only by the owners!')

            is_registered.return_value = False
            owner.append('foo')
            self.assertEqual(join(s, {'arguments': '!join #chan',
                'sender': 'foo'}),
                'This command can be run only by the owners!')

            is_registered.return_value = True
            self.assertListEqual(join(s, {'arguments': '!join #chan',
                'sender': 'foo', 'action_args': ['#foo']}),
                ['JOIN ', '#chan', '\r\nPRIVMSG #foo :Joined: #chan'])

            self.assertEqual(join(s, {'arguments': '!join chan chan2',
                'sender': 'foo'}),
                'Invalid channels names, usage: !join <#channel >+')

            self.assertListEqual(join(s, {'arguments': '!join #chan #c',
                'sender': 'foo', 'action_args': ['#foo']}),
                ['JOIN ', '#c', '\r\nPRIVMSG #foo :Joined: #c'])

            self.assertListEqual(join(s, {'arguments': '!join foobar   #test',
                'sender': 'foo', 'action_args': ['#foo']}),
                ['JOIN ', '#test', '\r\nPRIVMSG #foo :Joined: #test'])

            self.assertEqual(join(s, {'arguments': '!join    ',
                'sender': 'foo'}),
                'Invalid channels names, usage: !join <#channel >+')

            self.assertListEqual(['#chan', '#c', '#test'], chan)

    def test_mball(self):
        from cmds.mball import mball
        s = Mock()

        self.assertEqual(mball(s, {'arguments': '!mball garbage'}), '')

        self.assertRegexpMatches(mball(s, {'arguments': '!mball'}),
            'Magic Ball says: *')

    def test_quit(self):
        from cmds.quit import quit
        s = Mock()

        with nested(
            patch('cmds.quit.is_registered'),
            patch('config.owner', new=[]),
            patch('config.channels', new=[]),
        ) as (is_registered, owner, chan):
            chan.extend(['#foo', '#bar'])

            is_registered.return_value = None
            self.assertEqual(quit(s, {'arguments': '!quit', 'sender': 'foobaz'}),
                'An unexpected error occurred while fetching data!')

            is_registered.return_value = False
            owner.extend(['foo'])
            self.assertEqual(quit(s, {'arguments': '!quit', 'sender': 'foobaz'}),
                'This command can be run only by the owners!')

            is_registered.return_value = True
            self.assertEqual(quit(s, {'arguments': '!quit', 'sender': 'foobaz'}),
                'This command can be run only by the owners!')

            self.assertEqual(quit(s, {'arguments': '!quit baz qux',
                'sender': 'foo'}), 'Invalid channel names!')

            self.assertListEqual(quit(s, {'arguments': '!quit #foo #foobar',
                'sender': 'foo', 'action_args': ['#foo']}),
                ['PART', '#foo', '\r\nPRIVMSG #foo :Left: #foo'])

            self.assertListEqual(quit(s,
                {'arguments': '!quit', 'sender': 'foo'}), ['PART', '#bar'])

            self.assertListEqual([], chan)

    def test_so(self):
        from cmds.so import so
        import urllib2
        socket = Mock()

        self.assertEqual(so(socket, {'arguments': '!so'}),
            'Usage: !so <search term>')
        self.assertEqual(so(socket, {'arguments': '!so  '}),
            'Usage: !so <search term>')

        with patch('stackexchange.Site') as s:
            api = Mock()
            api.search.side_effect = urllib2.HTTPError(code=42, fp=file,
                    url='http://foo', msg='FooError', hdrs='headers')

            s.return_value = api

            self.assertEqual(so(socket, {'arguments': '!so foo'}),
                "The server couldn't fulfill the request!" + \
                        "\r\nReason: FooError\r\nCode: 42")

            api.search.side_effect = None
            api.search.return_value = []
            self.assertEqual(so(socket, {'arguments': '!so foo'}), 'Not found: foo')

            result = Mock()
            result.title = 'foo_title'
            result.url = 'foo_url'
            api.search.return_value = [result]
            self.assertEqual(so(socket, {'arguments': '!so foo'}),
                'foo_title\r\nfoo_url')

    def test_uptime(self):
        from cmds.uptime import uptime
        from datetime import timedelta
        s = Mock()

        self.assertEqual(uptime(s, {'arguments': '!uptime garbage'}), '')

        with nested(
            patch('time.time'),
            patch('config.start_time', new=0),
        ) as (time, start_time):
            time.return_value = 42

            self.assertEqual(uptime(s, {'arguments': '!uptime'}), 'Uptime: ' + \
                str(timedelta(seconds=time.return_value-start_time)))

    def test_twitter(self):
        from cmds.twitter import twitter
        s = Mock()

        with patch('cmds.twitter.getStatus') as status:
            status.return_value = {'date': '42', 'text': 'foobar'}

            self.assertEqual(twitter(s, {'arguments': '!twitter',
                'sender': 'foo'}),
                "foo's latest tweet was made on: 42\r\nfoobar")

            self.assertEqual(twitter(s, {'arguments': '!twitter !twitter ',
                'sender': 'foo'}),
                'Usage: !twitter <screen name>')

            self.assertEqual(twitter(s, {'arguments': '!twitter baz',
                'sender': 'foo'}),
                "baz's latest tweet was made on: 42\r\nfoobar")

            status.return_value = 'FooError'
            self.assertEqual(twitter(s, {'arguments': '!twitter baz',
                'sender': 'foo'}), 'FooError')

    def test_twitter_getStatus(self):
        from cmds.twitter import getStatus

        url = 'http://foo.bar'

        with nested(
            patch('urllib.urlopen'),
            patch('cmds.twitter.BeautifulStoneSoup')
        ) as (urlopen, BeautifulStoneSoup):
            urlopen.side_effect = Exception()
            self.assertEqual(getStatus(url), 'Error getting the status!')

            BeautifulStoneSoup.return_value.find.return_value = None

            urlopen.side_effect = None
            self.assertEqual(getStatus(url), "This user doesn't exist!")

            xmlStatus = Mock()
            xmlStatus.find.return_value = None
            BeautifulStoneSoup.return_value.find.return_value = xmlStatus
            self.assertEqual(getStatus(url), 'This user has no tweets!')

            content = Mock()
            content.find.return_value.contents = ['Wed Jan 26 15:16:34 +0000 2011']
            xmlStatus.find.return_value = content
            BeautifulStoneSoup.return_value.find.return_value = xmlStatus
            self.assertDictEqual(getStatus(url), {'date': '26/01/2011 15:34',
                'text': 'Wed Jan 26 15:16:34 +0000 2011'})

            content.find.return_value.contents = ['Wed Jan 26 15:16:34 -0000 2011']
            xmlStatus.find.return_value = content
            BeautifulStoneSoup.return_value.find.return_value = xmlStatus
            self.assertDictEqual(getStatus(url), {'date': '26/01/2011 15:34',
                'text': 'Wed Jan 26 15:16:34 -0000 2011'})

    def test_weather(self):
        from cmds.weather import weather
        s = Mock()

        conditions = {
            'location': 'foobar',
            'temp': '42',
            'weather': 'baz',
        }

        self.assertEqual(weather(s, {'arguments': '!weather'}),
            'Usage: !weather <city>, <state>')

        self.assertEqual(weather(s, {'arguments': '!weather  '}),
            'Usage: !weather <city>, <state>')

        with patch('cmds.weather.get_weather') as get_weather:
            get_weather.return_value = 'Inexistent location: foo'

            self.assertEqual(weather(s, {'arguments': '!weather foo'}),
                'Inexistent location: foo')

            get_weather.return_value = conditions
            self.assertEqual(weather(s, {'arguments': '!weather foo'}),
                conditions['location'] + ' - ' + conditions['temp'] + ' - ' + \
                conditions['weather'] + ' - Provided by: ' + \
                'Weather Underground, Inc.')

    def test_weather_get_weather(self):
        from cmds.weather import get_weather

        location = 'foobar'

        with nested(
            patch('urllib.urlopen'),
            patch('cmds.weather.BeautifulStoneSoup')
        ) as (urlopen, BeautifulStoneSoup):
            urlopen.side_effect = Exception()

            self.assertEqual(get_weather(location), 'Could not open the page!')

            urlopen.side_effect = None
            BeautifulStoneSoup.return_value.find.return_value.contents = [
                ','
            ]

            self.assertEqual(get_weather(location), 'Inexistent location: ' + \
                location)

            BeautifulStoneSoup.return_value.find.return_value.contents = [
                'foo bar baz'
            ]

            self.assertDictEqual(get_weather(location), {
                'weather': 'foo bar baz',
                'location': 'foo bar baz',
                'temp': u'foo\xb0 bar\xb0 baz',
            })

    def test_wiki(self):
        from cmds.wiki import wiki
        s = Mock()

        with patch('cmds.wiki.get_para') as get_para:
            get_para.return_value = 'foobar'

            self.assertEqual(wiki(s, {'arguments': '!wiki'}),
                'http://en.wikipedia.org/wiki/Main_Page\r\nfoobar')

            self.assertEqual(wiki(s, {'arguments': '!wiki      '}),
                'http://en.wikipedia.org/wiki/Main_Page\r\nfoobar')

            self.assertEqual(wiki(s, {'arguments': '!wiki foobar'}),
                'http://en.wikipedia.org/wiki/foobar\r\nfoobar')

    def test_wiki_get_para(self):
        from cmds.wiki import get_para

        search_term = 'foobar'

        with nested(
            patch('urllib2.Request'),
            patch('urllib2.urlopen'),
            patch('cmds.wiki.BeautifulSoup')
        ) as (request, urlopen, BeautifulSoup):
            request.side_effect = IOError()
            self.assertEqual(get_para(search_term), 'Cannot acces link!')

            request.side_effect = None
            paragraph = Mock()
            paragraph.findAll.return_value = ['foobar']
            BeautifulSoup.return_value.find.return_value.p = paragraph

            self.assertEqual(get_para(search_term), 'foobar')

            paragraph.findAll.return_value = ['foobar', '.'*462]
            BeautifulSoup.return_value.find.return_value.p = paragraph
            self.assertEqual(get_para(search_term), 'foobar' + '.'*454)

            paragraph.findAll.return_value = ['foobar', ' '*460]
            BeautifulSoup.return_value.find.return_value.p = paragraph
            self.assertEqual(get_para(search_term), 'foobar' + ' '*454)

suite = unittest.TestLoader().loadTestsFromTestCase(CmdsTests)

if __name__ == '__main__':
    unittest.main()
