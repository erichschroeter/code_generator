from textwrap import dedent
import unittest

from code_generator.generators.cpp2 import CppIdentifierError, CppTypeError, Function


class TestFunction(unittest.TestCase):

    def test_raises_CppIdentifierError_starts_with_digit(self):
        self.assertRaises(CppIdentifierError, Function, '0')

    def test_raises_CppIdentifierError_starts_with_digit(self):
        self.assertRaises(CppIdentifierError, Function, '0')

    def test_name_x(self):
        self.assertTrue(Function('x'))

    def test_name_X(self):
        self.assertTrue(Function, 'X')

    def test_name_aA(self):
        self.assertTrue(Function, 'aA')

    def test_name_aAunderscore(self):
        self.assertTrue(Function, 'aA_')

    def test_name_aAunderscore0(self):
        self.assertTrue(Function, 'aA_0')

    def test_name_aA0underscore(self):
        self.assertTrue(Function, 'aA0_')

    def test_name_Aa(self):
        self.assertTrue(Function, 'Aa')

    def test_name_underscore(self):
        self.assertTrue(Function, '_')

    def test_name_underscore0(self):
        self.assertTrue(Function, '_0')

    def test_decl_with_default_type(self):
        self.assertEqual(Function('x').declaration_str(), 'void x()')

    def test_decl_with_custom_type(self):
        self.assertEqual(Function('x', type='bool').declaration_str(), 'bool x()')

    def test_decl_raises_CppTypeError_with_type_with_whitespace(self):
        self.assertRaises(CppTypeError, Function, 'x', type='int whitespace')

    def test_decl_with_custom_one_qualifier(self):
        self.assertEqual(Function('x', qualifiers=['virtual']).declaration_str(), 'virtual void x()')

    def test_decl_with_custom_two_qualifier(self):
        self.assertEqual(Function('x', qualifiers=['static', 'const']).declaration_str(), 'static const void x()')

    def test_str(self):
        self.assertEqual(str(Function('x')), 'x')
