from textwrap import dedent
import unittest

from code_generator.generators.cpp import CppIdentifierError, Enum


class TestEnum(unittest.TestCase):

    def test_raises_CppIdentifierError_starts_with_digit(self):
        self.assertRaises(CppIdentifierError, Enum, "0")

    def test_name_x(self):
        self.assertTrue(Enum("x"))

    def test_name_X(self):
        self.assertTrue(Enum("X"))

    def test_name_aA(self):
        self.assertTrue(Enum("aA"))

    def test_name_aAunderscore(self):
        self.assertTrue(Enum("aA_"))

    def test_name_aAunderscore0(self):
        self.assertTrue(Enum("aA_0"))

    def test_name_aA0underscore(self):
        self.assertTrue(Enum("aA0_"))

    def test_name_Aa(self):
        self.assertTrue(Enum("Aa"))

    def test_name_underscore(self):
        self.assertTrue(Enum("_"))

    def test_name_underscore0(self):
        self.assertTrue(Enum("_0"))

    def test_str(self):
        self.assertEqual("x", str(Enum("x")))

    def test_def_str_with_one_item_without_prefix(self):
        self.assertEqual(
            dedent(
                """\
                                enum Colors
                                {
                                    RED
                                }"""
            ),
            Enum("Colors").add("RED").def_str(),
        )

    def test_def_str_with_one_item_with_prefix(self):
        self.assertEqual(
            dedent(
                """\
                                enum Colors
                                {
                                    COLOR_RED
                                }"""
            ),
            Enum("Colors", prefix="COLOR_").add("RED").def_str(),
        )

    def test_def_str_with_one_item_with_value(self):
        self.assertEqual(
            dedent(
                """\
                                enum Colors
                                {
                                    RED = 1
                                }"""
            ),
            Enum("Colors").add("RED", 1).def_str(),
        )

    def test_def_str_with_two_item_without_prefix(self):
        self.assertEqual(
            dedent(
                """\
                                enum Colors
                                {
                                    RED,
                                    BLUE
                                }"""
            ),
            Enum("Colors").add("RED").add("BLUE").def_str(),
        )

    def test_def_str_with_two_item_with_prefix(self):
        self.assertEqual(
            dedent(
                """\
                                enum Colors
                                {
                                    COLOR_RED,
                                    COLOR_BLUE
                                }"""
            ),
            Enum("Colors", prefix="COLOR_").add("RED").add("BLUE").def_str(),
        )

    def test_def_str_with_two_item_with_value(self):
        self.assertEqual(
            dedent(
                """\
                                enum Colors
                                {
                                    RED = 1,
                                    BLUE = 2
                                }"""
            ),
            Enum("Colors").add("RED", 1).add("BLUE", 2).def_str(),
        )
