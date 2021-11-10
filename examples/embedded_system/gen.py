import sys
import os

# For this example, the Python path needs to be added so we can use code generator modules.
GIT_TOP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, GIT_TOP_DIR)

import argparse
from dataclasses import dataclass, field
import json
from typing import List, Tuple

from code_generator.code_generator import CppFile
from code_generator.generators.cpp import Class, ClassDeclaration, ClassDefinition, Const, Function, Namespace, Variable, VariableDeclaration, VariableDefinition

@dataclass
class Config:
    strings: List[Tuple[str, str]] = field(init=list)


def generate_code(cfg: Config):
    hdr = CppFile('Example_Text.h')
    cpp = CppFile('Example_Text.cpp')
    vars = []
    for string_map in cfg.strings:
        vars.append(Variable(name=string_map[0], type='char *', qualifier=Const(), init_value=f'"{string_map[1]}"'))
    namespace = Namespace(name='MyCompany')
    cls = Class(name='Cfg', ref_to_parent=namespace)
    cls.add(Function(name=cls.name))
    for var in vars:
        cls.add(var)
        hdr(VariableDeclaration(var).code())
        cpp(VariableDefinition(var).code())
    hdr = CppFile('Example_Config.h')
    cpp = CppFile('Example_Config.cpp')
    hdr(ClassDeclaration(cls).code())
    cpp('#include "Example_Config.h"')
    cpp(ClassDefinition(cls).code())
    

def parse_i18n(text_filepath: str) -> List[Tuple[str, str]]:
    strings = []
    with open(text_filepath) as text_file:
        for line in text_file.readlines():
            tokens = line.split('=')
            strings.append((tokens[0].strip(), tokens[1].strip())) 
    return strings


def parse_config(args) -> Config:
    config = Config(strings=[])
    with open(args.config_file) as config_file:
        json_data = json.load(config_file)
        # TODO This is where you would perform validation for your own config schema.
        config.strings = parse_i18n(json_data['strings'][0])
    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument('--target', help='Generate C++ code for the specified target')
    parser.add_argument('-o', '--output-dir', help='Directory to write files')
    parser.add_argument('config_file', help='JSON config file')
    args = parser.parse_args()
    cfg = parse_config(args)
    print(cfg)
    generate_code(cfg)


if __name__ == "__main__":
    main()

