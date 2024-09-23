from textwrap import dedent
import unittest

from code_generator.generators.cpp2 import Array, Class, CppIdentifierError, CppTypeError, Function, Struct, Variable


class TestArray(unittest.TestCase):

    def test_raises_CppIdentifierError_starts_with_digit(self):
        self.assertRaises(CppIdentifierError, Array, '0')

    def test_raises_CppIdentifierError_starts_with_digit(self):
        self.assertRaises(CppIdentifierError, Array, '0')

    def test_name_x(self):
        self.assertTrue(Array('x'))

    def test_name_X(self):
        self.assertTrue(Array('X'))

    def test_name_aA(self):
        self.assertTrue(Array('aA'))

    def test_name_aAunderscore(self):
        self.assertTrue(Array('aA_'))

    def test_name_aAunderscore0(self):
        self.assertTrue(Array('aA_0'))

    def test_name_aA0underscore(self):
        self.assertTrue(Array('aA0_'))

    def test_name_Aa(self):
        self.assertTrue(Array('Aa'))

    def test_name_underscore(self):
        self.assertTrue(Array('_'))

    def test_name_underscore0(self):
        self.assertTrue(Array('_0'))

    def test_str(self):
        self.assertEqual(str(Array('x')), 'x')

    def test_decl_str_as_int(self):
        self.assertEqual('int x[]', Array('x', 'int').decl_str())

    def test_decl_with_default_type(self):
        self.assertEqual(Array('x').decl_str(), 'int x[]')

    def test_def_str_with_one_item_as_int(self):
        self.assertEqual(dedent('''\
                                int x[] =
                                {
                                    1
                                }'''),
                                Array('x', 'int').add(1).def_str())

    def test_def_str_with_two_item_as_int(self):
        self.assertEqual(dedent('''\
                                int x[] =
                                {
                                    1,
                                    2
                                }'''),
                                Array('x', 'int').add(1).add(2).def_str())

    def test_def_str_with_one_item_as_str(self):
        self.assertEqual(dedent('''\
                                Person x[] =
                                {
                                    {"John", "Doe", 21}
                                }'''),
                                Array('x', 'Person').add('{"John", "Doe", 21}').def_str())

    def test_def_str_with_two_item_as_str(self):
        self.assertEqual(dedent('''\
                                Person x[] =
                                {
                                    {"John", "Doe", 21},
                                    {"Jane", "Doe", 18}
                                }'''),
                                Array('x', 'Person').add('{"John", "Doe", 21}').add('{"Jane", "Doe", 18}').def_str())
