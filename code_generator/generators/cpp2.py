
from abc import ABC, abstractmethod
from io import StringIO
import re
from textwrap import dedent

from jinja2 import Template


CPP_IDENTIFIER_REGEX = r'^[a-zA-Z_]+[a-zA-Z0-9_]*$'
CPP_IDENTIFIER_PATTERN = re.compile(CPP_IDENTIFIER_REGEX)
CPP_TYPE_REGEX = r'^([a-zA-Z_]+[a-zA-Z0-9_]*| |&|\*)*$'
CPP_TYPE_PATTERN = re.compile(CPP_TYPE_REGEX)


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


def is_variable(obj):
    """
    Intended use is for Jinja2 template.

    Returns:
        Returns True if `obj` is a Variable, else False.
    """
    return isinstance(obj, Variable)


def is_function(obj):
    """
    Intended use is for Jinja2 template.

    Returns:
        Returns True if `obj` is a Function, else False.
    """
    return isinstance(obj, Function)


def is_class(obj):
    """
    Intended use is for Jinja2 template.

    Returns:
        Returns True if `obj` is a Class, else False.
    """
    return isinstance(obj, Class)


class Variable:
    def __init__(self, name, type='void', qualifiers=None) -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        if not CPP_TYPE_PATTERN.fullmatch(type):
            raise CppTypeError(type)
        self.name = name
        self.type = type
        self.qualifiers = qualifiers
        self.value = 0

    def __str__(self) -> str:
        return self.name

    def val(self, val):
        self.value = val
        return self

    def decl_str(self):
        qualifiers = ' '.join(self.qualifiers) + ' ' if self.qualifiers is not None else ''
        return f'{qualifiers}{self.type} {self.name}'

    def def_str(self):
        qualifiers = ' '.join(self.qualifiers) + ' ' if self.qualifiers is not None else ''
        value = str(self.value) if type(self.value) != str else f'"{self.value}"'
        return f'{qualifiers}{self.type} {self.name} = {value}'


class Function:
    def __init__(self, name, type='void', qualifiers=None) -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        if not CPP_TYPE_PATTERN.fullmatch(type):
            raise CppTypeError(type)
        self.name = name
        self.type = type
        self.qualifiers = qualifiers
        self.args = []

    def __str__(self) -> str:
        return self.name

    def decl_str(self):
        qualifiers = ' '.join(self.qualifiers) + ' ' if self.qualifiers is not None else ''
        args = ', '.join([v.decl_str() if type(v) == Variable else v for v in self.args]) if self.args is not None else ''
        return f'{qualifiers}{self.type} {self.name}({args})'

    def call_str(self):
        args = ', '.join([str(v) if type(v) == Variable else v for v in self.args]) if self.args is not None else ''
        return f'{args}'

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


class Class:
    """
    Creates a C++ class to add items such as variables, functions, etc.

    To render, the `decl_template` may be overridden for customization.
    """
    def __init__(self, name) -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        self.name = name
        self.type = 'class'
        self.members_public = []
        self.members_protected = []
        self.members_private = []
        self.decl_template = dedent('''\
        {{type}} {{name}}
        {
        {%- if public_members %}
        public:
            {%- for member in public_members %}
            {%- if member is variable or member is function %}
            {{member.decl_str()}};
            {%- else %}
            {{member}}
            {%- endif -%}
            {%- endfor -%}
        {% endif %}
        {%- if protected_members %}
        protected:
            {%- for member in protected_members %}
            {%- if member is variable or member is function %}
            {{member.decl_str()}};
            {%- else %}
            {{member}}
            {%- endif -%}
            {%- endfor -%}
        {% endif %}
        {%- if private_members %}
        private:
            {%- for member in private_members %}
            {%- if member is variable or member is function %}
            {{member.decl_str()}};
            {%- else %}
            {{member}}
            {%- endif -%}
            {%- endfor -%}
        {% endif %}
        }''')

    def __str__(self) -> str:
        return self.name

    def decl_str(self):
        fields = {
            'type': self.type,
            'name': self.name,
            'public_members': self.members_public,
            'protected_members': self.members_protected,
            'private_members': self.members_private}
        tmpl = Template(self.decl_template)
        tmpl.environment.tests['variable'] = is_variable
        tmpl.environment.tests['function'] = is_function
        return tmpl.render(fields)

    def member(self, member, scope='private'):
        if 'private' == scope.lower():
            self.members_private.append(member)
        elif 'protected' == scope.lower():
            self.members_protected.append(member)
        elif 'public' == scope.lower():
            self.members_public.append(member)
        return self


class Struct(Class):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.type = 'struct'

    def member(self, member, scope='public'):
        return super().member(member, scope)


class Array(ABC):
    def __init__(self, name, type='int') -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        if not CPP_IDENTIFIER_PATTERN.fullmatch(type):
            raise CppTypeError(name)
        self.name = name
        self.type = type
        self.items = []
        self._size = None
        self.def_template = dedent('''\
        {{type}} {{name}}[{{size}}] =
        {
        {%- if items %}
            {%- for item in items %}
            {{item}}{{"," if not loop.last else ""}}
            {%- endfor -%}
        {% endif %}
        }''')

    def __str__(self) -> str:
        return self.name

    @abstractmethod
    def decl_str(self) -> str:
        pass

    @abstractmethod
    def def_str(self) -> str:
        pass

    def size(self, the_size):
        self._size = the_size
        return self

    def add(self, item):
        self.items.append(item)
        return self


class ArrayOnStack(Array):
    def __init__(self, name, type='int') -> None:
        super().__init__(name, type)

    def decl_str(self):
        the_size = self._size if self._size is not None else len(self.items)
        return f'{self.type} {self.name}[{str(the_size)}]'

    def def_str(self):
        the_size = self._size if self._size is not None else len(self.items)
        fields = {
            'type': self.type,
            'name': self.name,
            'items': self.items,
            'size': the_size}
        tmpl = Template(self.def_template)
        tmpl.environment.tests['variable'] = is_variable
        tmpl.environment.tests['function'] = is_function
        return tmpl.render(fields)


class ArrayOnHeap(Array):
    def __init__(self, name, type='int') -> None:
        super().__init__(name, type)


class Header:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.includes = []
        self.includes_local = []
        self.cpp_items = []
        self._guard = None
        self.template = dedent('''\
        {%- if guard -%}
        #ifndef {{ guard }}
        #define {{ guard }}
        {% endif -%}
        {%- if includes %}{% for include in includes -%}
            #include <{{ include }}>
        {% endfor -%}{% endif %}
        {%- if includes_local %}{% for include in includes_local -%}
            #include "{{ include }}"
        {% endfor -%}{% endif %}
        {%- if cpp_items %}{% for cpp_item in cpp_items -%}
        {%- if cpp_item is variable or cpp_item is function or cpp_item is class -%}
        {{ cpp_item.decl_str() }};
        {% else -%}
        {{ cpp_item }}
        {% endif -%}
        {% endfor -%}{% endif %}
        {%- if guard -%}
        #endif
        {% endif %}''')

    def __str__(self) -> str:
        fields = {
            'guard': self._guard,
            'includes_local': self.includes_local,
            'includes': self.includes,
            'cpp_items': self.cpp_items}
        tmpl = Template(self.template)
        tmpl.environment.tests['variable'] = is_variable
        tmpl.environment.tests['function'] = is_function
        tmpl.environment.tests['class'] = is_class
        return tmpl.render(fields)

    def guard(self, guard):
        self._guard = guard
        return self

    def include(self, header):
        self.includes.append(header)
        return self

    def includelocal(self, header):
        self.includes_local.append(header)
        return self

    def add(self, cpp_item):
        self.cpp_items.append(cpp_item)
        return self
