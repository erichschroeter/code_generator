from textwrap import dedent
import unittest

from generators.cpp import Class, ClassDeclaration, ClassDefinition, Function, KnRStyle, Variable, Visibility


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

    def test_one_public_function(self):
        self.assertEqual(dedent("""\
            void A::Foo() {
            }"""), ClassDefinition(
            Class(name='A').add(Function(name='Foo')), brace_strategy=KnRStyle).code())
