import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../src')))

import unittest
from mock import patch

class ParserTests(unittest.TestCase):
    def test_parse_command(self):
        from parser import parse_command

        sender = 'foo'
        host = '@host.bar'

        user_command = ':{nick}!~{host} {action} {args}'
        server_command = '{action} {args}'

        with patch('parser.get_sender') as get_sender:
            get_sender.return_value = sender

            self.assertDictEqual(parse_command(user_command.format(nick=sender,
                host=sender + host, action='JOIN', args='#chan')),
                {'sender': sender, 'action': 'JOIN', 'arguments': '',
                'action_args': ['#chan']})

            self.assertDictEqual(parse_command(user_command.format(nick=sender,
                host=sender + host, action='KICK', args='#chan user :reason')),
                {'sender': sender, 'action': 'KICK', 'arguments': 'reason',
                'action_args': ['#chan', 'user']})

            self.assertDictEqual(parse_command(user_command.format(nick=sender,
                host=sender + host, action='QUIT', args=':reason')),
                {'sender': sender, 'action': 'QUIT', 'arguments': 'reason',
                'action_args': []})

            self.assertDictEqual(parse_command(server_command.format(
                action='PING', args=':server@foo.baz')), {'action': 'PING',
                'arguments': 'server@foo.baz', 'action_args': [],
                'sender': ''})

suite = unittest.TestLoader().loadTestsFromTestCase(ParserTests)

if __name__ == '__main__':
    unittest.main()
