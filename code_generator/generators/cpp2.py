
import re


CPP_IDENTIFIER_REGEX = r'^[a-zA-Z_]+[a-zA-Z0-9_]*$'
CPP_IDENTIFIER_PATTERN = re.compile(CPP_IDENTIFIER_REGEX)


class CppSyntaxError(Exception):
    pass


class CppIdentifierError(CppSyntaxError):
    def __init__(self, identifier) -> None:
        self.identifier = identifier
        self.message = f'Invalid C++ identifier: {identifier}'
        super().__init__()


class CppTypeError(CppSyntaxError):
    def __init__(self, type) -> None:
        self.type = type
        self.message = f'Invalid C++ type: {type}'
        super().__init__()


class Variable:
    def __init__(self, name, type='void', qualifiers=None) -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        if not CPP_IDENTIFIER_PATTERN.fullmatch(type):
            raise CppTypeError(type)
        self.name = name
        self.type = type
        self.qualifiers = qualifiers

    def __str__(self) -> str:
        return self.name

    def declaration_str(self):
        qualifiers = ' '.join(self.qualifiers) + ' ' if self.qualifiers is not None else ''
        return f'{qualifiers}{self.type} {self.name}'


class Function:
    def __init__(self, name, type='void', qualifiers=None) -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        if not CPP_IDENTIFIER_PATTERN.fullmatch(type):
            raise CppTypeError(type)
        self.name = name
        self.type = type
        self.qualifiers = qualifiers
        self.args = []

    def __str__(self) -> str:
        return self.name

    def declaration_str(self):
        qualifiers = ' '.join(self.qualifiers) + ' ' if self.qualifiers is not None else ''
        args = ', '.join([v.declaration_str() if type(v) == Variable else v for v in self.args]) if self.args is not None else ''
        return f'{qualifiers}{self.type} {self.name}({args})'

    def arg(self, arg):
        """
        Builder pattern to add an arg to the function.

        Args:
            arg -- A str or Variable

        Returns:
            self
        """
        self.args.append(arg)
        return self
