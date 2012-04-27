import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '../src/')))

import unittest
from mock import patch, MagicMock, Mock
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


if __name__ == '__main__':
    unittest.main()
