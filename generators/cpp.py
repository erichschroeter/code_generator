from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from io import IOBase, StringIO
from typing import Callable, List, Optional, Tuple, Type


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


class Visibility(Enum):
    """Supported C++ class access specifiers."""
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()


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

    elements: Optional[List[Tuple[CppLanguageElement, Visibility]]] = None
    parents: List[Tuple[str, Visibility]] = None

    def add(self, element: CppLanguageElement, visibility=Visibility.PRIVATE) -> 'Class':
        """
        Appends the element to the list of class elements, creating the list lazily.
        The element.ref_to_parent is set to this class.
        """
        if not self.elements:
            self.elements = []
        element.ref_to_parent = self
        self.elements.append((element, visibility))
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
        self.indentation.level += 1
        return self

    def __exit__(self, *_):
        self.indentation.level -= 1
        if not self.is_ended_with_newline:
            self.writer.write('\n')
        self.writer.write(f"}}{self.postfix if self.postfix else ''}")

    def write_line(self, line, enforce_newline=True):
        if line:
            self.writer.write(self.indentation.indent(line))
            self.is_ended_with_newline = line[-1] == '\n'
            if enforce_newline:
                if not line[-1] == '\n':
                    self.writer.write('\n')
                    self.is_ended_with_newline = True

    def write_lines(self, lines):
        if lines:
            lines = [self.indentation.indent(line)
                     for line in lines.split('\n')] if lines else []
            lines = [line + '\n' for line in lines]
            for line in lines:
                self.writer.write(line)
            self.is_ended_with_newline = lines[-1][-1] == '\n'

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
        # after writing the first indented brace since __enter__ increments indent level
        super().__enter__()
        self.is_ended_with_newline = True
        return self


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
        super().__enter__()
        self.writer.write(" {\n")
        self.is_ended_with_newline = True
        return self


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
        scope = self.cpp_element.ref_to_parent.name + \
            '::' if self.cpp_element.ref_to_parent else ''
        return_type = self.cpp_element.return_type if self.cpp_element.return_type else 'void'
        lhs = f"{qualifier}{return_type} {scope}{self.cpp_element.name}"
        args = ', '.join(
            self.cpp_element.args) if self.cpp_element.args else ''
        postfix_qualifier = ' ' + \
            self.cpp_element.postfix_qualifier() if self.cpp_element.postfix_qualifier else ''
        return f"{lhs}({args}){postfix_qualifier}"

    def function_definition(self, indentation=None) -> str:
        return self.cpp_element.implementation_handle() if self.cpp_element.implementation_handle else None

    def code(self, indentation=None) -> str:
        code = StringIO()
        code.write(self.function_prototype())
        style = CodeStyleFactory(self.brace_strategy)
        with style(code, indentation) as os:
            os.write_lines(self.function_definition(indentation=indentation))
        code = code.getvalue()
        return code


class CppLanguageElementFactory:
    """Factory for creating declaration and definition instances."""

    def build_declaration(self, element) -> CppDeclaration:
        """Returns a CppDeclaration for the given element."""
        if isinstance(element, Variable):
            return VariableDeclaration(element)
        elif isinstance(element, Function):
            return FunctionDeclaration(element)

    def build_definition(self, element) -> CppDefinition:
        """Returns a CppDeclaration for the given element."""
        if isinstance(element, Variable):
            return VariableDefinition(element)
        elif isinstance(element, Function):
            return FunctionDefinition(element)


@dataclass
class ClassDeclaration(CppDeclaration):

    brace_strategy: BraceStrategy = KnRStyle()
    visibility: Visibility = Visibility.PRIVATE
    factory: CppLanguageElementFactory = CppLanguageElementFactory()

    def class_prototype(self) -> str:
        return f"class {self.cpp_element.name}"

    def class_inheritance(self) -> str:
        parents = None
        if self.cpp_element.parents:
            parents = [f"{visibility.value} {name}" for name,
                       visibility in self.cpp_element.parents]
        return '' if not parents else f" : {', '.join(parents)}"

    def declarations(self, output_stream, indentation=None) -> None:
        if self.cpp_element.elements:
            last_visibility = self.visibility
            for member, member_visibility in self.cpp_element.elements:
                if not member_visibility == last_visibility:
                    indentation.level -= 1
                    output_stream.write_line(f'{member_visibility.value}:\n')
                    indentation.level += 1
                    last_visibility = member_visibility
                output_stream.write_line(
                    self.factory.build_declaration(member).code())
            self.visibility = last_visibility

    def code(self, indentation=None) -> str:
        indentation = indentation if indentation else Indentation()
        code = StringIO()
        code.write(self.class_prototype())
        code.write(self.class_inheritance())
        style = CodeStyleFactory(self.brace_strategy)
        with style(code, indentation, postfix=';') as os:
            self.declarations(os, indentation)
        code = code.getvalue()
        return code


@dataclass
class ClassDefinition(CppDefinition):

    brace_strategy: BraceStrategy = KnRStyle()
    factory: CppLanguageElementFactory = CppLanguageElementFactory()

    def class_scope(self) -> str:
        return f"{self.cpp_element.name}::"

    def definitions(self, output_stream, indentation=None) -> None:
        if self.cpp_element.elements:
            style = CodeStyleFactory(self.brace_strategy)
            functions = [
                e for e, _v in self.cpp_element.elements if isinstance(e, Function)]
            is_first_func = True
            for function in functions:
                if not is_first_func:
                    output_stream.write('\n')
                output_stream.write(
                    self.factory.build_definition(function).code())
                is_first_func = False

    def code(self, indentation=None) -> str:
        indentation = indentation if indentation else Indentation()
        code = StringIO()
        self.definitions(code, indentation)
        code = code.getvalue()
        return code
