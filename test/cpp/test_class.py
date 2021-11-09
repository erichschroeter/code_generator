from textwrap import dedent
import unittest

from generators.cpp import Class, ClassDeclaration, Function, KnRStyle, Variable, Visibility


class TestClass(unittest.TestCase):

    def test_raises_error_with_empty_name(self):
        self.assertRaises(ValueError, Class)


class TestClassDeclaration(unittest.TestCase):

    def test_with_name_only(self):
        self.assertEqual(dedent("""\
            class A {
            };"""), ClassDeclaration(
            Class(name='A'), brace_strategy=KnRStyle).code())

    def test_with_one_public_member(self):
        self.assertEqual(dedent("""\
            class A {
            public:
            \tint x;
            };"""), ClassDeclaration(
            Class(name='A').add(Variable(name='x', type='int'), visibility=Visibility.PUBLIC), brace_strategy=KnRStyle).code())

    def test_with_two_public_members(self):
        self.assertEqual(dedent("""\
            class A {
            public:
            \tint x;
            \tfloat y;
            };"""), ClassDeclaration(
            Class(name='A').add(Variable(name='x', type='int'), visibility=Visibility.PUBLIC).add(Variable(name='y', type='float'), visibility=Visibility.PUBLIC), brace_strategy=KnRStyle).code())

    def test_with_one_public_method(self):
        self.assertEqual(dedent("""\
            class A {
            public:
            \tvoid Foo();
            };"""), ClassDeclaration(
            Class(name='A').add(Function(name='Foo'), visibility=Visibility.PUBLIC), brace_strategy=KnRStyle).code())

    def test_with_two_public_methods(self):
        self.assertEqual(dedent("""\
            class A {
            public:
            \tvoid Foo();
            \tint Bar();
            };"""), ClassDeclaration(
            Class(name='A').add(Function(name='Foo'), visibility=Visibility.PUBLIC).add(Function(name='Bar', return_type='int'), visibility=Visibility.PUBLIC), brace_strategy=KnRStyle).code())

    def test_with_public_member_and_public_method(self):
        self.assertEqual(dedent("""\
            class A {
            public:
            \tint x;
            \tvoid Foo();
            };"""), ClassDeclaration(
            Class(name='A').add(Variable(name='x', type='int'), visibility=Visibility.PUBLIC).add(Function(name='Foo'), visibility=Visibility.PUBLIC), brace_strategy=KnRStyle).code())

    def test_with_one_private_member(self):
        self.assertEqual(dedent("""\
            class A {
            \tint x;
            };"""), ClassDeclaration(
            Class(name='A').add(Variable(name='x', type='int'), visibility=Visibility.PRIVATE), brace_strategy=KnRStyle).code())

    def test_with_one_private_method(self):
        self.assertEqual(dedent("""\
            class A {
            \tvoid Foo();
            };"""), ClassDeclaration(
            Class(name='A').add(Function(name='Foo'), visibility=Visibility.PRIVATE), brace_strategy=KnRStyle).code())
