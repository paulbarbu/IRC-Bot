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

        self.assertEqual(about({'arguments': '!about garbage'}), '')
        self.assertEqual(about({'arguments': '!about'}),
            'Author: Paullik @ http://github.com/paullik')

    def test_answer(self):
        from cmds.answer import answer

        self.assertEqual(answer({'arguments': '!answer garbage'}), '')
        self.assertEqual(answer({'arguments': '!answer'}),
            'The Answer to the Ultimate Question of Life, the Universe, and Everything is 42!')

    def test_channels(self):
        from cmds.channels import channels

        self.assertEqual(channels({'arguments': '!channels garbage'}), '')

        with nested(
            patch('cmds.channels.is_registered', create=True),
            patch('config.owner', new=[], create=True),
            patch('config.channels', new=[], create=True),
            patch('config.current_nick', new='test', create=True),
        ) as (is_registered, owner, chan, nick):

            chan.append('#foobar')
            owner.append('foo')

            is_registered.return_value = False
            self.assertEqual(channels({'arguments': '!channels',
                'sender': 'baz'}), 'This command can be run only by the owners!')

            is_registered.return_value = True
            self.assertEqual(channels({'arguments': '!channels',
                'sender': 'baz'}), 'This command can be run only by the owners!')

            is_registered.return_value = False
            self.assertEqual(channels({'arguments': '!channels',
                'sender': 'baz'}), 'This command can be run only by the owners!')

            is_registered.return_value = True
            owner.append('baz')
            self.assertEqual(channels({'arguments': '!channels',
                'sender': 'baz'}), 'test is connected to: #foobar')

    def test_google(self):
        from cmds.google import google

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

        self.assertEqual(google({'arguments': '!google'}),
            'Usage: !google <search term>')

        self.assertEqual(google({'arguments': '!google   '}),
            'Usage: !google <search term>')

        with patch('cmds.google.build', create=True) as build:
            query_result = MagicMock(spec_set=dict)
            query_result.__setitem__.side_effect = setitem
            query_result.__getitem__.side_effect = getitem

            service_mock = Mock()
            service_mock.cse.return_value.list.return_value.execute.return_value = query_result

            build.return_value = service_mock

            self.assertEqual(google({'arguments': '!google foo bar'}),
                'Not found: foo bar')

            result['queries']['request'][0]['totalResults'] = 42
            self.assertEqual(google({'arguments': '!google foo bar'}),
                'http://foobar.baz\r\nDetails about foobar')

    def test_help(self):
        from cmds.help import help

        self.assertEqual(help({'arguments': '!help garbage'}), '')

        with patch('config.cmds_list', new=[], create=True) as config:
            config.extend(['foo', 'bar'])

            self.assertEqual(help({'arguments': '!help'}),
                '2 available commands: foo bar ') #notice the space

    def test_join(self):
        from cmds.join import join

        self.assertEqual(join({'arguments': '!join', 'sender': 'foo'}),
            'Usage: !join <#channel >+')

        with nested(
            patch('cmds.join.is_registered', create=True),
            patch('config.owner', new=[], create=True),
            patch('config.channels', new=[], create=True),
        ) as (is_registered, owner, chan):

            is_registered.return_value = False
            owner.extend(['baz', 'bar'])
            self.assertEqual(join({'arguments': '!join #chan', 'sender': 'foo'}),
                'This command can be run only by the owners!')

            is_registered.return_value = True
            self.assertEqual(join({'arguments': '!join #chan', 'sender': 'foo'}),
                'This command can be run only by the owners!')

            is_registered.return_value = False
            owner.append('foo')
            self.assertEqual(join({'arguments': '!join #chan', 'sender': 'foo'}),
                'This command can be run only by the owners!')

            is_registered.return_value = True
            self.assertListEqual(join({'arguments': '!join #chan',
                'sender': 'foo'}), ['JOIN ', '#chan'])

            self.assertEqual(join({'arguments': '!join chan chan2',
                'sender': 'foo'}),
                'Invalid channels names, usage: !join <#channel >+')

            self.assertListEqual(join({'arguments': '!join #chan #c',
                'sender': 'foo'}), ['JOIN ', '#c'])

            self.assertListEqual(join({'arguments': '!join foobar   #test',
                'sender': 'foo'}), ['JOIN ', '#test'])

            self.assertEqual(join({'arguments': '!join    ',
                'sender': 'foo'}),
                'Invalid channels names, usage: !join <#channel >+')

            self.assertListEqual(['#chan', '#c', '#test'], chan)

    def test_mball(self):
        from cmds.mball import mball

        self.assertEqual(mball({'arguments': '!mball garbage'}), '')

        self.assertRegexpMatches(mball({'arguments': '!mball'}),
            'Magic Ball says: *')

    def test_quit(self):
        from cmds.quit import quit

        with nested(
            patch('cmds.quit.is_registered', create=True),
            patch('config.owner', new=[], create=True),
            patch('config.channels', new=[], create=True),
        ) as (is_registered, owner, chan):
            chan.extend(['#foo', '#bar'])

            is_registered.return_value = None
            self.assertEqual(quit({'arguments': '!quit', 'sender': 'foobaz'}),
                'An unexpected error occurred while fetching data!')

            is_registered.return_value = False
            owner.extend(['foo'])
            self.assertEqual(quit({'arguments': '!quit', 'sender': 'foobaz'}),
                'This command can be run only by the owners!')

            is_registered.return_value = True
            self.assertEqual(quit({'arguments': '!quit', 'sender': 'foobaz'}),
                'This command can be run only by the owners!')

            self.assertEqual(quit({'arguments': '!quit baz qux',
                'sender': 'foo'}), 'Invalid channel names!')

            self.assertListEqual(quit({'arguments': '!quit #foo #foobar',
                'sender': 'foo'}), ['PART', '#foo'])

            self.assertListEqual(quit({'arguments': '!quit', 'sender': 'foo'}),
                ['PART', '#bar'])

            #self.assertListEqual([], chan)

    def test_so(self):
        from cmds.so import so
        import urllib2

        self.assertEqual(so({'arguments': '!so'}), 'Usage: !so <search term>')
        self.assertEqual(so({'arguments': '!so  '}), 'Usage: !so <search term>')

        with patch('stackexchange.Site', create=True) as s:
            api = Mock()
            api.search.side_effect = urllib2.HTTPError(code=42, fp=file,
                    url='http://foo', msg='FooError', hdrs='headers')

            s.return_value = api

            self.assertEqual(so({'arguments': '!so foo'}),
                "The server couldn't fulfill the request!" + \
                        "\r\nReason: FooError\r\nCode: 42")

            api.search.side_effect = None
            api.search.return_value = []
            self.assertEqual(so({'arguments': '!so foo'}), 'Not found: foo')

            result = Mock()
            result.title = 'foo_title'
            result.url = 'foo_url'
            api.search.return_value = [result]
            self.assertEqual(so({'arguments': '!so foo'}),
                'foo_title\r\nfoo_url')

    def test_uptime(self):
        from cmds.uptime import uptime
        from datetime import timedelta

        self.assertEqual(uptime({'arguments': '!uptime garbage'}), '')

        with nested(
            patch('time.time', create=True),
            patch('config.start_time', new=0, create=True),
        ) as (time, start_time):
            time.return_value = 42

            self.assertEqual(uptime({'arguments': '!uptime'}), 'Uptime: ' + \
                str(timedelta(seconds=time.return_value-start_time)))

if __name__ == '__main__':
    unittest.main()
