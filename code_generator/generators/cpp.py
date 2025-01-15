from abc import ABC, abstractmethod
from io import StringIO
import re
from textwrap import dedent
from typing import Callable

from jinja2 import Template


CPP_IDENTIFIER_REGEX = r"^[a-zA-Z_:]+[a-zA-Z0-9_:]*$"
CPP_IDENTIFIER_PATTERN = re.compile(CPP_IDENTIFIER_REGEX)
CPP_TYPE_REGEX = r"^([a-zA-Z_:]+[a-zA-Z0-9_:]*| |&|\*)*$"
CPP_TYPE_PATTERN = re.compile(CPP_TYPE_REGEX)


class CppSyntaxError(Exception):
    pass


class CppIdentifierError(CppSyntaxError):
    def __init__(self, identifier) -> None:
        self.identifier = identifier
        self.message = f"Invalid C++ identifier: {identifier}"
        super().__init__()


class CppTypeError(CppSyntaxError):
    def __init__(self, type) -> None:
        self.type = type
        self.message = f"Invalid C++ type: {type}"
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


def is_header(obj):
    """
    Intended use is for Jinja2 template.

    Returns:
        Returns True if `obj` is a Header, else False.
    """
    return isinstance(obj, Header)


def build_jinja2_template(template_str):
    tmpl = Template(template_str)
    tmpl.environment.tests["variable"] = is_variable
    tmpl.environment.tests["function"] = is_function
    tmpl.environment.tests["class"] = is_class
    tmpl.environment.tests["header"] = is_header
    return tmpl


class Namespace:
    def __init__(self, name, parent=None) -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        self.parent = parent
        self.name = name

    def __str__(self) -> str:
        if self.parent is None:
            return self.name
        return f"{self.parent.__str__()}::{self.name}"


class QualifierContext:
    def __init__(self, def_pre=None, def_post=None, decl_pre=None, decl_post=None) -> None:
        self.def_pre = def_pre
        self.def_post = def_post
        self.decl_pre = decl_pre
        self.decl_post = decl_post

    def decl_str(self, obj):
        pre = (
            " ".join(self.decl_pre) + " " if self.decl_pre is not None else ""
        )
        post = (
            " ".join(self.decl_post) + " " if self.decl_post is not None else ""
        )
        return f"{pre}{obj}{post}"

    def def_str(self, obj):
        pre = (
            " ".join(self.def_pre) + " " if self.def_pre is not None else ""
        )
        post = (
            " ".join(self.def_post) + " " if self.def_post is not None else ""
        )
        return f"{pre}{obj}{post}"


class Variable:
    def __init__(self, name, type="void", qualifier_ctx=None) -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        if not CPP_TYPE_PATTERN.fullmatch(type):
            raise CppTypeError(type)
        self.name = name
        self.type = type
        self.qualifier_ctx = qualifier_ctx
        self._namespace = None
        self._value = 0

    def __str__(self) -> str:
        return self.name

    def val(self, the_value):
        self._value = the_value
        return self

    def namespace(self, the_namespace):
        self._namespace = the_namespace
        return self

    def decl_str(self):
        if self.qualifier_ctx:
            return self.qualifier_ctx.decl_str(f"{self.type} {self.name}")
        return f"{self.type} {self.name}"

    def def_str(self):
        the_value = str(self._value) if type(self._value) != str else f'"{self._value}"'
        the_namespace = f"{self._namespace}::" if self._namespace else ""
        if self.qualifier_ctx:
            return self.qualifier_ctx.def_str(f"{self.type} {the_namespace}{self.name} = {the_value}")
        return f"{self.type} {the_namespace}{self.name} = {the_value}"


class Function:
    def __init__(self, name, type="void", qualifiers=None) -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        if not CPP_TYPE_PATTERN.fullmatch(type):
            raise CppTypeError(type)
        self.name = name
        self.type = type
        self.qualifiers = qualifiers
        self.args = []
        self._impl = None
        self._namespace = None

    def __str__(self) -> str:
        return self.name

    def decl_str(self):
        qualifiers = (
            " ".join(self.qualifiers) + " " if self.qualifiers is not None else ""
        )
        args = (
            ", ".join([v.decl_str() if type(v) == Variable else v for v in self.args])
            if self.args is not None
            else ""
        )
        if not qualifiers and not self.type:
            return f"{self.name}({args})"
        else:
            return f"{qualifiers}{self.type} {self.name}({args})"

    def call_str(self):
        args = (
            ", ".join([str(v) if type(v) != str else v for v in self.args])
            if self.args is not None
            else ""
        )
        return f"{args}"

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

    def namespace(self, the_namespace):
        self._namespace = the_namespace
        return self

    def impl(self, the_impl):
        self._impl = the_impl
        return self

    def impl_str(self):
        if isinstance(self._impl, str):
            return f"{self._impl}"
        elif isinstance(self._impl, Callable):
            return f"{self._impl()}"
        else:
            return ""

    def def_str(self):
        qualifiers = (
            " ".join(self.qualifiers) + " " if self.qualifiers is not None else ""
        )
        args = self.call_str()
        the_impl = self.impl_str()
        the_impl = f"{the_impl}\n" if the_impl else the_impl
        the_namespace = f"{self._namespace}::" if self._namespace else ""
        if not qualifiers and not self.type:
            return f"{the_namespace}{self.name}({args})\n{{\n{the_impl}}}"
        else:
            return f"{qualifiers}{self.type} {the_namespace}{self.name}({args})\n{{\n{the_impl}}}"


class Constructor(Function):
    def __init__(self, name, type="", qualifiers=None) -> None:
        super().__init__(name, type, qualifiers)


class Class:
    """
    Creates a C++ class to add items such as variables, functions, etc.

    To render, the `decl_template` may be overridden for customization.
    """

    def __init__(self, name) -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        self.name = name
        self.type = "class"
        self.members_public = []
        self.members_protected = []
        self.members_private = []
        self.decl_template = dedent(
            """\
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
        }"""
        )
        self.def_template = dedent(
            """\
        {%- if private_members %}
            {%- for member in private_members %}
            {%- if member is variable or member is function -%}
            {{member.def_str()}}
            {%- else %}
            {{member}}
            {%- endif -%}
            {%- endfor -%}
        {% endif %}
        {%- if protected_members %}
            {%- for member in protected_members %}
            {%- if member is variable or member is function -%}
            {{member.def_str()}}
            {%- else %}
            {{member}}
            {%- endif -%}
            {%- endfor -%}
        {% endif %}
        {%- if public_members %}
            {%- for member in public_members %}
            {%- if member is variable or member is function -%}
            {{member.def_str()}}
            {%- else %}
            {{member}}
            {%- endif -%}
            {%- endfor -%}
        {% endif %}
        """
        )

    def __str__(self) -> str:
        return self.name

    def decl_str(self):
        fields = {
            "type": self.type,
            "name": self.name,
            "public_members": self.members_public,
            "protected_members": self.members_protected,
            "private_members": self.members_private,
        }
        tmpl = build_jinja2_template(self.decl_template)
        return tmpl.render(fields)

    def def_str(self):
        # return self.decl_str()
        # code = StringIO()
        # for member in self.members_public:
        #     code.write(member.def_str())
        # for member in self.members_protected:
        #     code.write(member.def_str())
        # for member in self.members_private:
        #     code.write(member.def_str())
        # return code.getvalue()
        fields = {
            "name": self.name,
            "public_members": self.members_public,
            "protected_members": self.members_protected,
            "private_members": self.members_private,
        }
        tmpl = build_jinja2_template(self.def_template)
        return tmpl.render(fields)

    def member(self, the_member, scope="private"):
        if hasattr(the_member, 'namespace'):
            the_member.namespace(self.name)  # Override the namespace now that it's a member of this class.
        if "private" == scope.lower():
            self.members_private.append(the_member)
        elif "protected" == scope.lower():
            self.members_protected.append(the_member)
        elif "public" == scope.lower():
            self.members_public.append(the_member)
        return self


class Struct(Class):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.type = "struct"

    def member(self, member, scope="public"):
        return super().member(member, scope)


class Array(ABC):
    def __init__(self, name, type="int") -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        if not CPP_IDENTIFIER_PATTERN.fullmatch(type):
            raise CppTypeError(name)
        self.name = name
        self.type = type
        self.items = []
        self._size = None
        self.def_template = dedent(
            """\
        {{type}} {{name}}[{{size}}] =
        {
        {%- if items %}
            {%- for item in items %}
            {%- if item is function %}
            {{ "{" }}{{ item.call_str() }}{{ "}" }}{{"," if not loop.last else ""}}
            {%- else %}
            {{item}}{{"," if not loop.last else ""}}
            {%- endif %}
            {%- endfor -%}
        {% endif %}
        }"""
        )

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
    def __init__(self, name, type="int") -> None:
        super().__init__(name, type)

    def decl_str(self):
        the_size = self._size if self._size is not None else len(self.items)
        return f"{self.type} {self.name}[{str(the_size)}]"

    def def_str(self):
        the_size = self._size if self._size is not None else len(self.items)
        fields = {
            "type": self.type,
            "name": self.name,
            "items": self.items,
            "size": the_size,
        }
        tmpl = build_jinja2_template(self.def_template)
        return tmpl.render(fields)


class ArrayOnHeap(Array):
    def __init__(self, name, type="int") -> None:
        super().__init__(name, type)
        self.def_template = dedent(
            """\
        {{type}} *{{name}} = new {{type}}[{{size}}];
        {%- if items %}
        {%- for item in items %}
        {%- if item is function %}
        {{name}}[{{loop.index0}}] = {{ item }};
        {%- else %}
        {{name}}[{{loop.index0}}] = {{item}};
        {%- endif %}
        {%- endfor -%}
        {% endif %}"""
        )

    def decl_str(self):
        the_size = self._size if self._size is not None else len(self.items)
        return f"{self.type} {self.name}[{str(the_size)}]"

    def def_str(self):
        the_size = self._size if self._size is not None else len(self.items)
        fields = {
            "type": self.type,
            "name": self.name,
            "items": self.items,
            "size": the_size,
        }
        tmpl = build_jinja2_template(self.def_template)
        return tmpl.render(fields)


class Enum:
    def __init__(self, name, type=None, prefix="") -> None:
        if not CPP_IDENTIFIER_PATTERN.fullmatch(name):
            raise CppIdentifierError(name)
        if type and not CPP_IDENTIFIER_PATTERN.fullmatch(type):
            raise CppTypeError(name)
        self.name = name
        self.type = type
        self._prefix = prefix
        self.items = []
        self.def_template = dedent(
            """\
        enum {{name}}{% if type %} : {{type}}{% endif %}
        {
        {%- if items %}
            {%- for item in items %}
            {{ prefix }}{{item.0}}{% if item.1 %} = {{item.1}}{% endif %}{{"," if not loop.last else ""}}
            {%- endfor -%}
        {% endif %}
        }"""
        )

    def __str__(self) -> str:
        return self.name

    def def_str(self) -> str:
        fields = {
            "type": self.type,
            "prefix": self._prefix,
            "name": self.name,
            "items": self.items,
        }
        tmpl = build_jinja2_template(self.def_template)
        return tmpl.render(fields)

    def prefix(self, the_prefix):
        self._prefix = the_prefix
        return self

    def add(self, item, value=None):
        self.items.append((item, value))
        return self


class Header:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.includes = []
        self.includes_local = []
        self.cpp_items = []
        self._guard = None
        self.template = dedent(
            """\
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
        {% endif %}"""
        )

    def __str__(self) -> str:
        fields = {
            "guard": self._guard,
            "includes_local": self.includes_local,
            "includes": self.includes,
            "cpp_items": self.cpp_items,
        }
        tmpl = Template(self.template)
        tmpl.environment.tests["variable"] = is_variable
        tmpl.environment.tests["function"] = is_function
        tmpl.environment.tests["class"] = is_class
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


class Source:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.includes = []
        self.includes_local = []
        self.cpp_items = []
        self.template = dedent(
            """\
        {%- if includes %}{% for include in includes -%}
            {%- if include is header -%}
            #include <{{ include.filename }}>
            {%- else -%}
            #include <{{ include }}>
            {%- endif %}
        {% endfor -%}{% endif %}
        {%- if includes_local %}{% for include in includes_local -%}
            {%- if include is header -%}
            #include "{{ include.filename }}"
            {%- else -%}
            #include "{{ include }}"
            {%- endif %}
        {% endfor -%}{% endif %}
        {%- if cpp_items %}{% for cpp_item in cpp_items -%}
        {%- if cpp_item is class -%}
        {%- for cls_member in cpp_item.members_private -%}
        {% if cls_member is variable -%}
        {{ cls_member.def_str() }};
        {% else -%}
        {{ cls_member.def_str() }}
        {% endif -%}
        {% endfor -%}
        {%- for cls_member in cpp_item.members_protected -%}
        {% if cls_member is variable -%}
        {{ cls_member.def_str() }};
        {% else -%}
        {{ cls_member.def_str() }}
        {% endif -%}
        {% endfor -%}
        {%- for cls_member in cpp_item.members_public -%}
        {% if cls_member is variable -%}
        {{ cls_member.def_str() }};
        {% else -%}
        {{ cls_member.def_str() }}
        {% endif -%}
        {% endfor -%}
        {% elif cpp_item is variable -%}
        {{ cpp_item.def_str() }};
        {% elif cpp_item is function -%}
        {{ cpp_item.def_str() }}
        {% else -%}
        {{ cpp_item }}
        {% endif -%}
        {% endfor -%}{% endif %}"""
        )

    def __str__(self) -> str:
        fields = {
            "includes_local": self.includes_local,
            "includes": self.includes,
            "cpp_items": self.cpp_items,
        }
        tmpl = build_jinja2_template(self.template)
        return tmpl.render(fields)

    def include(self, header):
        self.includes.append(header)
        return self

    def includelocal(self, header):
        self.includes_local.append(header)
        return self

    def add(self, cpp_item):
        self.cpp_items.append(cpp_item)
        return self
