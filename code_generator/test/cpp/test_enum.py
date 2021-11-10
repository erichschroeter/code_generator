from textwrap import dedent
import unittest

from code_generator.generators.cpp import Enum, EnumDeclaration, KnRStyle


class TestEnum(unittest.TestCase):

    def test_raises_error_with_empty_name(self):
        self.assertRaises(ValueError, Enum)


class TestEnumDeclaration(unittest.TestCase):

    def test_name_only(self):
        self.assertEqual(dedent("""\
            enum A {
            };"""), EnumDeclaration(
            Enum(name='A'), brace_strategy=KnRStyle).code())

    def test_one_element_with_prefix(self):
        self.assertEqual(dedent("""\
            enum Color {
            \tCOLOR_RED
            };"""), EnumDeclaration(
            Enum(name='Color', prefix='COLOR_').add('RED'), brace_strategy=KnRStyle).code())

    def test_one_element(self):
        self.assertEqual(dedent("""\
            enum Color {
            \tRED
            };"""), EnumDeclaration(
            Enum(name='Color').add('RED'), brace_strategy=KnRStyle).code())

    def test_two_elements(self):
        self.assertEqual(dedent("""\
            enum Color {
            \tRED,
            \tBLUE
            };"""), EnumDeclaration(
            Enum(name='Color').add('RED').add('BLUE'), brace_strategy=KnRStyle).code())

    def test_one_element_with_value(self):
        self.assertEqual(dedent("""\
            enum Color {
            \tRED = 0
            };"""), EnumDeclaration(
            Enum(name='Color').add('RED', 0), brace_strategy=KnRStyle).code())

    def test_two_elements_with_value(self):
        self.assertEqual(dedent("""\
            enum Color {
            \tRED = 0,
            \tBLUE = 1
            };"""), EnumDeclaration(
            Enum(name='Color').add('RED', 0).add('BLUE', 1), brace_strategy=KnRStyle).code())
