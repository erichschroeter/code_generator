from textwrap import dedent
import unittest

from code_generator.generators.cpp import Class, Function, Header, Variable


class TestHeader(unittest.TestCase):

    def test_str_default(self):
        self.assertEqual(
            dedent(
                """\
                                """
            ),
            str(Header("x.h")),
        )

    def test_str_default_with_guard(self):
        self.assertEqual(
            dedent(
                """\
                                #ifndef X_H
                                #define X_H
                                #endif
                                """
            ),
            str(Header("x.h").guard("X_H")),
        )

    def test_str_with_one_include(self):
        self.assertEqual(
            dedent(
                """\
                                #include <iostream>
                                """
            ),
            str(Header("x.h").include("iostream")),
        )

    def test_str_with_two_include(self):
        self.assertEqual(
            dedent(
                """\
                                #include <cassert>
                                #include <iostream>
                                """
            ),
            str(Header("x.h").include("cassert").include("iostream")),
        )

    def test_str_with_one_includelocal(self):
        self.assertEqual(
            dedent(
                """\
                                #include "stdint.h"
                                """
            ),
            str(Header("x.h").includelocal("stdint.h")),
        )

    def test_str_with_two_includelocal(self):
        self.assertEqual(
            dedent(
                """\
                                #include "assert.h"
                                #include "stdint.h"
                                """
            ),
            str(Header("x.h").includelocal("assert.h").includelocal("stdint.h")),
        )

    def test_str_with_add_one_item_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                static const int X = 0;
                                """
            ),
            str(Header("x.h").add("static const int X = 0;")),
        )

    def test_str_with_add_one_item_as_Variable(self):
        self.assertEqual(
            dedent(
                """\
                                int X;
                                """
            ),
            str(Header("x.h").add(Variable("X", "int"))),
        )

    def test_str_with_add_one_item_as_Function(self):
        self.assertEqual(
            dedent(
                """\
                                bool is_enabled();
                                """
            ),
            str(Header("x.h").add(Function("is_enabled", "bool"))),
        )

    def test_str_with_add_one_item_as_Class(self):
        self.assertEqual(
            dedent(
                """\
                                class Person
                                {
                                };
                                """
            ),
            str(Header("x.h").add(Class("Person"))),
        )

    def test_str_with_add_two_item_as_str(self):
        self.assertEqual(
            dedent(
                """\
                                int X = 0;
                                int Y = 0;
                                """
            ),
            str(Header("x.h").add("int X = 0;").add("int Y = 0;")),
        )

    def test_str_with_guard_and_include_and_includelocal_and_one_item(self):
        self.assertEqual(
            dedent(
                """\
                                #ifndef X_H
                                #define X_H
                                #include <iostream>
                                #include "stdio.h"
                                class Person
                                {
                                };
                                #endif
                                """
            ),
            str(
                Header("x.h")
                .guard("X_H")
                .include("iostream")
                .includelocal("stdio.h")
                .add(Class("Person"))
            ),
        )
