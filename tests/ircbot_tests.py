import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../src')))

import unittest
from mock import patch, Mock, call
from contextlib import nested

class IrcBotTests(unittest.TestCase):
    def test_run(self):
        from ircbot import run

        cmds = ['foo', 'bar']
        nick = 'foo_nick'

        self.assertIsNone(run('foo_socket', [], cmds, nick, 'qux'))

        with nested(
            patch('ircbot.get_datetime'),
            patch('ircbot.log_write'),
            patch('parser.parse_command'),
            patch('ircbot.send_response'),
            patch('ircbot.send_to'),
            patch('ircbot.run_cmd'),
        ) as (get_dt, log_write, parse_command, send_response, send_to, run_cmd):
            get_dt.return_value = {'date': '42', 'time': '42'}

            channels = ['#chan1', '#chan2']
            s = Mock()
            s.recv.side_effect = ['', 'foo', 'foo\n', 'foo\n', 'foo\n', 'foo\n']

            parse_command.side_effect = [
                {'action': 'foo'},
                {'action': 'PING', 'arguments': 'server'},
                {'action': 'KICK', 'action_args': ['#chan1', nick]},
                {'action': 'KICK', 'action_args': ['#chan2', nick]},
            ]
            run(s, channels, cmds, nick, 'qux')

            expected_send_response_calls = [
                call('', send_to(), s, 'qux'),
                call(['PONG', ':server'], send_to(), s, 'qux'),
                call('', send_to(), s, 'qux'),
                call('', send_to(), s, 'qux'),
            ]

            self.assertListEqual(channels, [])
            self.assertListEqual(expected_send_response_calls,
                send_response.call_args_list)

            send_response.call_args_list = []
            channels = ['#chan1', '#chan2']
            s = Mock()
            s.recv.side_effect = ['', 'foo', 'foo\n', 'foo\n', 'foo\n', 'foo\n']
            run_cmd.return_value = 'retval'

            parse_command.side_effect = [
                {'action': 'PRIVMSG', 'arguments': '!cmd'},
                {'action': 'PRIVMSG', 'arguments': 'cmd'},
                {'action': 'PRIVMSG', 'arguments': '!cmd '},
                {'action': 'QUIT', 'arguments': 'Ping timeout: '},
            ]
            run(s, channels, cmds, nick, 'qux')

            expected_send_response_calls = [
                call('retval', send_to(), s, 'qux'),
                call('', send_to(), s, 'qux'),
                call('retval', send_to(), s, 'qux'),
                call('', send_to(), s, 'qux'),
            ]

            self.assertListEqual(channels, [])
            self.assertListEqual(expected_send_response_calls,
                send_response.call_args_list)

suite = unittest.TestLoader().loadTestsFromTestCase(IrcBotTests)

if __name__ == '__main__':
    unittest.main()
