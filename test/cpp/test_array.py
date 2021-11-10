from textwrap import dedent
import unittest

from generators.cpp import Array, ArrayDeclaration, ArrayDefinition, Const, KnRStyle, Static, Variable


class TestArray(unittest.TestCase):

    def test_raises_error_with_empty_name(self):
        self.assertRaises(ValueError, Array)

    def test_raises_error_with_empty_type(self):
        self.assertRaises(ValueError, Array, name='x')


class TestArrayDeclaration(unittest.TestCase):

    def test_name_and_type_only(self):
        self.assertEqual("int A[0];", ArrayDeclaration(Array(name='A', type='int')).code())

    def test_is_declare_size(self):
        self.assertEqual("int A[];", ArrayDeclaration(Array(name='A', type='int'), is_declare_size=False).code())

    def test_size_ref(self):
        self.assertEqual("int A[COUNT];", ArrayDeclaration(Array(name='A', type='int'), size_ref=Variable(name='COUNT', type='int')).code())

    def test_qualifiers(self):
        self.assertEqual("static const int A[0];", ArrayDeclaration(Array(name='A', type='int', qualifier=Static(Const()))).code())

    def test_one_item(self):
        self.assertEqual("int A[1];", ArrayDeclaration(Array(name='A', type='int').add(Variable(name='x', type='int'))).code())

    def test_two_items(self):
        self.assertEqual("int A[2];", ArrayDeclaration(Array(name='A', type='int')
            .add(Variable(name='x', type='int'))
            .add(Variable(name='x', type='int'))).code())

class TestArrayDefinition(unittest.TestCase):

    def test_name_only(self):
        self.assertEqual(dedent("""\
            int A[] = {
            };"""), ArrayDefinition(
            Array(name='A', type='int'), brace_strategy=KnRStyle).code())

    def test_one_element(self):
        self.assertEqual(dedent("""\
            int A[] = {
            \t0
            };"""), ArrayDefinition(
            Array(name='A', type='int').add('0'), brace_strategy=KnRStyle).code())

    def test_two_element(self):
        self.assertEqual(dedent("""\
            int A[] = {
            \t0,
            \t1
            };"""), ArrayDefinition(
            Array(name='A', type='int').add('0').add('1'), brace_strategy=KnRStyle).code())
