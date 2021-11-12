import io
from textwrap import dedent
import unittest
from code_generator.code_generator import CppFile
from code_generator.cpp_generator import CppVariable
from code_generator.generators.cpp import Extern, Namespace, VariableConstructorDefinition, VariableDefinition, Const, Constexpr, Variable, VariableDeclaration


class TestCppVariableGenerator(unittest.TestCase):

    def test_cpp_var_via_writer(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        variables = CppVariable(name="var1",
                                type="char*",
                                is_class_member=False,
                                is_static=False,
                                is_const=True,
                                initialization_value='0')
        variables.render_to_string(cpp)
        self.assertEqual('const char* var1 = 0;\n', writer.getvalue())

    def test_is_constexpr_raises_error_when_is_const_true(self):
        self.assertRaises(RuntimeError, CppVariable, name="COUNT", type="int",
                          is_class_member=True, is_const=True, is_constexpr=True, initialization_value='0')

    def test_is_constexpr_raises_error_when_initialization_value_is_none(self):
        self.assertRaises(RuntimeError, CppVariable, name="COUNT",
                          type="int", is_class_member=True, is_constexpr=True)

    def test_is_constexpr_render_to_string(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        variables = CppVariable(name="COUNT",
                                type="int",
                                is_class_member=False,
                                is_constexpr=True,
                                initialization_value='0')
        variables.render_to_string(cpp)
        self.assertIn('constexpr int COUNT = 0;', writer.getvalue())

    def test_is_constexpr_render_to_string_declaration(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        variables = CppVariable(name="COUNT",
                                type="int",
                                is_class_member=True,
                                is_constexpr=True,
                                initialization_value='0')
        variables.render_to_string_declaration(cpp)
        self.assertIn('constexpr int COUNT = 0;', writer.getvalue())

    def test_is_extern_raises_error_when_is_static_is_true(self):
        self.assertRaises(RuntimeError, CppVariable, name="var1",
                          type="char*", is_static=True, is_extern=True)

    def test_is_extern_render_to_string(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        v = CppVariable(name="var1", type="char*", is_extern=True)
        v.render_to_string(cpp)
        self.assertIn('extern char* var1;', writer.getvalue())


class TestVariable(unittest.TestCase):

    def test_raises_error_with_empty_name(self):
        self.assertRaises(ValueError, Variable)

    def test_raises_error_with_empty_type(self):
        self.assertRaises(ValueError, Variable, name='a')


class TestVariableDeclaration(unittest.TestCase):

    def test_name_and_type_only(self):
        self.assertEqual('int a;', VariableDeclaration(
            Variable(name='a', type='int')).code())

    def test_qualifier_const(self):
        self.assertEqual('const int a;', VariableDeclaration(
            Variable(name='a', type='int', qualifier=Const())).code())

    def test_qualifier_constexpr(self):
        self.assertEqual('constexpr int a = 0;', VariableDeclaration(
            Variable(name='a', type='int', init_value='0', qualifier=Constexpr())).code())

    def test_qualifier_constexpr_raises_error_when_no_init_value(self):
        self.assertRaises(ValueError, VariableDeclaration(
            Variable(name='a', type='int', qualifier=Constexpr())).code)

    def test_qualifier_non_const(self):
        self.assertEqual('extern int a;', VariableDeclaration(
            Variable(name='a', type='int', qualifier=Extern())).code())

    def test_init_value(self):
        self.assertEqual('int a;', VariableDeclaration(
            Variable(name='a', type='int', init_value='0')).code())


class TestVariableDefinition(unittest.TestCase):

    def test_name_and_type_only(self):
        self.assertEqual('int a = 0;', VariableDefinition(
            Variable(name='a', type='int')).code())

    def test_qualifiers(self):
        self.assertEqual('const int a = 0;', VariableDefinition(
            Variable(name='a', type='int', qualifier=Const())).code())

    def test_init_value(self):
        self.assertEqual('int a = MY_CONSTANT;', VariableDefinition(
            Variable(name='a', type='int', init_value='MY_CONSTANT')).code())

    def test_ref_to_parent(self):
        self.assertEqual('int MyClass::a = 0;', VariableDefinition(
            Variable(name='a', type='int', ref_to_parent=Namespace(name='MyClass'))).code())


class TestVariableConstructorDefinition(unittest.TestCase):

    def test_name_and_type_only(self):
        self.assertEqual('a()', VariableConstructorDefinition(
            Variable(name='a', type='int')).code())

    def test_qualifiers(self):
        self.assertEqual('a()', VariableConstructorDefinition(
            Variable(name='a', type='int', qualifier=Const())).code())

    def test_init_value_and_const_qualifer(self):
        self.assertEqual('a(0)', VariableConstructorDefinition(
            Variable(name='a', type='int', qualifier=Const(), init_value='0')).code())

    def test_init_value_and_constexpr_qualifer(self):
        self.assertEqual('a(0)', VariableConstructorDefinition(
            Variable(name='a', type='int', qualifier=Constexpr(), init_value='0')).code())
