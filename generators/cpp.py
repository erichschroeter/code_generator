from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, List, Optional

@dataclass
class Qualifier:
    """Represents a C++ qualifier keyword, and follows the decorator pattern to allow chaining."""
    
    decorator: Optional['Qualifier']
    keyword: str
    
    def __call__(self):
        return f"{self.keyword} {self.decorator.keyword}" if self.decorator else f"{self.keyword}"


class Static(Qualifier):
    
    def __init__(self, decorator=None):
        super().__init__(keyword='static', decorator=decorator)


class Inline(Qualifier):
    
    def __init__(self, decorator=None):
        super().__init__(keyword='inline', decorator=decorator)


class Volatile(Qualifier):
    
    def __init__(self, decorator=None):
        super().__init__(keyword='volatile', decorator=decorator)


class Virtual(Qualifier):
    
    def __init__(self, decorator=None):
        super().__init__(keyword='virtual', decorator=decorator)


class Const(Qualifier):
    
    def __init__(self, decorator=None):
        super().__init__(keyword='const', decorator=decorator)


class Constexpr(Qualifier):
    
    def __init__(self, decorator=None):
        super().__init__(keyword='constexpr', decorator=decorator)


class Extern(Qualifier):
    
    def __init__(self, decorator=None):
        super().__init__(keyword='extern', decorator=decorator)


def is_const(qualifier: Qualifier) -> bool:
    if isinstance(qualifier, Const):
        return True
    if qualifier and qualifier.decorator:
        return is_const(qualifier.decorator)
    return False


def is_constexpr(qualifier: Qualifier) -> bool:
    if isinstance(qualifier, Constexpr):
        return True
    if qualifier and qualifier.decorator:
        return is_constexpr(qualifier.decorator)
    return False


# TODO move CppDeclaration here
# TODO move CppImplementation here
# TODO move CppLanguageElement here
# TODO move CppFunction here
# TODO move CppEnum here
# TODO move CppVariable here
# TODO move CppArray here
# TODO move CppClass here

# TODO refactor CppLanguageElement to a dataclass
# TODO refactor CppLanguageElement to accept a CppDeclaration using strategy pattern
# TODO refactor CppLanguageElement to accept a CppImplementation using strategy pattern


@dataclass
class CppLanguageElement(ABC):
    """The base class for all C++ language elements."""

    name: str = ''
    docs: Optional[str] = None
    ref_to_parent: Optional['CppLanguageElement'] = None
    

    def __post_init__(self):
        if not self.name:
            raise ValueError("CppElement.name cannot be empty")


    @abstractmethod
    def declaration(self) -> str:
        pass

    # @abstractmethod
    # def definition(self) -> str:
    #     pass


@dataclass
class Variable(CppLanguageElement):
    """The Python class that contains data for a C++ variable. """

    type: str = ''
    scope: Optional[str] = None
    qualifier: Optional[Qualifier] = None
    init_value: Optional[str] = None
    

    def __post_init__(self):
        if not self.type:
            raise ValueError("CppElement.type cannot be empty")
    

    def declaration(self) -> str:
        return f"{self.qualifier() + ' ' if self.qualifier else ''}{self.type} {self.name}{' = ' if self.init_value else ''}{self.init_value if self.init_value else ''};"


@dataclass
class Function(CppLanguageElement):
    """
    The Python class that contains data for a C++ function or method
    Parameters are passed as plain strings('int a', 'void p = NULL' etc)
    """

    return_type: str = ''
    scope: Optional[str] = None
    qualifier: Optional[Qualifier] = None
    # is_pure: bool
    implementation_handle: Optional[Callable] = None
    args: Optional[List[str]] = None
    

    def add_argument(self, argument):
        """Appends the argument to the list of function arguments."""
        self.args.append(argument)


    # def __init__(self, name: str, type: str, qualifier: Optional[Qualifier] = None, init_value: Optional[str] = None):
    #     pass

    # def __post_init__(self):
    #     if self.is_const and self.is_constexpr:
    #         raise RuntimeError(
    #             "Variable object can be either 'const' or 'constexpr', not both")
    #     if self.is_constexpr and not self.initialization_value:
    #         raise RuntimeError(
    #             "Variable object must be initialized when 'constexpr'")
    #     if self.is_static and self.is_extern:
    #         raise RuntimeError(
    #             "Variable object can be either 'extern' or 'static', not both")


@dataclass
class Indentation:
    """Represents the indentation level when writing code."""

    level: int = 0
    whitespace: str = '\t'
    
    def indent(self, text: str) -> str:
        if self.level < 1:
            return text
        whitespace = [''.join(self.whitespace) for _i in range(self.level)]
        return f"{''.join(whitespace)}{text}"
    

@dataclass
class CppCodeGenerator(ABC):
    """Generates C++ code for a CppLanguageElement."""
    
    cpp_element: CppLanguageElement

    @abstractmethod
    def code(self, indentation=None) -> str:
        """Generates C++ code."""
        pass


class CppDeclaration(CppCodeGenerator):
    """
    Isolates code generation to a C++ declaration.

    e.g. Function declaration

    int GetItem();
    """

    def code(self, indentaton=None) -> str:
        """Generates C++ declaration code."""
        pass


class CppDefinition(CppCodeGenerator):
    """
    Isolates code generation to a C++ definition.

    e.g. Method definition

    int GetItem() {...}
    """

    def code(self, indentaton=None) -> str:
        """Generates C++ definition code."""
        pass


def simple_variable_decl_def(cpp_element: Variable, indentation=None) -> str:
    qualifier = cpp_element.qualifier() + ' ' if cpp_element.qualifier else ''
    # scope = cpp_element.ref_to_parent.name + '::' if cpp_element.ref_to_parent else ''
    lhs = f"{qualifier}{cpp_element.type} {cpp_element.name}"
    code = f"{lhs};"
    if cpp_element.init_value and ( is_const(cpp_element.qualifier) or is_constexpr(cpp_element.qualifier) ):
        code = f"{lhs}{' = ' if cpp_element.init_value else ''}{cpp_element.init_value if cpp_element.init_value else ''};"
    if indentation:
        return indentation.indent(code)
    else:
        return code


class VariableDeclaration(CppDeclaration):
    
    def __init__(self, cpp_element: Variable):
        self.cpp_element = cpp_element


    def code(self, indentation=None) -> str:
        return simple_variable_decl_def(self.cpp_element, indentation)


class VariableDefinition(CppDefinition):
    
    def __init__(self, cpp_element: Variable):
        self.cpp_element = cpp_element

    def code(self, indentation=None) -> str:
        return simple_variable_decl_def(self.cpp_element, indentation)


class VariableConstructorDefinition(CppDefinition):
    """
    Generates constructor definition C++ code for a Variable.
    
    e.g. Constructor initialization
    SomeClass(int value) :
    a(value)
    {
    }
    """
    
    def __init__(self, cpp_element: Variable):
        self.cpp_element = cpp_element

    def code(self, indentation=None) -> str:
        value = self.cpp_element.init_value if self.cpp_element.init_value else ''
        code = f"{self.cpp_element.name}({value})"
        if indentation:
            return indentation.indent(code)
        else:
            return code

