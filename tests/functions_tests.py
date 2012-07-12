import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../src/')))

import unittest
from mock import patch, MagicMock, Mock, call
from StringIO import StringIO
from contextlib import nested

class FunctionsTests(unittest.TestCase):
    def test_get_sender(self):
        from functions import get_sender

        self.assertEqual(get_sender(':foo!foo@bar.baz PRIVMSG #channel :msg'),
            'foo')

    def test_log_write(self):
        from functions import log_write
        import err

        with nested(
            patch('functions.open', create=True),
            patch('sys.stdout', new=StringIO()),
        ) as (o, stdout):
            o.return_value = MagicMock(spec=file)
            fh = o.return_value.__enter__.return_value

            log_write('foo_file', 'pre', 'sep', 'post')

            fh.write.assert_called_with('preseppost')

            fh.write.side_effect = Exception()

            log_write('foo_file', 'pre', 'sep', 'post')

            self.assertEqual(stdout.getvalue(), err.LOG_FAILURE + '\n\n')

    def test_get_datetime(self):
        from functions import get_datetime

        with patch('datetime.datetime') as datetime:
            datetime.now.return_value.strftime.return_value = 'foo'

            self.assertDictEqual(get_datetime(), {'date': 'foo', 'time': 'foo'})

    def test_check_cfg(self):
        from functions import check_cfg

        self.assertTrue(check_cfg())
        self.assertTrue(check_cfg(['']))
        self.assertTrue(check_cfg([''], {'foo': 'bar'}))

        self.assertFalse(check_cfg([]))
        self.assertFalse(check_cfg([''], {}))

    def test_check_channel(self):
        from functions import check_channel

        self.assertTrue(check_channel(['#foo', '#bar']))
        self.assertTrue(check_channel([]))

        self.assertFalse(check_channel(['foo', '#bar']))
        self.assertFalse(check_channel(['#bar  ', 'foo']))

    def test_get_nick(self):
        from functions import get_nick

        with patch('config.nicks', new=[]) as nicks:
            nick = get_nick(nicks)

            self.assertRaises(StopIteration, nick.next)

            nicks.extend(['foo', 'bar'])
            nick = get_nick(nicks)

            self.assertEqual(nick.next(), 'foo')
            self.assertEqual(nick.next(), 'bar')
            self.assertRaises(StopIteration, nick.next)

    def test_sigint_handler(self):
        from functions import sigint_handler

        g = {'irc': Mock()}
        def getitem(name):
            return g[name]

        with nested(
            patch('sys.stdout', new=StringIO()),
            patch('functions.get_datetime'),
            patch('functions.log_write'),
        ) as (stdout, get_dt, log_write):
            get_dt.return_value = {'date': '42', 'time': '42'}


            frame = Mock()
            frame.f_globals = MagicMock(spec_set=dict)
            frame.f_globals.keys.return_value = 'irc'
            frame.f_globals.__getitem__.side_effect = getitem

            sigint_handler(42, frame)

            self.assertEqual(stdout.getvalue(),
                '\nClosing: CTRL-c pressed!\n')

            frame.f_globals.__getitem__.side_effect = Exception()
            sigint_handler(42, frame)
            self.assertEqual(stdout.getvalue(),
                '\nClosing: CTRL-c pressed!\n'*2)

            frame.f_globals.keys.return_value = 'foo'
            sigint_handler(42, frame)
            self.assertEqual(stdout.getvalue(),
                '\nClosing: CTRL-c pressed!\n'*3)


    def test_send_to(self):
        from functions import send_to

        with nested(
            patch('config.current_nick', new='foo'),
            patch('functions.get_sender'),
        ) as (nick, get_sender):
            get_sender.return_value = 'baz'

            self.assertEqual(send_to('PRIVMSG ' + nick + ' :'), 'PRIVMSG baz :')
            self.assertEqual(send_to('PRIVMSG #chan :msg'), 'PRIVMSG #chan :')

    def test_is_registered(self):
        from functions import is_registered

        checked_nick = 'foobaz'
        s = Mock()

        s.send = Mock()
        s.recv.return_value = 'NickServ Last seen  : now'

        self.assertTrue(is_registered(s, checked_nick))

        s.recv.return_value = 'NickServ'
        self.assertFalse(is_registered(s, checked_nick))

        response = ['baz', 'NickServ Information on:', 'NickServ', 'foo']
        # side_effect will return the next item from the list which will be
        # assigned to is_registered.receive this way I'm able to test the
        # pass branch in the function
        s.recv.side_effect = response

        self.assertFalse(is_registered(s, checked_nick))

    def test_create_socket(self):
        from functions import create_socket
        import err

        with nested(
            patch('socket.socket'),
            patch('functions.log_write'),
            patch('sys.stdout', new=StringIO()),
            patch('functions.get_datetime'),
        ) as (socket, log_write, stdout, get_dt):
            socket.side_effect = IOError()
            get_dt.return_value = {'date': '42', 'time': '42'}

            self.assertIsNone(create_socket('foo'))
            self.assertEqual(stdout.getvalue(), err.NO_SOCKET + '\n\n')
            log_write.assert_called_with('foo', '42', ' <> ',
                err.NO_SOCKET + '\n\n')

            socket.side_effect = None
            socket.return_value = 42
            self.assertEqual(create_socket('foo'), 42)

    def test_connect_to(self):
        from functions import connect_to

        with nested(
            patch('functions.log_write'),
            patch('sys.stdout', new=StringIO()),
            patch('functions.get_datetime'),
        ) as (log_write, stdout, get_dt):
            get_dt.return_value = {'date': '42', 'time': '42'}

            s = Mock()
            s.connect.side_effect = IOError()

            address = ('server', 'port')
            message = 'Could not connect to {0}\n{1}'.format(address, '\n')

            self.assertFalse(connect_to(address, s, 'foo'))
            self.assertEqual(stdout.getvalue(), message)
            log_write.assert_called_with('foo', '42', ' <> ', message)

            s.connect.side_effect = None
            s.connect = Mock()
            self.assertTrue(connect_to(address, s, 'foo'))

            s.connect.assert_called_with(address)

    def test_join_channels(self):
        from functions import join_channels

        with nested(
            patch('functions.log_write'),
            patch('sys.stdout', new=StringIO()),
            patch('functions.get_datetime'),
        ) as (log_write, stdout, get_dt):
            get_dt.return_value = {'date': '42', 'time': '42'}

            s = Mock()
            s.send.side_effect = IOError()

            channels = ['#foo', '#bar']
            clist = ','.join(channels)

            message = 'Unexpected error while joining {0}: {1}'.format(
                clist, '\n')

            self.assertFalse(join_channels(channels, s, 'foo'))
            self.assertEqual(stdout.getvalue(), message)

            log_write.assert_called_with('foo', '42', ' <> ', message)


            log_write.call_args_list = []
            s.send.side_effect = None
            s.send = Mock()
            msg = 'Joined: {0}\n'.format(clist)

            self.assertTrue(join_channels(channels, s, 'foo'))

            log_write.assert_called_with('foo', '42', ' <> ', msg)
            self.assertEqual(stdout.getvalue(), message + msg)

            s.send.assert_called_with('JOIN ' + clist + '\r\n')

    def test_quit_bot(self):
        from functions import quit_bot

        with nested(
            patch('functions.log_write'),
            patch('sys.stdout', new=StringIO()),
            patch('functions.get_datetime'),
        ) as (log_write, stdout, get_dt):
            get_dt.return_value = {'date': '42', 'time': '42'}

            s = Mock()
            s.send.side_effect = IOError()

            message = 'Unexpected error while quitting: \n'

            self.assertFalse(quit_bot(s, 'foo'))
            self.assertEqual(stdout.getvalue(), message)

            log_write.assert_called_with('foo', '42', ' <> ', message)


            s.send.side_effect = None
            s.send = Mock()

            self.assertTrue(quit_bot(s, 'foo'))

            log_write.assert_called_with('foo', '42', ' <> ', 'QUIT\r\n')
            s.send.assert_called_with('QUIT\r\n')

    def test_run_cmd(self):
        from functions import run_cmd
        import err

        cmds_list = ['foo', 'bar']
        args = {'sender': 'foobar', 'action': 'qux'}
        s = Mock()

        with nested(
            patch('functions.__import__', create=True),
            patch('functions.getattr', create=True),
        ) as (import_mock, getattr_mock):
            foo = Mock()
            foo.return_value = 'response'

            getattr_mock.return_value = foo

            self.assertEqual(run_cmd(s, 'foo', args, cmds_list), 'response')
            self.assertIsNone(run_cmd(s, 'baz', args, cmds_list))

            import_mock.side_effect = ImportError()
            self.assertEqual(run_cmd(s, 'foo', args, cmds_list),
                err.C_INEXISTENT.format('foo'))

            getattr_mock.side_effect = AttributeError()
            import_mock.side_effect = None

            self.assertEqual(run_cmd(s, 'foo', args, cmds_list),
                err.C_INVALID.format('foo'))

    def test_send_response(self):
        from functions import send_response

        self.assertIsNone(send_response('', 'nick', 'bar', 'baz'))
        self.assertIsNone(send_response([], '#chan', 'bar', 'baz'))
        self.assertIsNone(send_response(None, '#chan', 'bar', 'baz'))

        with nested(
            patch('functions.log_write'),
            patch('functions.get_datetime'),
        ) as (log_write, get_dt):
            get_dt.return_value = {'date': '42', 'time': '42'}

            response = ['foo', 'bar']
            s = Mock()
            self.assertTrue(send_response(response, '#chan', s, 'foo'))
            s.send.assert_called_with(' '.join(response) + '\r\n')
            log_write.assert_called_with('foo', '42', ' <> ',
                ' '.join(response) + '\r\n')

            self.assertTrue(send_response('baz', '#chan', s, 'foo'))
            s.send.assert_called_with('#chanbaz\r\n')
            log_write.assert_called_with('foo', '42', ' <> ', '#chanbaz\r\n')

            self.assertTrue(send_response('baz\r\n', '#chan', s, 'foo'))
            s.send.assert_called_with('#chanbaz\r\n')
            log_write.assert_called_with('foo', '42', ' <> ', '#chanbaz\r\n')

            self.assertTrue(send_response('foo\r\nbaz\r\n', '#chan', s, 'foo'))
            s.send.assert_called_with('#chanfoo\r\n#chanbaz\r\n')
            log_write.assert_called_with('foo', '42', ' <> ',
                '#chanfoo\r\n#chanbaz\r\n')

            self.assertTrue(send_response('foo\r\nbaz\r\nquo\r\nfoobar',
                '#chan', s, 'foo'))
            s.send.assert_called_with(
                '#chanfoo\r\n#chanbaz\r\n#chanquo\r\n#chanfoobar\r\n')
            log_write.assert_called_with('foo', '42', ' <> ',
                '#chanfoo\r\n#chanbaz\r\n#chanquo\r\n#chanfoobar\r\n')

            s.send.side_effect = IOError()
            self.assertFalse(send_response('baz', '#chan', s, 'foo'))
            log_write.assert_called_with('foo', '42', ' <> ',
                'Unexpected error while sending the response: \n')


    def test_name_bot(self):
        from functions import name_bot

        logfile = 'foo'
        irc = Mock()
        irc.send = Mock()

        nicks = ['nick1', 'nick2']

        with nested(
            patch('functions.get_nick'),
            patch('functions.log_write'),
            patch('functions.get_datetime'),
            patch('config.real_name', new='foo'),
            patch('random.sample'),
        ) as (get_nick, log_write, get_dt, real_name, sample):
            get_dt.return_value = {'date': '42', 'time': '42'}
            get_nick.return_value = iter(nicks)
            sample.return_value = 'baz'

            irc.recv.side_effect = [
                'foo',
                'Nickname is already in use',
                nicks[1],
            ]

            self.assertEqual(name_bot(irc, nicks, real_name, logfile), nicks[1])
            expected_log_write_calls = [
                call(logfile, '42', ' <> ',
                    'Set nick to: {0}\n'.format(nicks[0])),
                call(logfile, '42', ' <> ',
                    'Changing nick to: {0}\n'.format(nicks[1])),
            ]

            expected_send_calls = [
                call('NICK ' + nicks[0] + '\r\n'),
                call('USER {0} {0} {0} :{1}\r\n'.format(nicks[0], real_name)),
                call('NICK ' + nicks[1] + '\r\n'),
            ]

            self.assertListEqual(expected_log_write_calls,
                log_write.call_args_list)

            self.assertListEqual(expected_send_calls, irc.send.call_args_list)

            nicks = ['used_nick']
            get_nick.return_value = iter(nicks)
            irc.recv.side_effect = ['Nickname is already in use', 'motd']

            self.assertEqual(name_bot(irc, nicks, real_name, logfile), nicks[0] + 'baz')
            expected_log_write_calls = [
                call(logfile, '42', ' <> ',
                    'Set nick to: {0}\n'.format(nicks[0])),
                call(logfile, '42', ' <> ',
                    'Changing nick to: {0}\n'.format(nicks[0] + 'baz')),
            ]

            expected_send_calls = [
                call('NICK ' + nicks[0] + '\r\n'),
                call('USER {0} {0} {0} :{1}\r\n'.format(nicks[0], real_name)),
                call('NICK ' + nicks[0] + 'baz\r\n'),
            ]

suite = unittest.TestLoader().loadTestsFromTestCase(FunctionsTests)

if __name__ == '__main__':
    unittest.main()
