import io
from textwrap import dedent
import unittest
from code_generator import CppFile
from cpp_generator import CppFunction
from generators.cpp import AllmanStyle, Const, Function, FunctionDeclaration, FunctionDefinition, KnRStyle, Pure, Virtual


def handle_to_factorial(self, cpp):
    cpp('return n < 1 ? 1 : (n * factorial(n - 1));')


class TestCppFunctionGenerator(unittest.TestCase):

    def handle_to_factorial(self, cpp):
        cpp('return n < 1 ? 1 : (n * factorial(n - 1));')

    def test_is_constexpr_raises_error_when_implementation_value_is_none(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        func = CppFunction(name="factorial", ret_type="int", is_constexpr=True)
        self.assertRaises(RuntimeError, func.render_to_string, cpp)

    def test_is_constexpr_render_to_string(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        func = CppFunction(name="factorial", ret_type="int",
                           implementation_handle=TestCppFunctionGenerator.handle_to_factorial, is_constexpr=True)
        func.add_argument('int n')
        func.render_to_string(cpp)
        self.assertIn(dedent('''\
            constexpr int factorial(int n)
            {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }'''), writer.getvalue())

    def test_is_constexpr_render_to_string_declaration(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        func = CppFunction(name="factorial", ret_type="int",
                           implementation_handle=TestCppFunctionGenerator.handle_to_factorial, is_constexpr=True)
        func.add_argument('int n')
        func.render_to_string_declaration(cpp)
        self.assertIn(dedent('''\
            constexpr int factorial(int n)
            {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }'''), writer.getvalue())

    def test_README_example(self):
        writer = io.StringIO()
        cpp = CppFile(None, writer=writer)
        factorial_function = CppFunction(name='factorial', ret_type='int', is_constexpr=True,
                                         implementation_handle=handle_to_factorial, documentation='/// Calculates and returns the factorial of \p n.')
        factorial_function.add_argument('int n')
        factorial_function.render_to_string(cpp)
        self.assertIn(dedent('''\
            /// Calculates and returns the factorial of \p n.
            constexpr int factorial(int n)
            {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }'''), writer.getvalue())


class TestFunction(unittest.TestCase):

    def test_raises_error_with_empty_name(self):
        self.assertRaises(ValueError, Function)


class TestFunctionDeclaration(unittest.TestCase):

    def test_default_return_type_void(self):
        self.assertEqual('void a();', FunctionDeclaration(
            Function(name='a')).code())

    def test_pure_virtual(self):
        self.assertEqual('virtual void a() = 0;', FunctionDeclaration(
            Function(name='a', qualifier=Virtual(), postfix_qualifier=Pure())).code())

    def test_with_one_arg(self):
        self.assertEqual('void a(int x);', FunctionDeclaration(
            Function(name='a').with_arg('int x')).code())

    def test_with_two_args(self):
        self.assertEqual('void a(int x, float y);', FunctionDeclaration(
            Function(name='a').with_arg('int x').with_arg('float y')).code())


class TestAllmanStyle(unittest.TestCase):

    def test_open_brace_on_line_after_function(self):
        def example_main() -> str:
            return 'return 0;'
        self.assertEqual(dedent("""\

            {
            \treturn 0;
            }"""), AllmanStyle().code(implementation_handle=example_main))


class TestKnRStyle(unittest.TestCase):

    def test_open_brace_on_same_line_as_function(self):
        def example_main() -> str:
            return 'return 0;'
        self.assertEqual(dedent("""\
             {
            \treturn 0;
            }"""), KnRStyle().code(implementation_handle=example_main))


class TestFunctionDefinition(unittest.TestCase):

    def test_default_return_type_void(self):
        self.assertEqual('void a() {\n}', FunctionDefinition(
            Function(name='a'), brace_strategy=KnRStyle()).code())

    def test_default_with_one_arg(self):
        self.assertEqual('void a(int x) {\n}', FunctionDefinition(
            Function(name='a').with_arg('int x'), brace_strategy=KnRStyle()).code())

    def test_default_with_two_arg(self):
        self.assertEqual('void a(int x, float y) {\n}', FunctionDefinition(Function(
            name='a').with_arg('int x').with_arg('float y'), brace_strategy=KnRStyle()).code())

    def test_default_with_implementation_handle(self):
        def do_something() -> str:
            return dedent("""\
            for ( auto const var : var_list )
            {
            \tvar->update();
            }""")
        self.assertEqual(dedent("""\
            void a() {
            \tfor ( auto const var : var_list )
            \t{
            \t\tvar->update();
            \t}
            }"""), FunctionDefinition(Function(name='a', implementation_handle=do_something), brace_strategy=KnRStyle()).code())

    def test_const_function(self):
        def example_accessor() -> str:
            return 'return m_count;'
        self.assertEqual(dedent("""\
            int get_count() const {
            \treturn m_count;
            }"""), FunctionDefinition(Function(name='get_count', return_type='int', postfix_qualifier=Const(), implementation_handle=example_accessor), brace_strategy=KnRStyle()).code())
