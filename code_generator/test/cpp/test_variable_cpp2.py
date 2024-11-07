import unittest

from code_generator.generators.cpp2 import CppIdentifierError, CppTypeError, Variable


class TestVariable(unittest.TestCase):

    def test_raises_CppIdentifierError_starts_with_digit(self):
        self.assertRaises(CppIdentifierError, Variable, "0")

    def test_raises_CppTypeError_starts_with_digit(self):
        self.assertRaises(CppTypeError, Variable, "x", "0")

    def test_name_x(self):
        self.assertTrue(Variable("x"))

    def test_name_X(self):
        self.assertTrue(Variable("X"))

    def test_name_aA(self):
        self.assertTrue(Variable("aA"))

    def test_name_aAunderscore(self):
        self.assertTrue(Variable("aA_"))

    def test_name_aAunderscore0(self):
        self.assertTrue(Variable("aA_0"))

    def test_name_aA0underscore(self):
        self.assertTrue(Variable("aA0_"))

    def test_name_Aa(self):
        self.assertTrue(Variable("Aa"))

    def test_name_underscore(self):
        self.assertTrue(Variable("_"))

    def test_name_underscore0(self):
        self.assertTrue(Variable("_0"))

    def test_name_namespace(self):
        self.assertTrue(Variable("company::Type"))

    def test_type_namespace(self):
        self.assertTrue(Variable("name", type="std::string"))

    def test_decl_with_default_type(self):
        self.assertEqual(Variable("x").decl_str(), "void x")

    def test_decl_with_type_with_whitespace(self):
        self.assertEqual(Variable("x", "unsigned int").decl_str(), "unsigned int x")

    def test_decl_with_type_with_pointer(self):
        self.assertEqual(Variable("x", "int *").decl_str(), "int * x")

    def test_decl_with_type_with_reference(self):
        self.assertEqual(Variable("x", "int &").decl_str(), "int & x")

    def test_decl_with_custom_type(self):
        self.assertEqual(Variable("x", type="bool").decl_str(), "bool x")

    def test_decl_raises_CppTypeError_with_type_with_whitespace_and_invalid_identifier(
        self,
    ):
        self.assertRaises(CppTypeError, Variable, "x", type="int ^ whitespace")

    def test_decl_with_custom_one_qualifier(self):
        self.assertEqual(
            Variable("x", qualifiers=["extern"]).decl_str(), "extern void x"
        )

    def test_decl_with_custom_two_qualifier(self):
        self.assertEqual(
            Variable("x", qualifiers=["extern", "const"]).decl_str(),
            "extern const void x",
        )

    def test_str(self):
        self.assertEqual(str(Variable("x")), "x")

    def test_def_with_default(self):
        self.assertEqual(Variable("x").def_str(), "void x = 0")

    def test_def_with_value_as_int(self):
        self.assertEqual(Variable("x").val(1).def_str(), "void x = 1")

    def test_def_with_value_as_str(self):
        self.assertEqual(Variable("x").val("hello").def_str(), 'void x = "hello"')

    def test_def_with_value_as_Variable(self):
        self.assertEqual(
            Variable("x").val(Variable("myfunc")).def_str(), "void x = myfunc"
        )
