from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from io import IOBase, StringIO
from typing import Callable, List, Optional, Type


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


class Pure(Qualifier):

    def __init__(self, decorator=None):
        super().__init__(keyword='= 0', decorator=decorator)


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


# TODO move CppEnum here
# TODO move CppArray here
# TODO move CppClass here
@dataclass
class CppLanguageElement(ABC):
    """The base class for all C++ language elements."""

    name: str = ''
    docs: Optional[str] = None
    ref_to_parent: Optional['CppLanguageElement'] = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("CppElement.name cannot be empty")


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


@dataclass
class Function(CppLanguageElement):
    """
    The Python class that contains data for a C++ function or method
    Parameters are passed as plain strings('int a', 'void p = NULL' etc)
    """

    return_type: Optional[str] = None
    scope: Optional[str] = None
    qualifier: Optional[Qualifier] = None
    postfix_qualifier: Optional[Qualifier] = None
    implementation_handle: Optional[Callable[..., str]] = None
    args: Optional[List[str]] = None

    def with_arg(self, argument) -> 'Function':
        """Appends the argument to the list of function arguments."""
        if not self.args:
            self.args = []
        self.args.append(argument)
        return self


@dataclass
class Class(CppLanguageElement):
    """The Python class that contains data for a C++ class."""

    members: Optional[List[Variable]] = None
    methods: Optional[List[Function]] = None

    def with_member(self, member: Variable) -> 'Class':
        """Appends the member to the list of class members."""
        if not self.members:
            self.members = []
        self.members.append(member)
        return self

    def with_method(self, function: Function) -> 'Class':
        """Appends the function to the list of class methods."""
        if not self.methods:
            self.methods = []
        self.methods.append(function)
        return self


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
    if cpp_element.init_value and (is_const(cpp_element.qualifier) or is_constexpr(cpp_element.qualifier)):
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


@dataclass
class BraceStrategy(ABC):

    writer: IOBase = StringIO()
    indentation: Indentation = Indentation()
    postfix: Optional[str] = None
    is_ended_with_newline: bool = False

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, *_):
        if not self.is_ended_with_newline:
            self.writer.write('\n')

    def write(self, data):
        if data:
            self.writer.write(data)
            self.is_ended_with_newline = data[-1] == '\n'


class AllmanStyle(BraceStrategy):
    """
    Braces are put on their own line.
    see https://en.wikipedia.org/wiki/Indentation_style#Allman_style

    e.g. 
    while (x == y)
    {
        something();
        somethingelse();
    }
    """

    def __enter__(self):
        """Open code block."""
        self.writer.write(f"\n{self.indentation.indent('{')}\n")
        self.indentation.level += 1
        return self

    def __exit__(self, *_):
        """Close code block."""
        super().__exit__(self, *_)
        self.writer.write(f"}}{self.postfix if self.postfix else ''}")


class KnRStyle(BraceStrategy):
    """
    Braces are put on same line as function.
    see https://en.wikipedia.org/wiki/Indentation_style#K&R_style

    e.g. 
    while (x == y) {
        something();
        somethingelse();
    }
    """

    def __enter__(self):
        """Open code block."""
        self.writer.write(" {\n")
        self.is_ended_with_newline = True
        return self

    def __exit__(self, *_):
        """Close code block."""
        super().__exit__(self, *_)
        self.writer.write(f"}}{self.postfix if self.postfix else ''}")


@dataclass
class CodeStyleFactory:

    code_style: Type[BraceStrategy]

    def __call__(self, stream: IOBase = None, indentation: Indentation = None, postfix: str = None) -> BraceStrategy:
        writer = stream if stream else StringIO()
        indentation = indentation if indentation else Indentation()
        postfix = postfix if postfix else ''
        return self.code_style(writer=writer, indentation=indentation, postfix=postfix)


class FunctionDeclaration(CppDeclaration):

    def code(self, indentation=None) -> str:
        qualifier = self.cpp_element.qualifier() + ' ' if self.cpp_element.qualifier else ''
        # scope = self.cpp_element.ref_to_parent.name + '::' if self.cpp_element.ref_to_parent else ''
        return_type = self.cpp_element.return_type if self.cpp_element.return_type else 'void'
        lhs = f"{qualifier}{return_type} {self.cpp_element.name}"
        args = ', '.join(
            self.cpp_element.args) if self.cpp_element.args else ''
        postfix_qualifier = ' ' + \
            self.cpp_element.postfix_qualifier() if self.cpp_element.postfix_qualifier else ''
        code = f"{lhs}({args}){postfix_qualifier};"
        if indentation:
            return indentation.indent(code)
        else:
            return code


@dataclass
class FunctionDefinition(CppDefinition):

    brace_strategy: Type[BraceStrategy] = KnRStyle

    def function_prototype(self) -> str:
        qualifier = self.cpp_element.qualifier() + ' ' if self.cpp_element.qualifier else ''
        # scope = self.cpp_element.ref_to_parent.name + '::' if self.cpp_element.ref_to_parent else ''
        return_type = self.cpp_element.return_type if self.cpp_element.return_type else 'void'
        lhs = f"{qualifier}{return_type} {self.cpp_element.name}"
        args = ', '.join(
            self.cpp_element.args) if self.cpp_element.args else ''
        postfix_qualifier = ' ' + \
            self.cpp_element.postfix_qualifier() if self.cpp_element.postfix_qualifier else ''
        return f"{lhs}({args}){postfix_qualifier}"

    def function_definition(self, indentation=None) -> str:
        code = self.cpp_element.implementation_handle(
        ) if self.cpp_element.implementation_handle else None
        indentation = indentation if indentation else Indentation()
        indentation.level += 1
        lines = [indentation.indent(line)
                 for line in code.split('\n')] if code else []
        code = '\n'.join(lines)
        # reset indentation level to prior value upon entering this function
        indentation.level -= 1
        return code

    def code(self, indentation=None) -> str:
        code = StringIO()
        code.write(self.function_prototype())
        style = CodeStyleFactory(self.brace_strategy)
        with style(code, indentation) as os:
            os.write(self.function_definition(indentation=indentation))
        code = code.getvalue()
        if indentation:
            return indentation.indent(code)
        else:
            return code


@dataclass
class ClassDeclaration(CppDeclaration):

    brace_strategy: BraceStrategy = KnRStyle()

    def code(self, indentation=None) -> str:
        code = f"class {self.cpp_element.name}"
        if indentation:
            return indentation.indent(code)
        else:
            return code
