from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum as PythonEnum, auto
from io import IOBase, StringIO
from typing import Callable, List, Optional, Tuple, Type
from .docs import Docs


class CppStandard(PythonEnum):
    CPP_03 = (0, 'C++03')
    CPP_11 = (1, 'C++11')

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value[0] < other.value[0]
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value[0] > other.value[0]
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value[0] <= other.value[0]
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value[0] >= other.value[0]
        return NotImplemented

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


def is_static(qualifier: Qualifier) -> bool:
    if isinstance(qualifier, Static):
        return True
    if qualifier and qualifier.decorator:
        return is_static(qualifier.decorator)
    return False


class Visibility(PythonEnum):
    """Supported C++ class access specifiers."""
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    PUBLIC = auto()
    PRIVATE = auto()
    PROTECTED = auto()


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
class CppDocs(Docs):

    cpp_element: CppLanguageElement


class VerbatimAboveDocs(CppDocs):
    """
    Returns the value of the 'docs' attribute on a CppLanguageElement or empty string if None.

    ```
    /// Example documentation for variable a.
    int a = 0;
    ```
    """

    def docs(self, attachment: str) -> str:
        docs = self.cpp_element.docs if self.cpp_element.docs else ''
        newline = '\n' if docs and attachment else ''
        attachment = attachment if attachment else ''
        return f"{docs}{newline}{attachment}"


class VerbatimSameLineDocs(CppDocs):
    """
    Returns the value of the 'docs' attribute on a CppLanguageElement or empty string if None.

    ```
    int a = 0; // Example documentation for variable a.
    ```
    """

    def docs(self, attachment: str) -> str:
        docs = self.cpp_element.docs if self.cpp_element.docs else ''
        attachment = attachment if attachment else ''
        return f"{attachment}{docs}"


@dataclass
class DocsFactory:

    docs_generator: Type[CppDocs]

    def __call__(self, element: CppLanguageElement) -> CppDocs:
        return self.docs_generator(element)


@dataclass
class Namespace(CppLanguageElement):
    pass


@dataclass
class Variable(CppLanguageElement):
    """The Python class that contains data for a C++ variable. """

    type: str = ''
    qualifier: Optional[Qualifier] = None
    init_value: Optional[str] = None

    def __post_init__(self):
        if not self.type:
            raise ValueError("CppElement.type cannot be empty")


def is_integral(type: str) -> bool:
    return type in ['int', 'long', 'size_t']

class DefaultValueFactory:
    """Factory class to support getting default values for known C++ types."""

    def default_value(self, element: Variable) -> str:
        if element.init_value:
            return element.init_value
        elif is_integral(element.type):
            return '0'
        elif 'string' in element.type or 'char' in element.type:
            return '""'
        elif 'float' in element.type or 'double' in element.type:
            return '0.0'
        raise ValueError(
            f"Cannot determine default init value for '{element.name}' of type: {element.type}")


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
    args: Optional[List[Tuple[str, str]]] = None
    """
    Optional list of tuple of args with its potential default value.
    Arg default values are defaulted to `None` if not specified.
    """
    context: Optional[object] = None
    """
    An object that will be passed to the implementation_handle.
    """

    def __post_init__(self):
        super().__post_init__()
        if not self.args is None:
            if not isinstance(self.args, List):
                raise ValueError(f"attribute 'args' must be tuple (str, str)")
            if len(self.args) > 0 and not isinstance(self.args[0], Tuple):
                raise ValueError(f"attribute 'args' must be tuple (str, str)")
            if len(self.args[0]) < 2:
                raise ValueError(f"attribute 'args' must be tuple (str, str)")

    def with_arg(self, argument, default_value=None) -> 'Function':
        """Appends the argument to the list of function arguments."""
        if not self.args:
            self.args = []
        self.args.append((argument, default_value))
        return self


@dataclass
class Enum(CppLanguageElement):
    """The Python class that generates string representation for C++ enum."""

    prefix: str = ''
    items: Optional[List[Tuple[str, str]]] = None

    def add(self, item: str, value: str = None) -> 'Enum':
        """
        Appends the item to the list of enum items.
        """
        if not self.items:
            self.items = []
        self.items.append((item, value))
        return self


@dataclass
class Array(Variable):
    """The Python class that generates string representation for C++ array."""

    type: str = ''
    qualifier: Optional[Qualifier] = None
    items: Optional[List[str]] = None
    size_ref: Optional[Variable] = None
    """Optional Variable reference to use as the array size."""

    def __post_init__(self):
        if not self.type:
            raise ValueError("CppElement.type cannot be empty")

    def add(self, item: str) -> 'Array':
        """
        Appends the item to the list of array items.
        """
        if not self.items:
            self.items = []
        self.items.append(item)
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
class Struct(Class):
    """The Python class that contains data for a C++ struct."""

    def add(self, element: CppLanguageElement, visibility=Visibility.PUBLIC) -> 'Struct':
        return super().add(element, visibility)


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
    docs_generator: Type[CppDocs] = VerbatimAboveDocs
    cpp_standard: CppStandard = CppStandard.CPP_11

    @abstractmethod
    def code(self, indentation=None) -> str:
        """Generates C++ code."""
        pass

    def docs(self, indentation=None) -> str:
        """Returns documentation without the code itself."""
        return DocsFactory(self.docs_generator)(self.cpp_element).docs(None)

    def code_with_docs(self, indentation=None) -> str:
        """Returns documentation paired with its documentation."""
        return DocsFactory(self.docs_generator)(self.cpp_element).docs(self.code())


class CppDeclaration(CppCodeGenerator):
    """
    Isolates code generation to a C++ declaration.

    e.g. Function declaration

    int GetItem();
    """

    @abstractmethod
    def code(self, indentaton=None) -> str:
        """Generates C++ declaration code."""
        pass


class CppDefinition(CppCodeGenerator):
    """
    Isolates code generation to a C++ definition.

    e.g. Method definition

    int GetItem() {...}
    """

    @abstractmethod
    def code(self, indentaton=None) -> str:
        """Generates C++ definition code."""
        pass


def reduce_qualifiers(qualifier: Qualifier, exclude: List[Type[Qualifier]]) -> Qualifier:
    """
    Recursive function returning qualifier with the excluded Qualifier types omitted.
    """
    if not qualifier:
        return qualifier
    if qualifier.decorator:
        qualifier.decorator = reduce_qualifiers(qualifier.decorator, exclude)
    if type(qualifier) in exclude:
        return qualifier.decorator
    return qualifier


def build_scope(cpp_element: CppLanguageElement) -> str:
    """Recursively travels up the ref_to_parent to generate the scope."""
    if not cpp_element.ref_to_parent:
        return ''
    scope = cpp_element.ref_to_parent.name + '::'
    parent_scope = build_scope(cpp_element.ref_to_parent)
    if parent_scope:
        return parent_scope + scope
    else:
        return scope


def variable_prototype(cpp_element: Variable, use_ref_to_parent=False, exclude: List[Type[Qualifier]] = None) -> str:
    """
    Returns a variable with its qualifiers, type, and name.

    ```
    const int x
    const int MyClass::x
    ```
    """
    qualifier = cpp_element.qualifier
    if exclude:
        # Don't want to modify cpp_element's qualifier
        qualifier_copy = deepcopy(cpp_element.qualifier)
        qualifier = reduce_qualifiers(qualifier_copy, exclude)
    qualifier = qualifier() + ' ' if qualifier else ''
    scoped_name = f"{build_scope(cpp_element)}{cpp_element.name}" if use_ref_to_parent and cpp_element.ref_to_parent else cpp_element.name
    return f"{qualifier}{cpp_element.type} {scoped_name}"


class VariableDeclaration(CppDeclaration):
    """
    Generates a variable declaration.

    ```
    int x;
    ```
    """

    def is_assignable(self, cpp_element: CppLanguageElement) -> bool:
        if is_constexpr(cpp_element.qualifier):
            if cpp_element.init_value:
                return True
            raise ValueError(
                f"constexpr requires init_value to be assigned: '{cpp_element}'")
        if isinstance(cpp_element.ref_to_parent, Class) and is_static(cpp_element.qualifier):
            if is_integral(cpp_element.type) and is_const(cpp_element.qualifier):
                return True
            return False
        return cpp_element.init_value and is_const(self.cpp_element.qualifier)

    def code(self, indentation=None) -> str:
        if self.is_assignable(self.cpp_element):
            return f"{variable_prototype(self.cpp_element, use_ref_to_parent=False)} = {DefaultValueFactory().default_value(self.cpp_element)};"
        return f"{variable_prototype(self.cpp_element)};"


class VariableDefinition(CppDefinition):
    """
    Generates a variable definition.

    ```
    int x = 0;
    ```
    """

    def is_class_member(self, cpp_element: CppLanguageElement) -> bool:
        return isinstance(cpp_element.ref_to_parent, Class) and is_static(cpp_element.qualifier)

    def code(self, indentation=None) -> str:
        if self.cpp_element.init_value:
            return f"{variable_prototype(self.cpp_element, use_ref_to_parent=True, exclude=[Static])} = {self.cpp_element.init_value};"
        return f"{variable_prototype(self.cpp_element, use_ref_to_parent=True, exclude=[Static])} = {DefaultValueFactory().default_value(self.cpp_element)};"


class VariableConstructorDefinition(CppDefinition):
    """
    Generates a constructor definition C++ code for a Variable.

    ```
    my_var(0)
    ```
    """

    def code(self, indentation=None) -> str:
        value = self.cpp_element.init_value if self.cpp_element.init_value else ''
        return f"{self.cpp_element.name}({value})"


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
        self.writer.write(self.indentation.indent(
            f"}}{self.postfix if self.postfix else ''}"))

    def __call__(self, data):
        self.write(data)

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


class SingleLineStyle(BraceStrategy):
    """
    Opening and closing braces are put on same line.

    e.g. 
    { 0, "", 2 }
    """

    def __enter__(self):
        """Open code block."""
        self.writer.write("{")
        return self

    def __exit__(self, *_):
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
    """
    Generates a function declaration.

    ```
    int Foo();
    ```
    """

    def function_return_type(self) -> str:
        return self.cpp_element.return_type if self.cpp_element.return_type else 'void'

    def code(self, indentation=None) -> str:
        qualifier = self.cpp_element.qualifier() + ' ' if self.cpp_element.qualifier else ''
        return_type = self.function_return_type()
        return_type = return_type + ' ' if return_type else ''
        lhs = f"{qualifier}{return_type}{self.cpp_element.name}"
        args = []
        if self.cpp_element.args:
            for (arg, default_value) in self.cpp_element.args:
                assignment = f" = {default_value}" if default_value else ''
                args.append(f"{arg}{assignment}")
        args = ', '.join(args) if args else ''
        postfix_qualifier = ' ' + \
            self.cpp_element.postfix_qualifier() if self.cpp_element.postfix_qualifier else ''
        return f"{lhs}({args}){postfix_qualifier};"


@dataclass
class FunctionDefinition(CppDefinition):
    """
    Generates a function definition.

    ```
    int foo() {
        return 0;
    }
    ```
    """

    brace_strategy: Type[BraceStrategy] = KnRStyle

    def function_return_type(self) -> str:
        return self.cpp_element.return_type if self.cpp_element.return_type else 'void'

    def function_prototype(self) -> str:
        scope = build_scope(self.cpp_element)
        return_type = self.function_return_type()
        lhs = f"{return_type + ' ' if return_type else ''}{scope}{self.cpp_element.name}"
        args = [arg for (arg, _default_value)
                in self.cpp_element.args if self.cpp_element.args] if self.cpp_element.args else []
        args = ', '.join(args) if args else ''
        postfix_qualifier = ' ' + \
            self.cpp_element.postfix_qualifier() if self.cpp_element.postfix_qualifier else ''
        return f"{lhs}({args}){postfix_qualifier}"

    def function_definition(self, indentation=None) -> str:
        if self.cpp_element.context:
            return self.cpp_element.implementation_handle(self.cpp_element.context) if self.cpp_element.implementation_handle else None
        return self.cpp_element.implementation_handle() if self.cpp_element.implementation_handle else None

    def code(self, indentation=None) -> str:
        code = StringIO()
        code.write(self.function_prototype())
        style = CodeStyleFactory(self.brace_strategy)
        with style(code, indentation) as os:
            os.write_lines(self.function_definition(indentation=indentation))
        code = code.getvalue()
        return code


@dataclass
class ConstructorDeclaration(FunctionDeclaration):

    def function_return_type(self) -> str:
        return None


@dataclass
class ConstructorInitializerFactory:

    cpp_standard: CppStandard

    def build(self, cpp_element: CppLanguageElement) -> CppDefinition:
        if isinstance(cpp_element, Array):
            return ArrayConstructorDefinition(cpp_element, cpp_standard=self.cpp_standard)
        return VariableConstructorDefinition(cpp_element, cpp_standard=self.cpp_standard)


@dataclass
class ConstructorDefinition(FunctionDefinition):
    """
    Generates a constructor definition.

    ```
    Foo::Foo() :
    x(0),
    y(0) {
    }
    ```
    """

    initializer_factory: ConstructorInitializerFactory = field(init=False)
    
    def __post_init__(self):
        self.initializer_factory = ConstructorInitializerFactory(self.cpp_standard)

    def function_return_type(self) -> str:
        """Returns None since constructors don't have a return type."""
        return None

    def is_initializable(self, cpp_element: CppLanguageElement) -> bool:
        if not isinstance(cpp_element, Variable):
            return False
        elif is_static(cpp_element.qualifier):
            return False
        elif is_constexpr(cpp_element.qualifier):
            return False
        return True

    def initializer_list(self, indentation=None) -> List[str]:
        items = None
        if self.cpp_element.ref_to_parent:
            items = [self.initializer_factory.build(e).code(
            ) for e, _v in self.cpp_element.ref_to_parent.elements if self.is_initializable(e)]
        return items

    def code(self, indentation=None) -> str:
        code = StringIO()
        code.write(self.function_prototype())
        initializer_list = self.initializer_list()
        if initializer_list:
            code.write(' :\n')
            code.write(',\n'.join(initializer_list))
        style = CodeStyleFactory(self.brace_strategy)
        with style(code, indentation) as os:
            os.write_lines(self.function_definition(indentation=indentation))
        code = code.getvalue()
        return code


@dataclass
class EnumDeclaration(CppDeclaration):
    """
    Generates an enum declaration.

    ```
    enum Color {
            RED,
            GREEN,
            BLUE
    };
    ```
    """

    brace_strategy: Type[BraceStrategy] = KnRStyle

    def enum_prototype(self) -> str:
        return f"enum {self.cpp_element.name}"

    def enum_definition(self, output_stream, indentation=None) -> str:
        lines = []
        if self.cpp_element.items:
            for name, value in self.cpp_element.items:
                name = name if not self.cpp_element.prefix else f"{self.cpp_element.prefix}{name}"
                value = f" = {value}" if value is not None else ''
                lines.append(f"{name}{value}")
        return ',\n'.join(lines)

    def code(self, indentation=None) -> str:
        code = StringIO()
        code.write(self.enum_prototype())
        style = CodeStyleFactory(self.brace_strategy)
        with style(code, indentation, ';') as os:
            os.write_lines(self.enum_definition(os, indentation))
        code = code.getvalue()
        return code


@dataclass
class ArrayDeclaration(VariableDeclaration):
    """
    Generates an array declaration.
    If `size_ref` is not `None` then the name will be used to declare the array size.

    ```
    int my_array[0];
    int my_array[COUNT];
    ```
    """

    def code(self, indentation=None) -> str:
        qualifier = self.cpp_element.qualifier() + ' ' if self.cpp_element.qualifier else ''
        lhs = f"{qualifier}{self.cpp_element.type} {self.cpp_element.name}"
        size = self.cpp_element.size_ref.name if self.cpp_element.size_ref else len(
            self.cpp_element.items) if self.cpp_element.items else 0
        return f"{lhs}[{size}];"


@dataclass
class StdArrayDeclaration(VariableDeclaration):
    """
    Generates a standard library array declaration.
    If `size_ref` is not `None` then the name will be used to declare the array size.

    ```
    std::array<int, 0> my_array;
    std::array<int, COUNT> my_array;
    ```
    """

    def code(self, indentation=None) -> str:
        qualifier = self.cpp_element.qualifier() + ' ' if self.cpp_element.qualifier else ''
        size = self.cpp_element.size_ref.name if self.cpp_element.size_ref else len(
            self.cpp_element.items) if self.cpp_element.items else 0
        return f"{qualifier}std::array<{self.cpp_element.type}, {size}> {self.cpp_element.name};"


@dataclass
class ArrayDefinition(CppDefinition):
    """
    Generates an array definition.

    ```
    int my_array[] = {
            0,
            1,
            2
    };
    ```
    """

    brace_strategy: Type[BraceStrategy] = KnRStyle

    def array_prototype(self, size='') -> str:
        return f"{variable_prototype(self.cpp_element, use_ref_to_parent=True, exclude=[Static])}[{size}]"

    def array_values(self, indentation=None) -> List[str]:
        lines = []
        if self.cpp_element.items:
            for item in self.cpp_element.items:
                lines.append(f"{item}")
        return lines

    def code(self, indentation=None) -> str:
        code = StringIO()
        code.write(self.array_prototype())
        code.write(' =')
        style = CodeStyleFactory(self.brace_strategy)
        with style(code, indentation, ';') as os:
            init_value = self.cpp_element.init_value
            if not init_value:
                init_value = ',\n'.join(self.array_values(indentation))
            os.write_lines(init_value)
        return code.getvalue()


@dataclass
class ArrayConstructorDefinition(ArrayDefinition):

    brace_strategy: Type[BraceStrategy] = SingleLineStyle

    def array_prototype(self, size='') -> str:
        return self.cpp_element.name

    def code(self, indentation=None) -> str:
        code = StringIO()
        code.write(self.array_prototype())
        style = CodeStyleFactory(self.brace_strategy)
        if self.cpp_standard >= CppStandard.CPP_11:
            with style(code, indentation) as os:
                init_value = self.cpp_element.init_value
                if not init_value:
                    init_value = ','.join(self.array_values(indentation))
                os.write(init_value)
        else:
            code.write('()')
        return code.getvalue()


@dataclass
class ClassCodeFactory:
    """Factory for creating declaration and definition instances."""

    name: str
    cpp_standard: CppStandard

    def build_declaration(self, element) -> CppDeclaration:
        """Returns a CppDeclaration for the given element."""
        if isinstance(element, Variable):
            if isinstance(element, Array):
                return ArrayDeclaration(element, self.cpp_standard) if self.cpp_standard < CppStandard.CPP_11 else StdArrayDeclaration(element, self.cpp_standard)
            return VariableDeclaration(element, self.cpp_standard)
        elif isinstance(element, Function):
            if element.name == self.name:
                return ConstructorDeclaration(element, self.cpp_standard)
            return FunctionDeclaration(element, self.cpp_standard)
        elif isinstance(element, Class):
            if isinstance(element, Struct):
                return StructDeclaration(element, self.cpp_standard)
            return ClassDeclaration(element, self.cpp_standard)
        elif isinstance(element, Enum):
            return EnumDeclaration(element, self.cpp_standard)
        raise ValueError(f"Unsupported declaration for element '{element}'")

    def build_definition(self, element) -> CppDefinition:
        """Returns a CppDeclaration for the given element."""
        if isinstance(element, Variable):
            if isinstance(element, Array):
                return ArrayDefinition(element, cpp_standard=self.cpp_standard)
            return VariableDefinition(element, cpp_standard=self.cpp_standard)
        elif isinstance(element, Function):
            if element.name == self.name:
                return ConstructorDefinition(element, cpp_standard=self.cpp_standard)
            return FunctionDefinition(element, cpp_standard=self.cpp_standard)
        elif isinstance(element, Class):
            if isinstance(element, Struct):
                return StructDefinition(element, cpp_standard=self.cpp_standard)
            return ClassDefinition(element, cpp_standard=self.cpp_standard)
        raise ValueError(f"Unsupported definition for element '{element}'")


@dataclass
class ClassDeclaration(CppDeclaration):

    brace_strategy: BraceStrategy = KnRStyle
    visibility: Visibility = Visibility.PRIVATE
    element_factory: ClassCodeFactory = field(init=False)

    def __post_init__(self):
        self.element_factory = ClassCodeFactory(name=self.cpp_element.name, cpp_standard=self.cpp_standard)

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
                    self.element_factory.build_declaration(member).code(indentation=indentation))
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


def is_translation_unit_element(cpp_element: CppLanguageElement) -> bool:
    if isinstance(cpp_element, Variable) and is_static(cpp_element.qualifier):
        if is_constexpr(cpp_element.qualifier):
            return False
        if is_const(cpp_element.qualifier) and is_integral(cpp_element.type):
            return False
        return True
    elif isinstance(cpp_element, Function):
        return True
    return False


def translation_unit_elements(cls: Class) -> List[CppLanguageElement]:
    """Recursivley aggregates all translation units in the given class."""
    units = []
    for e, _v in cls.elements:
        if isinstance(e, Class):
            units.extend(translation_unit_elements(e))
    units.extend([e for e, _v in cls.elements if is_translation_unit_element(e)])
    return units


@dataclass
class ClassDefinition(CppDefinition):

    brace_strategy: BraceStrategy = KnRStyle
    element_factory: ClassCodeFactory = field(init=False)

    def __post_init__(self):
        self.element_factory = ClassCodeFactory(name=self.cpp_element.name, cpp_standard=self.cpp_standard)

    def class_scope(self) -> str:
        return f"{self.cpp_element.name}::"

    def translation_unit_elements(self) -> List[CppLanguageElement]:
        return translation_unit_elements(self.cpp_element)

    def definitions(self, output_stream, indentation=None) -> None:
        if self.cpp_element.elements:
            style = CodeStyleFactory(self.brace_strategy)
            is_first_func = True
            translation_unit_elements = self.translation_unit_elements()
            for cpp_element in translation_unit_elements:
                if not is_first_func:
                    output_stream.write('\n')
                output_stream.write(
                    self.element_factory.build_definition(cpp_element).code())
                is_first_func = False

    def code(self, indentation=None) -> str:
        indentation = indentation if indentation else Indentation()
        code = StringIO()
        self.definitions(code, indentation)
        code = code.getvalue()
        return code


@dataclass
class ClassArrayInitializer(CppDefinition):

    brace_strategy: BraceStrategy = SingleLineStyle()

    def definitions(self, output_stream, indentation=None) -> None:
        style = CodeStyleFactory(self.brace_strategy)
        with style(output_stream, indentation) as os:
            members = []
            if self.cpp_element.elements:
                members = [
                    e for e, _v in self.cpp_element.elements if isinstance(e, Variable)]
            init_values = [member.init_value if member.init_value else DefaultValueFactory(
            ).default_value(member) for member in members]
            init_values = ', '.join(init_values)
            os.write(init_values)

    def code(self, indentation=None) -> str:
        indentation = indentation if indentation else Indentation()
        code = StringIO()
        self.definitions(code, indentation)
        code = code.getvalue()
        return code


@dataclass
class StructDeclaration(ClassDeclaration):

    visibility: Visibility = Visibility.PUBLIC

    def class_prototype(self) -> str:
        return f"struct {self.cpp_element.name}"


@dataclass
class StructDefinition(ClassDefinition):
    """A convenience class the same as ClassDefinition."""
    pass


@dataclass
class StructArrayInitializer(ClassArrayInitializer):
    """A convenience class the same as ClassArrayInitializer."""
    pass
