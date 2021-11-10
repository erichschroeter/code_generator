import unittest
from code_generator.generators.cpp import Const, Constexpr, Pure, Indentation, Static, Inline, Variable, VariableDefinition, VerbatimAboveDocs, VerbatimSameLineDocs, Volatile, Extern, Virtual, is_const, is_constexpr


class TestVerbatimAboveDocs(unittest.TestCase):

    def test_no_attachment(self):
        self.assertEqual('/// A variable named a.', VerbatimAboveDocs(Variable(name='a', type='int', docs='/// A variable named a.')).docs(None))

    def test_empty_string_attachment(self):
        self.assertEqual('/// A variable named a.', VerbatimAboveDocs(Variable(name='a', type='int', docs='/// A variable named a.')).docs(''))

    def test_docs_with_attachment(self):
        self.assertEqual('/// A variable named a.\nint a;', VerbatimAboveDocs(Variable(name='a', type='int', docs='/// A variable named a.')).docs('int a;'))

    def test_no_docs_on_cpp_element(self):
        self.assertEqual('int a;', VerbatimAboveDocs(Variable(name='a', type='int')).docs('int a;'))


class TestVerbatimSameLineDocs(unittest.TestCase):

    def test_no_attachment(self):
        self.assertEqual('// A variable named a.', VerbatimSameLineDocs(Variable(name='a', type='int', docs='// A variable named a.')).docs(None))

    def test_empty_string_attachment(self):
        self.assertEqual('// A variable named a.', VerbatimSameLineDocs(Variable(name='a', type='int', docs='// A variable named a.')).docs(''))

    def test_docs_with_attachment(self):
        self.assertEqual('int a;// A variable named a.', VerbatimSameLineDocs(Variable(name='a', type='int', docs='// A variable named a.')).docs('int a;'))

    def test_no_docs_on_cpp_element(self):
        self.assertEqual('int a;', VerbatimSameLineDocs(Variable(name='a', type='int')).docs('int a;'))
