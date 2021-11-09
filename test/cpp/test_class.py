from textwrap import dedent
import unittest

from generators.cpp import Class, ClassDeclaration, KnRStyle


class TestClass(unittest.TestCase):

    def test_raises_error_with_empty_name(self):
        self.assertRaises(ValueError, Class)


# class TestClassDeclaration(unittest.TestCase):

#     def test_with_name_only(self):
#         self.assertEqual(dedent("""\
#             class A {
#             }"""), ClassDeclaration(
#             Class(name='A'), brace_strategy=KnRStyle()).code())
