from textwrap import dedent
import unittest

from code_generator.generators.cpp2 import (
    ArrayOnHeap,
    ArrayOnStack,
    CppIdentifierError,
    Function,
    Variable,
)


class TestArrayOnStack(unittest.TestCase):

    def test_raises_CppIdentifierError_starts_with_digit(self):
        self.assertRaises(CppIdentifierError, ArrayOnStack, "0")

    def test_name_x(self):
        self.assertTrue(ArrayOnStack("x"))

    def test_name_X(self):
        self.assertTrue(ArrayOnStack("X"))

    def test_name_aA(self):
        self.assertTrue(ArrayOnStack("aA"))

    def test_name_aAunderscore(self):
        self.assertTrue(ArrayOnStack("aA_"))

    def test_name_aAunderscore0(self):
        self.assertTrue(ArrayOnStack("aA_0"))

    def test_name_aA0underscore(self):
        self.assertTrue(ArrayOnStack("aA0_"))

    def test_name_Aa(self):
        self.assertTrue(ArrayOnStack("Aa"))

    def test_name_underscore(self):
        self.assertTrue(ArrayOnStack("_"))

    def test_name_underscore0(self):
        self.assertTrue(ArrayOnStack("_0"))

    def test_str(self):
        self.assertEqual(str(ArrayOnStack("x")), "x")

    def test_decl_str_as_int(self):
        self.assertEqual("int x[0]", ArrayOnStack("x", "int").decl_str())

    def test_decl_with_default_type(self):
        self.assertEqual(ArrayOnStack("x").decl_str(), "int x[0]")

    def test_decl_with_size_as_str(self):
        self.assertEqual(ArrayOnStack("x").size("COUNT").decl_str(), "int x[COUNT]")

    def test_decl_with_size_as_Variable(self):
        self.assertEqual(
            ArrayOnStack("x").size(Variable("COUNT")).decl_str(), "int x[COUNT]"
        )

    def test_decl_with_size_calculated(self):
        self.assertEqual(ArrayOnStack("x").add(0).decl_str(), "int x[1]")

    def test_def_str_with_size_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                int x[COUNT] =
                                {
                                    1
                                }"""
            ),
            ArrayOnStack("x", "int").add(1).size("COUNT").def_str(),
        )

    def test_def_str_with_size_as_Variable(self):
        self.assertEqual(
            dedent(
                """\
                                int x[COUNT] =
                                {
                                    1
                                }"""
            ),
            ArrayOnStack("x", "int").add(1).size(Variable("COUNT")).def_str(),
        )

    def test_def_str_with_one_item_as_int(self):
        self.assertEqual(
            dedent(
                """\
                                int x[1] =
                                {
                                    1
                                }"""
            ),
            ArrayOnStack("x", "int").add(1).def_str(),
        )

    def test_def_str_with_two_item_as_int(self):
        self.assertEqual(
            dedent(
                """\
                                int x[2] =
                                {
                                    1,
                                    2
                                }"""
            ),
            ArrayOnStack("x", "int").add(1).add(2).def_str(),
        )

    def test_def_str_with_one_item_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                Person x[1] =
                                {
                                    {"John", "Doe", 21}
                                }"""
            ),
            ArrayOnStack("x", "Person").add('{"John", "Doe", 21}').def_str(),
        )

    def test_def_str_with_two_item_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                Person x[2] =
                                {
                                    {"John", "Doe", 21},
                                    {"Jane", "Doe", 18}
                                }"""
            ),
            ArrayOnStack("x", "Person")
            .add('{"John", "Doe", 21}')
            .add('{"Jane", "Doe", 18}')
            .def_str(),
        )

    def test_def_str_with_one_item_as_Function(self):
        self.assertEqual(
            dedent(
                """\
                                Person x[1] =
                                {
                                    {"John", "Doe", 21}
                                }"""
            ),
            ArrayOnStack("x", "Person")
            .add(Function("Person").arg('"John"').arg('"Doe"').arg(21))
            .def_str(),
        )

    def test_def_str_with_two_item_as_Function(self):
        self.assertEqual(
            dedent(
                """\
                                Person x[2] =
                                {
                                    {"John", "Doe", 21},
                                    {"Jane", "Doe", 18}
                                }"""
            ),
            ArrayOnStack("x", "Person")
            .add(Function("Person").arg('"John"').arg('"Doe"').arg(21))
            .add(Function("Person").arg('"Jane"').arg('"Doe"').arg(18))
            .def_str(),
        )


class TestArrayOnHeap(unittest.TestCase):

    def test_decl_with_size_calculated(self):
        self.assertEqual(ArrayOnHeap("x").add(0).decl_str(), "int x[1]")

    def test_def_str_with_size_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                int *x = new int[COUNT];
                                x[0] = 1;"""
            ),
            ArrayOnHeap("x", "int").add(1).size("COUNT").def_str(),
        )

    def test_def_str_with_size_as_Variable(self):
        self.assertEqual(
            dedent(
                """\
                                int *x = new int[COUNT];
                                x[0] = 1;"""
            ),
            ArrayOnHeap("x", "int").add(1).size(Variable("COUNT")).def_str(),
        )

    def test_def_str_with_one_item_as_int(self):
        self.assertEqual(
            dedent(
                """\
                                int *x = new int[1];
                                x[0] = 1;"""
            ),
            ArrayOnHeap("x", "int").add(1).def_str(),
        )

    def test_def_str_with_two_item_as_int(self):
        self.assertEqual(
            dedent(
                """\
                                int *x = new int[2];
                                x[0] = 1;
                                x[1] = 2;"""
            ),
            ArrayOnHeap("x", "int").add(1).add(2).def_str(),
        )

    def test_def_str_with_one_item_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                Person *x = new Person[1];
                                x[0] = {"John", "Doe", 21};"""
            ),
            ArrayOnHeap("x", "Person").add('{"John", "Doe", 21}').def_str(),
        )

    def test_def_str_with_two_item_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                Person *x = new Person[2];
                                x[0] = {"John", "Doe", 21};
                                x[1] = {"Jane", "Doe", 18};"""
            ),
            ArrayOnHeap("x", "Person")
            .add('{"John", "Doe", 21}')
            .add('{"Jane", "Doe", 18}')
            .def_str(),
        )

    def test_def_str_with_one_item_as_Function(self):
        self.assertEqual(
            dedent(
                """\
                                Person *x = new Person[1];
                                x[0] = add;"""
            ),
            ArrayOnHeap("x", "Person").add(Function("add").arg("1")).def_str(),
        )
