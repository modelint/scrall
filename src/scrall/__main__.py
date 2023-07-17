"""
__main__.py

Scrall Parser
"""

import logging
import logging.config
import sys
import argparse
from pathlib import Path
from scrall import version
from scrall.parse.parser import ScrallParser

_logpath = Path("scrall.log")

def get_logger():
    """Initiate the logger"""
    log_conf_path = Path(__file__).parent / 'log.conf'  # Logging configuration is in this file
    logging.config.fileConfig(fname=log_conf_path, disable_existing_loggers=False)
    return logging.getLogger(__name__)  # Create a logger for this module

# Configure the expected parameters and actions for the argparse module
def parse(cl_input):
    """
    The command line interface is for diagnostic purposes

    :param cl_input:
    :return:
    """
    parser = argparse.ArgumentParser(description='Scrall parser')
    parser.add_argument('-e', '--expr', action='store',
                        help='Scrall expression')
    parser.add_argument('-f', '--file', action='store',
                        help='Scrall file name')
    parser.add_argument('-D', '--debug', action='store_true',
                        help='Debug mode'),
    parser.add_argument('-V', '--version', action='store_true',
                        help='Print the current version of parser')
    return parser.parse_args(cl_input)


def main():
    # Start logging
    logger = get_logger()
    logger.info(f'Scrall parser version: {version}')

    # Parse the command line args
    args = parse(sys.argv[1:])

    if args.version:
        # Just print the version and quit
        print(f'Scrall parser version: {version}')
        sys.exit(0)

    if args.expr:
        text = args.expr + '\n'
        d = args.debug
        result = ScrallParser.parse_text(scrall_text=text, debug=d)

    if args.file:
        fpath = Path(args.file)
        d = args.debug
        result = ScrallParser.parse_file(file_input=fpath, debug=d)

    logger.info("No problemo")  # We didn't die on an exception, basically
    print("\nNo problemo")


if __name__ == "__main__":
    main()