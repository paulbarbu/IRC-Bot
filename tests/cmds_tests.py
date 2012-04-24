import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))

import unittest
from mock import patch
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

if __name__ == '__main__':
    unittest.main()
