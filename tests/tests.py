import unittest

import cmds_tests
import functions_tests
import parser_tests

suites = []

suites.append(cmds_tests.suite)
suites.append(functions_tests.suite)
suites.append(parser_tests.suite)

all_tests = unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.TextTestRunner().run(all_tests)
