""" parser.py """

from scrall.exceptions import ScrallGrammarFileOpen, ScrallParseError, ScrallInputFileEmpty, ScrallInputFileOpen
from scrall.parse.visitor import ScrallVisitor, Execution_Unit_a, Output_Flow_a
from arpeggio import visit_parse_tree, NoMatch
from arpeggio.cleanpeg import ParserPEG
import os  # For issuing system commands to generate diagnostic files
from pathlib import Path
from typing import List


class ScrallParser:
    """
    Parses the text of an Activity written in Scrall

        Attributes

        - scrall_grammar -- Text read from the Scrall grammar file
        - scrall_text -- Unparsed scrall text input for a single metamodel activity (state, method, operation)
    """
    debug = False  # by default
    scrall_grammar = None  # We haven't read it in yet
    scrall_text = None  # User will provide this

    root_rule_name = 'activity'  # The required name of the highest level parse element

    # Useful paths within the project
    src_path = Path(__file__).parent.parent.parent  # Path to src folder
    module_path = src_path / 'scrall'
    grammar_path = module_path / 'parse'  # The grammar files are all here
    cwd = Path.cwd()
    diagnostics_path = cwd / 'scrall-diagnostics'  # All parser diagnostic output goes here

    # Files
    grammar_file = grammar_path / "scrall.peg"  # We parse using this peg grammar
    grammar_model_pdf = diagnostics_path / "scrall_model.pdf"
    parse_tree_pdf = diagnostics_path / "scrall_parse_tree.pdf"
    parse_tree_dot = cwd / f"{root_rule_name}_parse_tree.dot"
    parser_model_dot = cwd / f"{root_rule_name}_peg_parser_model.dot"

    pg_tree_dot = cwd / "peggrammar_parse_tree.dot"
    pg_model_dot = cwd / "peggrammar_parser_model.dot"
    pg_tree_pdf = diagnostics_path / "peggrammar_parse_tree.pdf"
    pg_model_pdf = diagnostics_path / "peggrammar_parser_model.pdf"

    @classmethod
    def parse_file(cls, file_input: Path, debug=False) -> (List[Execution_Unit_a | Output_Flow_a], str):
        """
        Read and save the file contents and options and then call the parser

        :param file_input:  Scrall file to read
        :param debug: Run parser in debug mode
        :return:
        """
        cls.debug = debug
        if debug:
            # If there is no scrall diagnostics directory, create one
            cls.diagnostics_path.mkdir(parents=False, exist_ok=True)



        # Try to read the supplied scrall text file
        try:
            cls.scrall_text = open(file_input, 'r').read()
        except OSError as e:
            raise ScrallInputFileOpen(file_input)

        if not cls.scrall_text:
            raise ScrallInputFileEmpty(file_input)

        if not cls.scrall_text.endswith('\n'):
            cls.scrall_text += '\n'

        return cls.parse()

    @classmethod
    def parse_text(cls, scrall_text: str, debug=False) -> (List[Execution_Unit_a | Output_Flow_a], str):
        """
        Save options and call the parser

        :param scrall_text: One or more lines of scrall_text
        :param debug: Run parser in debug mode
        :return:
        """
        cls.debug = debug
        cls.scrall_text = scrall_text
        if not cls.scrall_text.endswith('\n'):
            cls.scrall_text += '\n'

        return cls.parse()

    @classmethod
    def parse(cls) -> (List[Execution_Unit_a | Output_Flow_a], str):
        """
        Parse a Scrall activity

        :return: A list of parsed execution units and the input scrall text
        """
        # Read the grammar file
        try:
            cls.scrall_grammar = open(cls.grammar_file, 'r').read()
        except OSError as e:
            raise ScrallGrammarFileOpen(cls.grammar_file)

        # Create an arpeggio parser for our model grammar that does not eliminate whitespace
        # We interpret newlines and indents in our grammar, so whitespace must be preserved
        parser = ParserPEG(cls.scrall_grammar, cls.root_rule_name, ignore_case=True, skipws=False, debug=cls.debug)
        if cls.debug:
            # Transform dot files into pdfs
            # os.system(f'dot -Tpdf {cls.pg_tree_dot} -o {cls.pg_tree_pdf}')
            # os.system(f'dot -Tpdf {cls.pg_model_dot} -o {cls.pg_model_pdf}')
            os.system(f'dot -Tpdf {cls.parser_model_dot} -o {cls.grammar_model_pdf}')
            cls.parser_model_dot.unlink(True)
            cls.pg_tree_dot.unlink(True)
            cls.pg_model_dot.unlink(True)

        # Now create an abstract syntax tree from our Scrall activity text
        try:
            parse_tree = parser.parse(cls.scrall_text)
        except NoMatch as e:
            raise ScrallParseError(e) from None

        # Transform that into a result that is better organized with grammar artifacts filtered out
        result = visit_parse_tree(parse_tree, ScrallVisitor(debug=cls.debug))

        if cls.debug:
            # Transform dot files into pdfs
            os.system(f'dot -Tpdf {cls.parse_tree_dot} -o {cls.parse_tree_pdf}')
            # Delete dot files since we are only interested in the generated PDFs
            # Comment this part out if you want to retain the dot files
            cls.parse_tree_dot.unlink(True)

        return result, cls.scrall_text
