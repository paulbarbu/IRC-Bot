import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../src')))

import unittest
from mock import patch, Mock, call
from contextlib import nested
from StringIO import StringIO

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

    def test_main(self):
        from ircbot import main

        with nested(
            patch('ircbot.check_cfg'),
            patch('ircbot.check_channel'),
            patch('ircbot.create_socket'),
            patch('ircbot.get_datetime'),
            patch('config.owner', new='owner'),
            patch('config.server', new='server'),
            patch('config.nicks', new=['foo', 'bar']),
            patch('config.real_name', new='real name'),
            patch('config.log', new='log_foo'),
            patch('config.cmds_list', new=['baz', 'bar']),
            patch('config.port', new=42),
            patch('signal.signal'),
            patch('ircbot.sigint_handler'),
            patch('config.channels', new=['#chan1', '#chan2']),
            patch('ircbot.connect_to'),
            patch('ircbot.log_write'),
            patch('config.current_nick', new='nick'),
            patch('ircbot.name_bot'),
            patch('ircbot.join_channels'),
            patch('ircbot.run'),
            patch('ircbot.quit_bot'),
            patch('sys.stdout', new=StringIO()),
        ) as (check_cfg, check_channel, create_socket, get_dt,
        owner, server, nicks, real_name, log, cmds_list, port, signal,
        sigint_handler, channels, connect_to, log_write, current_nick,
        name_bot, join_channels, run, quit_bot, stdout):
            s= Mock()
            get_dt.return_value = {'date': '42', 'time': '42'}
            logfile = log + get_dt.return_value['date'] + '.log'
            check_cfg.return_value = False

            self.assertRaises(SystemExit, main)

            check_cfg.return_value = True
            check_channel.return_value = False
            self.assertRaises(SystemExit, main)

            check_channel.return_value = True
            create_socket.return_value = False
            connect_to.return_value = False
            self.assertIsNone(main())

            create_socket.return_value = True
            connect_to.return_value = False
            self.assertIsNone(main())

            create_socket.return_value = False
            connect_to.return_value = True
            self.assertIsNone(main())

            create_socket.return_value = s
            connect_to.return_value = True

            main()

            connect_msg = 'Connected to {0}:{1}\n'.format(server, port)
            disconnect_msg = 'Disconnected from {0}:{1}\n'.format(server, port)

            expected_log_write_calls = [
                call(logfile, '42', ' <> ',
                    connect_msg),
                call(logfile, '42', ' <> ',
                    disconnect_msg),
            ]

            self.assertListEqual(expected_log_write_calls,
                log_write.call_args_list)

            self.assertEqual(stdout.getvalue(), connect_msg + disconnect_msg)
            s.close.assert_called_with()
            name_bot.assert_called_with(s, nicks, real_name, logfile)
            join_channels.assert_called_with(channels, s, logfile)
            run.assert_called_with(s, channels, cmds_list, name_bot(), logfile)

            join_channels.return_value = False
            log_write.call_args_list = []
            main()

            connect_msg = 'Connected to {0}:{1}\n'.format(server, port)
            disconnect_msg = 'Disconnected from {0}:{1}\n'.format(server, port)

            expected_log_write_calls = [
                call(logfile, '42', ' <> ',
                    connect_msg),
                call(logfile, '42', ' <> ',
                    disconnect_msg),
            ]

            self.assertListEqual(expected_log_write_calls,
                log_write.call_args_list)

            self.assertEqual(stdout.getvalue(), (connect_msg + disconnect_msg)*2)
            s.close.assert_called_with()
            name_bot.assert_called_with(s, nicks, real_name, logfile)
            join_channels.assert_called_with(channels, s, logfile)

suite = unittest.TestLoader().loadTestsFromTestCase(IrcBotTests)

if __name__ == '__main__':
    unittest.main()
