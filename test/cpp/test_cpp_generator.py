import os
import filecmp
import unittest

from cpp_generator_tests import generate_array, generate_class, generate_enum, generate_func, generate_var


class TestCppGenerator(unittest.TestCase):
    '''
    Test C++ code generation
    '''

    def test_cpp_variables(self):
        generate_var(output_dir='.')
        expected_cpp = ['var.cpp']
        self.assertEqual(filecmp.cmpfiles(
            '.', 'tests', expected_cpp)[0], expected_cpp)
        os.remove(expected_cpp[0])

    def test_cpp_arrays(self):
        generate_array(output_dir='.')
        expected_cpp = ['array.cpp']
        self.assertEqual(filecmp.cmpfiles(
            '.', 'tests', expected_cpp)[0], expected_cpp)
        os.remove(expected_cpp[0])

    def test_cpp_function(self):
        generate_func(output_dir='.')
        expected_cpp = ['func.cpp']
        expected_h = ['func.h']
        self.assertEqual(filecmp.cmpfiles(
            '.', 'tests', expected_cpp)[0], expected_cpp)
        self.assertEqual(filecmp.cmpfiles(
            '.', 'tests', expected_h)[0], expected_h)
        os.remove(expected_cpp[0])
        os.remove(expected_h[0])

    def test_cpp_enum(self):
        generate_enum(output_dir='.')
        expected_cpp = ['enum.cpp']
        self.assertEqual(filecmp.cmpfiles(
            '.', 'tests', expected_cpp)[0], expected_cpp)
        os.remove(expected_cpp[0])

    def test_cpp_class(self):
        generate_class(output_dir='.')
        expected_cpp = ['class.cpp']
        expected_h = ['class.h']
        self.assertEqual(filecmp.cmpfiles(
            '.', 'tests', expected_cpp)[0], expected_cpp)
        self.assertEqual(filecmp.cmpfiles(
            '.', 'tests', expected_h)[0], expected_h)
        os.remove(expected_cpp[0])
        os.remove(expected_h[0])
