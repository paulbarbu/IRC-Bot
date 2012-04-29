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

            self.assertEqual(stdout.getvalue(), err.LOG_FAILURE + '\n')

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
            nick = get_nick()

            self.assertRaises(StopIteration, nick.next)

            nicks.extend(['foo', 'bar'])
            nick = get_nick()

            self.assertEqual(nick.next(), 'foo')
            self.assertEqual(nick.next(), 'bar')
            self.assertRaises(StopIteration, nick.next)

    def test_sigint_handler(self):
        from functions import sigint_handler

        with nested(
            patch('sys.stdout', new=StringIO()),
            patch('functions.get_datetime'),
            patch('functions.log_write'),
        ) as (stdout, get_dt, log_write):
            get_dt.return_value = {'date': '42', 'time': '42'}

            sigint_handler(42, Mock())

            self.assertEqual(stdout.getvalue(),
                '\nClosing: CTRL-c pressed!\n')

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
        import err

        checked_nick = 'foobaz'

        with nested(
            patch('functions.get_datetime'),
            patch('config.log', new='log_path'),
            patch('socket.socket'),
            patch('functions.log_write'),
            patch('config.server', new='server'),
            patch('config.port', new=42),
            patch('random.sample'),
            patch('config.current_nick', new='baz'),
            patch('config.realName', new='bar'),
        ) as (get_dt, log, socket, log_write, server, port, sample, nick,
        real_name):
            get_dt.return_value = {'date': '42', 'time': '42'}
            sample.return_value = 'foo'
            socket.side_effect = Exception()

            sampled_nick = nick + sample.return_value

            self.assertIsNone(is_registered(checked_nick))
            log_write.assert_called_with(log + '42.log', '42', ' <miniclient> ',
                err.NO_SOCKET + '\n')

            socket.side_effect = None
            socket.return_value.connect.side_effect = IOError()
            socket.return_value.close = Mock()

            self.assertIsNone(is_registered(checked_nick))
            socket.return_value.close.assert_called_once_with()
            log_write.assert_called_with(log + '42.log', '42', ' <miniclient> ',
                    'Could not connect to {0}:{1}\n'.format(server, port))

            socket.return_value.connect.side_effect = None
            socket.return_value.send = Mock()
            socket.return_value.recv.return_value = 'NickServ Last seen  : now'

            self.assertTrue(is_registered(checked_nick))

            expected_calls = [
                call('NICK {0}\r\n'.format(sampled_nick)),
                call('USER {0} {0} {0} :{1}\r\n'.format(sampled_nick,
                    real_name + sample.return_value)),
                call('PRIVMSG nickserv :info ' + checked_nick + '\r\n'),
            ]

            self.assertListEqual(expected_calls,
                socket.return_value.send.call_args_list)

            socket.return_value.recv.return_value = 'NickServ'
            self.assertFalse(is_registered(checked_nick))

            response = ['NickServ Information on:', 'NickServ', 'foo']
            # side_effect will call next() internally on the generator object
            # returned by iter() and so the next item will be assigned to
            # is_registered.receive this way I'm able to test the pass branch
            # in the function
            socket.return_value.recv.side_effect = iter(response)

            self.assertFalse(is_registered(checked_nick))

if __name__ == '__main__':
    unittest.main()
