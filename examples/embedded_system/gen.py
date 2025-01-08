from code_generator.generators.cpp import Class, Constructor, Function, Header, Source, Variable
from typing import List, Tuple
from dataclasses import dataclass, field
import argparse
import json
import logging
import os
import sys

# For this example, the Python path needs to be added so we can use code generator modules.
GIT_TOP_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, GIT_TOP_DIR)


@dataclass
class Config:
    strings: List[Tuple[str, str]] = field(init=list)


def generate_code(cfg: Config):
    '''
    Uses the Config to generate a simple code example.
    '''
    hdr = Header('Config.h')
    src = Source('Config.cpp')
    vars = []
    for string_map in cfg.strings:
        vars.append(Variable(name=string_map[0], type='char *', qualifiers=['const']).val(string_map[1]))
    cls = Class(name='Config')
    cls.member(Constructor(name=cls.name), scope='public')
    for var in vars:
        cls.member(var, scope='public')
    hdr.add(cls)
    src.includelocal(hdr)
    src.add(cls)
    return hdr, src


def _parse_i18n(text_filepath: str) -> List[Tuple[str, str]]:
    strings = []
    with open(text_filepath) as text_file:
        for line in text_file.readlines():
            tokens = line.split('=')
            strings.append((tokens[0].strip(), tokens[1].strip()))
    return strings


def parse_config(args) -> Config:
    '''
    Parses the config file specified via the command line and returns a valid Config.
    '''
    config = Config(strings=[])
    with open(args.config_file) as config_file:
        json_data = json.load(config_file)
        i18n_relative_path = os.path.join(os.path.dirname(args.config_file), json_data['strings'][0])
        config.strings = _parse_i18n(i18n_relative_path)
        # BEGIN custom validation of config
        # END custom validation of config
    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='0.1.0')
    parser.add_argument('-v', '--verbosity',
                        choices=['critical', 'error', 'warning', 'info', 'debug'],
                        default='info',
                        help='Set the logging verbosity level.')
    parser.add_argument(
        '--target', help='Generate C++ code for the specified target')
    parser.add_argument('-o', '--output_dir', help='Directory to write files')
    parser.add_argument('-d', '--dryrun', action='store_true', help="Dryrun, don't write files")
    parser.add_argument('config_file', help='JSON config file')
    args = parser.parse_args()

    # START configure logger
    class ColorLogFormatter(logging.Formatter):
        '''
        Custom formatter that changes the color of logs based on the log level.
        '''

        grey = "\x1b[38;20m"
        green = "\u001b[32m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        blue = "\u001b[34m"
        cyan = "\u001b[36m"
        reset = "\x1b[0m"

        timestamp = '%(asctime)s - '
        loglevel = '%(levelname)s'
        message = ' - %(message)s'

        FORMATS = {
            logging.DEBUG:    timestamp + blue + loglevel + reset + message,
            logging.INFO:     timestamp + green + loglevel + reset + message,
            logging.WARNING:  timestamp + yellow + loglevel + reset + message,
            logging.ERROR:    timestamp + red + loglevel + reset + message,
            logging.CRITICAL: timestamp + bold_red + loglevel + reset + message
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
    loglevel = getattr(logging, args.verbosity.upper())
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    ch.setFormatter(ColorLogFormatter())
    log = logging.getLogger()
    log.setLevel(loglevel)
    log.addHandler(ch)
    # END configure logger

    logging.debug(args)
    cfg = parse_config(args)
    logging.debug(cfg)
    output_dir = args.output_dir if args.output_dir else os.getcwd()
    os.makedirs(output_dir, exist_ok=True)
    hdr, src = generate_code(cfg)
    if args.dryrun:
        print('================================================================================')
        print('Config.h')
        print('================================================================================')
        print(str(hdr))
        print('================================================================================')
        print('Config.cpp')
        print('================================================================================')
        print(str(src))
    else:
        with open(os.path.join(os.getcwd(), hdr.filename), 'w+') as f:
            f.write(str(hdr))
        with open(os.path.join(os.getcwd(), src.filename), 'w+') as f:
            f.write(str(src))


if __name__ == "__main__":
    main()
