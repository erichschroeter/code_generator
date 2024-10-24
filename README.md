# Code Generator

- [Code Generator](#code-generator)
  - [Usage examples](#usage-examples)
    - [C++ Variables](#c-variables)
    - [C++ Functions](#c-functions)
    - [C++ Classes and Structures](#c-classes-and-structures)
  - [Maintainers](#maintainers)

Simple and straightforward code generator for creating C++ code.
It also could be used for generating code in any programming language.

Every C++ element could render its current state to a string that could be evaluated as a legal C++ construction.
Some elements could be rendered to a pair of representations (C++ classes and functions declaration and implementation)

## Usage examples

### C++ Variables
Python code:
```python
var_count = Variable(name='count', type='int').val(0)
var_pi = Variable(name='pi', type='float').val(3.14)
var_title = Variable(name='title', type='const char *').val('Title:')

source = Source('main.cpp').add(var_count).add(var_pi).add(var_title)
str(source)
```

Generated C++ code:
```c++
int i = 0;
static constexpr int const& x = 42;
extern char* name;
```

[top](#code-generator)

### C++ Functions
Python code:
```python
def factorial_definition():
  return 'return n < 1 ? 1 : (n * factorial(n - 1));'

factorial_function = Function(name='factorial', type='int')
  .arg('int n')
  .impl(factorial_definition)

source = Source('main.cpp').add(factorial_function)
str(source)
```

Generated C++ code:
```c++
int factorial(int n)
{
    return n <= 1 ? 1 : (n * factorial(n - 1));
}
```

[top](#code-generator)

### C++ Classes and Structures
Python code:
```python
var_name = Variable(name='name', type='std::string')
fn_getname = Function(name='GetName', type='std::string', qualifiers=['const']).impl('return name;')
fn_setname = Function(name='SetName').arg('std::string & new_name').impl('name = new_name;')

cls_person = Class(name='Person')
  .member(var_name, scope='private')
  .method(fn_getname, scope='public')
  .method(fn_setname, scope='public')

header = Header('Person.h').add(cls_person)
source = Source('Person.cpp').include(header).add(cls_person)
str(header)
str(source)
```
Generated C++ code for `Person.h`:
```c++
class Person
{
public:
    std::string GetName() const;
    void SetName(std::string & name);
private:
    std::string name;
};
```
Generated C++ code for `Person.cpp`:
```c++
std::string Person::GetName() const
{
    return name;
}

void Person::SetName(std::string & new_name)
{
    name = new_name;
}
```

[top](#code-generator)

## Maintainers

See [DEVELOPERS.md](./DEVELOPERS.md)

[top](#code-generator)
