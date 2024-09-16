# Code Generator

- [Code Generator](#code-generator)
  - [Usage examples](#usage-examples)
    - [Generate C++ code from Python code](#generate-c-code-from-python-code)
      - [Python code](#python-code)
      - [Generated C++ code](#generated-c-code)
      - [Creating functions](#creating-functions)
        - [Python code](#python-code-1)
        - [Generated C++ code](#generated-c-code-1)
      - [Creating classes and structures](#creating-classes-and-structures)
        - [Python code](#python-code-2)
        - [Generated C++ code](#generated-c-code-2)
      - [Rendering `CppClass` objects to C++ declaration and implementation](#rendering-cppclass-objects-to-c-declaration-and-implementation)
        - [Python code](#python-code-3)
        - [Generated C++ declaration](#generated-c-declaration)
      - [Generated C++ implementation](#generated-c-implementation)
  - [Maintainers](#maintainers)

Simple and straightforward code generator for creating C++ code.
It also could be used for generating code in any programming language.
Written using Python 3.

Every C++ element could render its current state to a string that could be evaluated as 
a legal C++ construction.
Some elements could be rendered to a pair of representations (C++ classes and functions declaration and implementation)

The idea of this project was mainly based on [Eric Reynold's article](http://www.codeproject.com/Articles/571645/Really-simple-Cplusplus-code-generation-in-Python).
However, this solution has been both simplified and extended compared to the initial idea.

## Usage examples

### Generate C++ code from Python code

#### Python code
```python
var_count = Variable(name='count', type='int', initialilization_value=0)
var_pi = Variable(name='pi', type='float', initialization_value=3.14)
var_title = Variable(name='title', type='const char *', initialization_value='Title:')

var_name = Variable(name='name', type='std::string', initialization_value='John Doe')
fn_getname = Function(name='GetName', ret_type='std::string', is_const=True)
fn_setname = Function(name='SetName', args='std::string & name')

cls_person = Class(name='Person', type='Person')
cls_person.add_member(var_name)
cls_person.add_method(fn_getname)
cls_person.add_method(fn_setname)

header = DeclarationFile('Person.h')
source = DefinitionFile('Person.cpp')

// TODO
```

#### Generated C++ code
```c++
int i = 0;
static constexpr int const& x = 42;
extern char* name;
```

[top](#code-generator)

#### Creating functions

##### Python code
```python
def handle_to_factorial(self, cpp):
    cpp('return n < 1 ? 1 : (n * factorial(n - 1));')

cpp = CodeFile('example.cpp')

factorial_function = CppFunction(name='factorial',
    ret_type='int',
    is_constexpr=True,
    implementation_handle=handle_to_factorial,
    documentation='/// Calculates and returns the factorial of \p n.')
factorial_function.add_argument('int n')
factorial_function.render_to_string(cpp)
```

##### Generated C++ code
```c++
/// Calculates and returns the factorial of \p n.
constexpr int factorial(int n)
{
    return n <= 1 ? 1 : (n * factorial(n - 1));
}
```

[top](#code-generator)

#### Creating classes and structures

##### Python code
```python
cpp = CppFile('example.cpp')
with cpp.block('class A', ';'):
    cpp.label('public:')
    cpp('int m_classMember1;')
    cpp('double m_classMember2;')
```

##### Generated C++ code
```c++
class A
{
public:
    int m_classMember1;
    double m_classMember2;
};
```

[top](#code-generator)

#### Rendering `CppClass` objects to C++ declaration and implementation

##### Python code

```python
cpp_class = CppClass(name = 'MyClass', is_struct = True)
cpp_class.add_variable(CppVariable(name = "m_var",
    type = 'size_t',
    is_static = True,
    is_const = True,
    initialization_value = 255))
```
 
##### Generated C++ declaration

```c++
struct MyClass
{
    static const size_t m_var;
}
```
 
#### Generated C++ implementation
```c++
const size_t MyClass::m_var = 255;
```

Module `cpp_generator.py` highly depends on parent `code_generator.py`, as it uses
code generating and formatting primitives implemented there.
 
The main object referenced from `code_generator.py` is `CppFile`, 
which is passed as a parameter to `render_to_string(cpp)` Python method

It could also be used for composing more complicated C++ code,
that does not supported by `cpp_generator`

Class `ANSICodeStyle` is responsible for code formatting. Re-implement it if you wish to apply any other formatting style.
 
 
It support:

- functional calls:
```python
cpp('int a = 10;')
```
 
- `with` semantic:
```python
with cpp.block('class MyClass', ';')
    class_definition(cpp)
```
 
- append code to the last string without EOL:
```python
cpp.append(', p = NULL);')
```
 
- empty lines:
```python
cpp.newline(2)
```

[top](#code-generator)

## Maintainers

See [DEVELOPERS.md](./DEVELOPERS.md)

[top](#code-generator)
