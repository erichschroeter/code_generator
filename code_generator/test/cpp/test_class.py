from textwrap import dedent
import unittest

from code_generator.generators.cpp import Class, ClassArrayInitializer, ClassDeclaration, ClassDefinition, Function, KnRStyle, SingleLineStyle, Variable, Visibility


class TestClass(unittest.TestCase):

    def test_raises_error_with_empty_name(self):
        self.assertRaises(ValueError, Class)


class TestClassDeclaration(unittest.TestCase):

    def test_name_only(self):
        self.assertEqual(dedent("""\
            class A {
            };"""), ClassDeclaration(
            Class(name='A'), brace_strategy=KnRStyle).code())

    def test_one_public_element(self):
        self.assertEqual(dedent("""\
            class A {
            public:
            \tint x;
            };"""), ClassDeclaration(
            Class(name='A').add(Variable(name='x', type='int'), visibility=Visibility.PUBLIC), brace_strategy=KnRStyle).code())

    def test_two_public_elements(self):
        self.assertEqual(dedent("""\
            class A {
            public:
            \tint x;
            \tvoid Foo();
            };"""), ClassDeclaration(
            Class(name='A').add(Variable(name='x', type='int'), visibility=Visibility.PUBLIC).add(Function(name='Foo'), visibility=Visibility.PUBLIC), brace_strategy=KnRStyle).code())

    def test_one_private_element(self):
        self.assertEqual(dedent("""\
            class A {
            \tint x;
            };"""), ClassDeclaration(
            Class(name='A').add(Variable(name='x', type='int'), visibility=Visibility.PRIVATE), brace_strategy=KnRStyle).code())

    def test_two_private_elements(self):
        self.assertEqual(dedent("""\
            class A {
            \tint x;
            \tvoid Foo();
            };"""), ClassDeclaration(
            Class(name='A').add(Variable(name='x', type='int'), visibility=Visibility.PRIVATE).add(Function(name='Foo'), visibility=Visibility.PRIVATE), brace_strategy=KnRStyle).code())

    def test_alternating_visibility_elements(self):
        self.assertEqual(dedent("""\
            class A {
            \tint x;
            public:
            \tvoid Foo();
            private:
            \tfloat y;
            };"""), ClassDeclaration(
            Class(name='A')
            .add(Variable(name='x', type='int'), visibility=Visibility.PRIVATE)
            .add(Function(name='Foo'), visibility=Visibility.PUBLIC)
            .add(Variable(name='y', type='float'), visibility=Visibility.PRIVATE), brace_strategy=KnRStyle).code())

    def test_inheritance_with_one_private(self):
        self.assertEqual(dedent("""\
            class Circle : private Shape {
            };"""), ClassDeclaration(
            Class(name='Circle', parents=[('Shape', Visibility.PRIVATE)]), brace_strategy=KnRStyle).code())

    def test_inheritance_with_one_public_and_one_private(self):
        self.assertEqual(dedent("""\
            class Dog : public Animal, private Mammal {
            };"""), ClassDeclaration(
            Class(name='Dog', parents=[('Animal', Visibility.PUBLIC), ('Mammal', Visibility.PRIVATE)]), brace_strategy=KnRStyle).code())


class TestClassDefinition(unittest.TestCase):

    def test_no_elements(self):
        self.assertEqual('', ClassDefinition(
            Class(name='A'), brace_strategy=KnRStyle).code())

    def test_one_function(self):
        self.assertEqual(dedent("""\
            void A::Foo() {
            }"""), ClassDefinition(
            Class(name='A').add(Function(name='Foo')), brace_strategy=KnRStyle).code())

    def test_constructor(self):
        self.assertEqual(dedent("""\
            A::A() {
            }"""), ClassDefinition(
            Class(name='A').add(Function(name='A')), brace_strategy=KnRStyle).code())

    def test_constructor_with_one_arg(self):
        self.assertEqual(dedent("""\
            A::A() :
            x(1) {
            }"""), ClassDefinition(
            Class(name='A').add(Function(name='A')).add(Variable(name='x', type='int', init_value='1')), brace_strategy=KnRStyle).code())

    def test_constructor_with_two_args(self):
        self.assertEqual(dedent("""\
            A::A() :
            x(0),
            y(3.14) {
            }"""), ClassDefinition(
            Class(name='A')
                .add(Function(name='A'))
                .add(Variable(name='x', type='int', init_value='0'))
                .add(Variable(name='y', type='float', init_value='3.14')), brace_strategy=KnRStyle).code())

    def test_two_functions(self):
        def factorial():
            return 'return n < 1 ? 1 : (n * factorial(n - 1));'
        self.assertEqual(dedent("""\
            int A::factorial(int n) {
            \treturn n < 1 ? 1 : (n * factorial(n - 1));
            }
            void A::Foo() {
            }"""), ClassDefinition(
            Class(name='A')
                .add(Function(name='factorial', return_type='int', args=['int n'], implementation_handle=factorial))
                .add(Function(name='Foo')), brace_strategy=KnRStyle).code())


class TestClassArrayInitializer(unittest.TestCase):

    def test_no_member(self):
        self.assertEqual('{}', ClassArrayInitializer(
            Class(name='A'), brace_strategy=SingleLineStyle).code())

    def test_one_member(self):
        self.assertEqual('{0}', ClassArrayInitializer(
            Class(name='A').add(Variable(name='x', type='int')), brace_strategy=SingleLineStyle).code())

    def test_two_members(self):
        self.assertEqual('{0, 0}', ClassArrayInitializer(
            Class(name='A').add(Variable(name='x', type='int')).add(Variable(name='y', type='int')), brace_strategy=SingleLineStyle).code())

    def test_default_init_value_long(self):
        self.assertEqual('{0}', ClassArrayInitializer(
            Class(name='A').add(Variable(name='x', type='long')), brace_strategy=SingleLineStyle).code())

    def test_default_init_value_string(self):
        self.assertEqual('{""}', ClassArrayInitializer(
            Class(name='A').add(Variable(name='x', type='string')), brace_strategy=SingleLineStyle).code())

    def test_default_init_value_char(self):
        self.assertEqual('{""}', ClassArrayInitializer(
            Class(name='A').add(Variable(name='x', type='char *')), brace_strategy=SingleLineStyle).code())

    def test_default_init_value_double(self):
        self.assertEqual('{0.0}', ClassArrayInitializer(
            Class(name='A').add(Variable(name='x', type='double')), brace_strategy=SingleLineStyle).code())

    def test_default_init_value_float(self):
        self.assertEqual('{0.0}', ClassArrayInitializer(
            Class(name='A').add(Variable(name='x', type='float')), brace_strategy=SingleLineStyle).code())

    def test_raises_error_with_type_unknown_and_no_init_value(self):
        self.assertRaises(ValueError, ClassArrayInitializer(
            Class(name='A').add(Variable(name='x', type='UnknownType')), brace_strategy=SingleLineStyle).code)
