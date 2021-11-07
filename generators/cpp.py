from dataclasses import dataclass
from typing import Optional

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
