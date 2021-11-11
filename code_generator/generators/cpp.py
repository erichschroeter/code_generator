from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum as PythonEnum, auto
from io import IOBase, StringIO
from typing import Callable, List, Optional, Tuple, Type
from .docs import Docs


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


class DefaultValueFactory:
    """Factory class to support getting default values for known C++ types."""
    
    def default_value(self, element: Variable) -> str:
        if element.init_value:
            return element.init_value
        if 'int' in element.type or 'long' in element.type:
            return '0'
        elif 'string' in element.type or 'char' in element.type:
            return '""'
        elif 'float' in element.type or 'double' in element.type:
            return '0.0'
        raise ValueError(f"Cannot determine default init value for '{element.name}' of type: {element.type}")


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
class Enum(CppLanguageElement):
    """The Python class that generates string representation for C++ enum."""
    
    prefix: str = ''
    items: Optional[List[Tuple[str, str]]] = None
    
    def add(self, item: str, value: str=None) -> 'Enum':
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


def variable_prototype(cpp_element: Variable, use_ref_to_parent=False) -> str:
    """
    Returns a variable with its qualifiers, type, and name.
    
    ```
    const int x
    const int MyClass::x
    ```
    """
    qualifier = cpp_element.qualifier() + ' ' if cpp_element.qualifier else ''
    scoped_name = f"{cpp_element.ref_to_parent.name}::{cpp_element.name}" if use_ref_to_parent and cpp_element.ref_to_parent else cpp_element.name
    return f"{qualifier}{cpp_element.type} {scoped_name}"


class VariableDeclaration(CppDeclaration):
    """
    Generates a variable declaration.
    
    ```
    int x;
    ```
    """

    def code(self, indentation=None) -> str:
        if is_const(self.cpp_element.qualifier) or is_constexpr(self.cpp_element.qualifier):
            if self.cpp_element.init_value:
                return f"{variable_prototype(self.cpp_element, False)} = {self.cpp_element.init_value};"
            return f"{variable_prototype(self.cpp_element, False)} = {DefaultValueFactory().default_value(self.cpp_element)};"
        return f"{variable_prototype(self.cpp_element)};"


class VariableDefinition(CppDefinition):
    """
    Generates a variable definition.
    
    ```
    int x = 0;
    ```
    """

    def code(self, indentation=None) -> str:
        if self.cpp_element.init_value:
            return f"{variable_prototype(self.cpp_element, True)} = {self.cpp_element.init_value};"
        return f"{variable_prototype(self.cpp_element, True)} = {DefaultValueFactory().default_value(self.cpp_element)};"


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
        self.writer.write(self.indentation.indent(f"}}{self.postfix if self.postfix else ''}"))

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

    def code(self, indentation=None) -> str:
        qualifier = self.cpp_element.qualifier() + ' ' if self.cpp_element.qualifier else ''
        return_type = self.cpp_element.return_type if self.cpp_element.return_type else 'void'
        lhs = f"{qualifier}{return_type} {self.cpp_element.name}"
        args = ', '.join(
            self.cpp_element.args) if self.cpp_element.args else ''
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
        qualifier = self.cpp_element.qualifier() + ' ' if self.cpp_element.qualifier else ''
        scope = self.cpp_element.ref_to_parent.name + \
            '::' if self.cpp_element.ref_to_parent else ''
        return_type = self.function_return_type()
        lhs = f"{qualifier}{return_type + ' ' if return_type else ''}{scope}{self.cpp_element.name}"
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

    def function_return_type(self) -> str:
        """Returns None since constructors don't have a return type."""
        return None

    def initializer_list(self, indentation=None) -> List[str]:
        items = None
        if self.cpp_element.ref_to_parent:
            members = [e for e, _v in self.cpp_element.ref_to_parent.elements if isinstance(e, Variable)]
            if members:
                items = [VariableConstructorDefinition(member).code() for member in members]
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
        size = self.cpp_element.size_ref.name if self.cpp_element.size_ref else len(self.cpp_element.items) if self.cpp_element.items else 0
        return f"{lhs}[{size}];"


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
        qualifier = self.cpp_element.qualifier() + ' ' if self.cpp_element.qualifier else ''
        return f"{qualifier}{self.cpp_element.type} {self.cpp_element.name}[{size}]"

    def array_definition(self, output_stream, indentation=None) -> str:
        lines = []
        if self.cpp_element.items:
            for item in self.cpp_element.items:
                lines.append(f"{item}")
        return ',\n'.join(lines)

    def code(self, indentation=None) -> str:
        code = StringIO()
        code.write(self.array_prototype())
        code.write(' =')
        style = CodeStyleFactory(self.brace_strategy)
        with style(code, indentation, ';') as os:
            os.write_lines(self.array_definition(os, indentation))
        code = code.getvalue()
        return code


@dataclass
class CppLanguageElementClassFactory:
    """Factory for creating declaration and definition instances."""
    
    name: str

    def build_declaration(self, element) -> CppDeclaration:
        """Returns a CppDeclaration for the given element."""
        if isinstance(element, Variable):
            if isinstance(element, Array):
                return ArrayDeclaration(element)
            return VariableDeclaration(element)
        elif isinstance(element, Function):
            return FunctionDeclaration(element)
        elif isinstance(element, Class):
            if isinstance(element, Struct):
                return StructDeclaration(element)
            return ClassDeclaration(element)
        elif isinstance(element, Enum):
            return EnumDeclaration(element)
        raise ValueError(f"Unsupported declaration for element '{element}'")

    def build_definition(self, element) -> CppDefinition:
        """Returns a CppDeclaration for the given element."""
        if isinstance(element, Variable):
            return VariableDefinition(element)
        elif isinstance(element, Function):
            if element.name == self.name:
                return ConstructorDefinition(element)
            else:
                return FunctionDefinition(element)
        elif isinstance(element, Class):
            if isinstance(element, Struct):
                return StructDefinition(element)
            return ClassDefinition(element)
        raise ValueError(f"Unsupported definition for element '{element}'")


@dataclass
class ClassDeclaration(CppDeclaration):

    brace_strategy: BraceStrategy = KnRStyle
    visibility: Visibility = Visibility.PRIVATE
    factory: CppLanguageElementClassFactory = field(init=False)
    
    def __post_init__(self):
        self.factory = CppLanguageElementClassFactory(self.cpp_element.name)

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
                    self.factory.build_declaration(member).code(indentation=indentation))
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

    brace_strategy: BraceStrategy = KnRStyle
    factory: CppLanguageElementClassFactory = field(init=False)
    
    def __post_init__(self):
        self.factory = CppLanguageElementClassFactory(self.cpp_element.name)

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
            init_values = [member.init_value if member.init_value else DefaultValueFactory().default_value(member) for member in members]
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
