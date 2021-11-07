import io
from textwrap import dedent
import unittest
from code_generator import CppFile
from cpp_generator import CppVariable
from generators.cpp import Pure, VariableConstructorDefinition, Indentation, Static, Inline, VariableDefinition, Volatile, Const, Constexpr, Extern, Variable, VariableDeclaration, Virtual, is_const, is_constexpr


class TestCppQualifiers(unittest.TestCase):

    def test_static(self):
        self.assertEqual('static', Static()())

    def test_inline(self):
        self.assertEqual('inline', Inline()())

    def test_volatile(self):
        self.assertEqual('volatile', Volatile()())

    def test_virtual(self):
        self.assertEqual('virtual', Virtual()())

    def test_const(self):
        self.assertEqual('const', Const()())

    def test_constexpr(self):
        self.assertEqual('constexpr', Constexpr()())

    def test_extern(self):
        self.assertEqual('extern', Extern()())

    def test_pure(self):
        self.assertEqual('= 0', Pure()())

    def test_static_const(self):
        self.assertEqual('static const', Static(Const())())


class TestIsConst(unittest.TestCase):

    def test_const_only(self):
        self.assertTrue(is_const(Const()))

    def test_static_const(self):
        self.assertTrue(is_const(Static(Const())))


class TestIsConstexpr(unittest.TestCase):

    def test_constexpr_only(self):
        self.assertTrue(is_constexpr(Constexpr()))

    def test_static_constexpr(self):
        self.assertTrue(is_constexpr(Static(Constexpr())))


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


class TestIndentation(unittest.TestCase):

    def test_with_level_1(self):
        self.assertEqual('\ta', Indentation(level=1).indent('a'))

    def test_with_level_1_and_single_whitespace(self):
        self.assertEqual(' a', Indentation(
            level=1, whitespace=' ').indent('a'))

    def test_with_level_1_and_four_whitespace(self):
        self.assertEqual('    a', Indentation(
            level=1, whitespace='    ').indent('a'))

    def test_with_level_2(self):
        self.assertEqual('\t\ta', Indentation(level=2).indent('a'))

    def test_with_level_2_and_single_whitespace(self):
        self.assertEqual('  a', Indentation(
            level=2, whitespace=' ').indent('a'))

    def test_with_level_2_and_four_whitespace(self):
        self.assertEqual('        a', Indentation(
            level=2, whitespace='    ').indent('a'))


class TestVariable(unittest.TestCase):

    def test_raises_error_with_empty_name(self):
        self.assertRaises(ValueError, Variable)

    def test_raises_error_with_empty_type(self):
        self.assertRaises(ValueError, Variable, name='a')


class TestVariableDeclaration(unittest.TestCase):

    def test_with_name_and_type_only(self):
        self.assertEqual('int a;', VariableDeclaration(
            Variable(name='a', type='int')).code())

    def test_with_qualifiers(self):
        self.assertEqual('const int a;', VariableDeclaration(
            Variable(name='a', type='int', qualifier=Const())).code())

    def test_with_init_value_and_const_qualifer(self):
        self.assertEqual('const int a = 0;', VariableDeclaration(
            Variable(name='a', type='int', qualifier=Const(), init_value='0')).code())

    def test_with_init_value_and_constexpr_qualifer(self):
        self.assertEqual('constexpr int a = 0;', VariableDeclaration(
            Variable(name='a', type='int', qualifier=Constexpr(), init_value='0')).code())


class TestVariableDefinition(unittest.TestCase):

    def test_with_name_and_type_only(self):
        self.assertEqual('int a;', VariableDefinition(
            Variable(name='a', type='int')).code())

    def test_with_qualifiers(self):
        self.assertEqual('const int a;', VariableDefinition(
            Variable(name='a', type='int', qualifier=Const())).code())

    def test_with_init_value_and_const_qualifer(self):
        self.assertEqual('const int a = 0;', VariableDefinition(
            Variable(name='a', type='int', qualifier=Const(), init_value='0')).code())

    def test_with_init_value_and_constexpr_qualifer(self):
        self.assertEqual('constexpr int a = 0;', VariableDefinition(
            Variable(name='a', type='int', qualifier=Constexpr(), init_value='0')).code())

    # def test_with_ref_to_parent(self):
    #     self.assertEqual('int MyClass::a;', VariableDefinition(Variable(name='a', type='int', init_value='0', ref_to_parent=)).code())


class TestVariableConstructorDefinition(unittest.TestCase):

    def test_with_name_and_type_only(self):
        self.assertEqual('a()', VariableConstructorDefinition(
            Variable(name='a', type='int')).code())

    def test_with_qualifiers(self):
        self.assertEqual('a()', VariableConstructorDefinition(
            Variable(name='a', type='int', qualifier=Const())).code())

    def test_with_init_value_and_const_qualifer(self):
        self.assertEqual('a(0)', VariableConstructorDefinition(
            Variable(name='a', type='int', qualifier=Const(), init_value='0')).code())

    def test_with_init_value_and_constexpr_qualifer(self):
        self.assertEqual('a(0)', VariableConstructorDefinition(
            Variable(name='a', type='int', qualifier=Constexpr(), init_value='0')).code())
