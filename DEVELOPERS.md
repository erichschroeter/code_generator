# Developers

## Design

### C++ Components

```mermaid
---
title: C++ components
---
flowchart LR
    Python --> Codefile
    Codefile --> DeclarationFile
    Codefile --> DefinitionFile
    Variable --> DeclarationFile
    Function --> DeclarationFile
    Class --> DefinitionFile
    Variable --> DefinitionFile
    Function --> DefinitionFile
    Class --> DeclarationFile
    DefinitionFile --> .cpp
    DeclarationFile --> .h
```

## Executing unit tests
The following command will execute the unit tests.

```bash
python -m unittest
```

or, using [pytest](https://docs.pytest.org/en/6.2.x/):

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
```
