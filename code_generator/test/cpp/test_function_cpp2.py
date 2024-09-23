from textwrap import dedent
import unittest

from code_generator.generators.cpp2 import CppIdentifierError, CppTypeError, Function, Variable


class TestFunction(unittest.TestCase):

    def test_raises_CppIdentifierError_starts_with_digit(self):
        self.assertRaises(CppIdentifierError, Function, '0')

    def test_raises_CppTypeError_starts_with_digit(self):
        self.assertRaises(CppTypeError, Function, 'x', '0')

    def test_name_x(self):
        self.assertTrue(Function('x'))

    def test_name_X(self):
        self.assertTrue(Function('X'))

    def test_name_aA(self):
        self.assertTrue(Function('aA'))

    def test_name_aAunderscore(self):
        self.assertTrue(Function('aA_'))

    def test_name_aAunderscore0(self):
        self.assertTrue(Function('aA_0'))

    def test_name_aA0underscore(self):
        self.assertTrue(Function('aA0_'))

    def test_name_Aa(self):
        self.assertTrue(Function('Aa'))

    def test_name_underscore(self):
        self.assertTrue(Function('_'))

    def test_name_underscore0(self):
        self.assertTrue(Function('_0'))

    def test_decl_with_default_type(self):
        self.assertEqual(Function('x').decl_str(), 'void x()')

    def test_decl_with_type_with_whitespace(self):
        self.assertEqual(Function('x', 'unsigned int').decl_str(), 'unsigned int x()')

    def test_decl_with_type_with_pointer(self):
        self.assertEqual(Function('x', 'int *').decl_str(), 'int * x()')

    def test_decl_with_type_with_reference(self):
        self.assertEqual(Function('x', 'int &').decl_str(), 'int & x()')

    def test_decl_with_custom_type(self):
        self.assertEqual(Function('x', type='bool').decl_str(), 'bool x()')

    def test_decl_raises_CppTypeError_with_type_with_whitespace_and_invalid_identifier(self):
        self.assertRaises(CppTypeError, Function, 'x', type='int % whitespace')

    def test_decl_with_custom_one_qualifier(self):
        self.assertEqual(Function('x', qualifiers=['virtual']).decl_str(), 'virtual void x()')

    def test_decl_with_custom_two_qualifier(self):
        self.assertEqual(Function('x', qualifiers=['static', 'const']).decl_str(), 'static const void x()')

    def test_str(self):
        self.assertEqual(str(Function('x')), 'x')

    def test_decl_with_one_arg_as_str(self):
        self.assertEqual(Function('x').arg('int').decl_str(), 'void x(int)')

    def test_decl_with_two_arg_as_str(self):
        self.assertEqual(Function('x').arg('int').arg('bool enable').decl_str(), 'void x(int, bool enable)')

    def test_decl_with_one_arg_as_Variable(self):
        self.assertEqual(Function('x').arg(Variable('x')).decl_str(), 'void x(void x)')

    def test_decl_with_two_arg_as_Variable(self):
        self.assertEqual(Function('x').arg(Variable('x')).arg(Variable('y', type='int')).decl_str(), 'void x(void x, int y)')

    def test_call_with_one_arg_as_str(self):
        self.assertEqual('y', Function('x').arg('y').call_str())

    def test_call_with_two_arg_as_str(self):
        self.assertEqual('y, z', Function('x').arg('y').arg('z').call_str())

    def test_call_with_one_arg_as_Variable(self):
        self.assertEqual('y', Function('x').arg(Variable('y')).call_str())

    def test_call_with_two_arg_as_Variable(self):
        self.assertEqual('y, z', Function('x').arg(Variable('y')).arg(Variable('z')).call_str())
