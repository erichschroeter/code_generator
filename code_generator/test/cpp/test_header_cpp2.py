from textwrap import dedent
import unittest

from code_generator.generators.cpp2 import Header


class TestHeader(unittest.TestCase):

    def test_str_default(self):
        self.assertEqual(dedent('''\
                                '''),
                                str(Header('x.h')))

    def test_str_default_with_guard(self):
        self.assertEqual(dedent('''\
                                #ifndef X_H
                                #define X_H
                                #endif'''),
                                str(Header('x.h').guard('X_H')))

    def test_str_with_include(self):
        self.assertEqual(dedent('''\
                                #include <iostream>'''),
                                str(Header('x.h').include('iostream')))

    def test_str_with_includelocal(self):
        self.assertEqual(dedent('''\
                                #include "stdint.h"'''),
                                str(Header('x.h').includelocal('stdint.h')))
