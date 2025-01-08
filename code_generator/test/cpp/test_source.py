from textwrap import dedent
import unittest

from code_generator.generators.cpp import Class, Function, Header, Source, Variable


class TestSource(unittest.TestCase):

    def test_str_default(self):
        self.assertEqual("", str(Source("x.cpp")))

    def test_str_with_one_include_as_str(self):
        self.assertEqual(
            "#include <iostream>\n", str(Source("x.cpp").include("iostream"))
        )

    def test_str_with_one_include_as_Header(self):
        self.assertEqual(
            "#include <custom.h>\n", str(Source("x.cpp").include(Header("custom.h")))
        )

    def test_str_with_two_include(self):
        self.assertEqual(
            dedent(
                """\
                                #include <cassert>
                                #include <iostream>
                                """
            ),
            str(Source("x.cpp").include("cassert").include("iostream")),
        )

    def test_str_with_one_includelocal_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                #include "stdint.h"
                                """
            ),
            str(Source("x.cpp").includelocal("stdint.h")),
        )

    def test_str_with_one_includelocal_as_Header(self):
        self.assertEqual(
            dedent(
                """\
                                #include "custom.h"
                                """
            ),
            str(Source("x.cpp").includelocal(Header("custom.h"))),
        )

    def test_str_with_two_includelocal(self):
        self.assertEqual(
            dedent(
                """\
                                #include "assert.h"
                                #include "stdint.h"
                                """
            ),
            str(Source("x.cpp").includelocal("assert.h").includelocal("stdint.h")),
        )

    def test_str_with_add_one_item_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                static const int X = 0;
                                """
            ),
            str(Source("x.cpp").add("static const int X = 0;")),
        )

    def test_str_with_add_one_item_as_Variable(self):
        self.assertEqual(
            dedent(
                """\
                                int X = 0;
                                """
            ),
            str(Source("x.cpp").add(Variable("X", "int"))),
        )

    def test_str_with_add_one_item_as_Function(self):
        self.assertEqual(
            dedent(
                """\
                                bool is_enabled()
                                {
                                }
                                """
            ),
            str(Source("x.cpp").add(Function("is_enabled", "bool"))),
        )

    # def test_str_with_add_one_item_as_Class(self):
    #     self.assertEqual(
    #         dedent(
    #             """\
    #                             unsigned int Person::get_age()
    #                             {
    #                             return 21;
    #                             }
    #                             """
    #         ),
    #         str(Source("x.cpp").add(Class("Person").member(Function("get_age", "unsigned int").impl("return 21;")))),
    #     )

    def test_str_with_add_two_item_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                int X = 0;
                                int Y = 0;
                                """
            ),
            str(Source("x.cpp").add("int X = 0;").add("int Y = 0;")),
        )

    def test_str_with_include_and_includelocal_and_one_item(self):
        self.assertEqual(
            dedent(
                """\
                                #include <iostream>
                                #include "stdio.h"
                                int x = 0;
                                """
            ),
            str(
                Source("x.cpp")
                .include("iostream")
                .includelocal("stdio.h")
                .add(Variable("x", type="int"))
            ),
        )
