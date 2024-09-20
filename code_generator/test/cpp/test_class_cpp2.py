from textwrap import dedent
import unittest

from code_generator.generators.cpp2 import Class, CppIdentifierError, CppTypeError, Function, Struct, Variable


class TestClass(unittest.TestCase):

    def test_raises_CppIdentifierError_starts_with_digit(self):
        self.assertRaises(CppIdentifierError, Class, '0')

    def test_raises_CppIdentifierError_starts_with_digit(self):
        self.assertRaises(CppIdentifierError, Class, '0')

    def test_name_x(self):
        self.assertTrue(Class('x'))

    def test_name_X(self):
        self.assertTrue(Class, 'X')

    def test_name_aA(self):
        self.assertTrue(Class, 'aA')

    def test_name_aAunderscore(self):
        self.assertTrue(Class, 'aA_')

    def test_name_aAunderscore0(self):
        self.assertTrue(Class, 'aA_0')

    def test_name_aA0underscore(self):
        self.assertTrue(Class, 'aA0_')

    def test_name_Aa(self):
        self.assertTrue(Class, 'Aa')

    def test_name_underscore(self):
        self.assertTrue(Class, '_')

    def test_name_underscore0(self):
        self.assertTrue(Class, '_0')

    def test_decl_with_default_type(self):
        self.assertEqual(dedent('''\
                                class x
                                {
                                }'''),
                                Class('x').decl_str())

    def test_str(self):
        self.assertEqual(str(Class('x')), 'x')

    def test_decl_with_one_private_member_as_str(self):
        self.assertEqual(dedent('''\
                                class x
                                {
                                private:
                                    static const int X = 0;
                                }'''),
                                Class('x').member('static const int X = 0;').decl_str())

    def test_decl_with_one_private_member_as_Variable(self):
        self.assertEqual(dedent('''\
                                class x
                                {
                                private:
                                    int x;
                                }'''),
                                Class('x').member(Variable('x', type='int')).decl_str())

    def test_decl_with_one_private_member_as_Function(self):
        self.assertEqual(dedent('''\
                                class x
                                {
                                private:
                                    bool is_enabled();
                                }'''),
                                Class('x').member(Function('is_enabled', type='bool')).decl_str())

    def test_decl_with_one_protected_member_as_str(self):
        self.assertEqual(dedent('''\
                                class x
                                {
                                protected:
                                    static const int X = 0;
                                }'''),
                                Class('x').member('static const int X = 0;', scope='protected').decl_str())

    def test_decl_with_one_protected_member_as_Variable(self):
        self.assertEqual(dedent('''\
                                class x
                                {
                                protected:
                                    int x;
                                }'''),
                                Class('x').member(Variable('x', type='int'), scope='protected').decl_str())

    def test_decl_with_one_protected_member_as_Function(self):
        self.assertEqual(dedent('''\
                                class x
                                {
                                protected:
                                    bool is_enabled();
                                }'''),
                                Class('x').member(Function('is_enabled', type='bool'), scope='protected').decl_str())

    def test_decl_with_one_public_member_as_str(self):
        self.assertEqual(dedent('''\
                                class x
                                {
                                public:
                                    static const int X = 0;
                                }'''),
                                Class('x').member('static const int X = 0;', scope='public').decl_str())

    def test_decl_with_one_public_member_as_Variable(self):
        self.assertEqual(dedent('''\
                                class x
                                {
                                public:
                                    int x;
                                }'''),
                                Class('x').member(Variable('x', type='int'), scope='public').decl_str())

    def test_decl_with_one_public_member_as_Function(self):
        self.assertEqual(dedent('''\
                                class x
                                {
                                public:
                                    bool is_enabled();
                                }'''),
                                Class('x').member(Function('is_enabled', type='bool'), scope='public').decl_str())


class TestStruct(unittest.TestCase):

    def test_decl_with_default_type(self):
        self.assertEqual(dedent('''\
                                struct x
                                {
                                }'''),
                                Struct('x').decl_str())
