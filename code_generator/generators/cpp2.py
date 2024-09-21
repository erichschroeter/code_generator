
import re
from textwrap import dedent

from jinja2 import Template


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

    def decl_str(self):
        qualifiers = ' '.join(self.qualifiers) + ' ' if self.qualifiers is not None else ''
        return f'{qualifiers}{self.type} {self.name}'


def is_variable(obj):
    return isinstance(obj, Variable)


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

    def decl_str(self):
        qualifiers = ' '.join(self.qualifiers) + ' ' if self.qualifiers is not None else ''
        args = ', '.join([v.decl_str() if type(v) == Variable else v for v in self.args]) if self.args is not None else ''
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


def is_function(obj):
    return isinstance(obj, Function)


class Class:
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
        # return Template(self.decl_template).render(fields)

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
