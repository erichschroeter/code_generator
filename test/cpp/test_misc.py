import unittest
from generators.cpp import Const, Constexpr, Pure, Indentation, Static, Inline, Volatile, Extern, Virtual, is_const, is_constexpr


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
