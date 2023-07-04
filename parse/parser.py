""" parser.py """

from class_model_dsl.sp_exceptions import ScrallGrammarFileOpen, ScrallParseError
from class_model_dsl.parse.scrall_visitor import ScrallVisitor
from arpeggio import visit_parse_tree, NoMatch
from arpeggio.cleanpeg import ParserPEG
import os # For issuing system commands to generate diagnostic files
from pathlib import Path

class ScrallParser:
    """
    Parses the text of an Activity written in Scrall

        Attributes

        - scrall_grammar -- Text read from the Scrall grammar file
        - scrall_text -- Unparsed scrall text input for a single metamodel activity (state, method, operation)
    """
    scrall_grammar = None # We haven't read it in yet
    scrall_text = None # User will provide this

    root_rule_name = 'activity' # The required name of the highest level parse element

    # Useful paths within the project
    project_path = Path(__file__).parent.parent.parent
    module_path = project_path / 'class_model_dsl'
    grammar_path = module_path / 'grammar' # The grammar files are all here
    diagnostics_path = module_path / 'diagnostics' # All parser diagnostic output goes here

    # Files
    grammar_file = grammar_path / "scrall.peg" # We parse using this peg grammar
    grammar_model_pdf = diagnostics_path / "scrall_model.pdf"
    parse_tree_pdf = diagnostics_path / "scrall_parse_tree.pdf"
    parse_tree_dot = project_path / f"{root_rule_name}_parse_tree.dot"
    parser_model_dot = project_path / f"{root_rule_name}_peg_parser_model.dot"

    pg_tree_dot = project_path / "peggrammar_parse_tree.dot"
    pg_model_dot = project_path / "peggrammar_parser_model.dot"
    pg_tree_pdf = diagnostics_path / "peggrammar_parse_tree.pdf"
    pg_model_pdf = diagnostics_path / "peggrammar_parser_model.pdf"

    @classmethod
    def parse(cls, scrall_text: str, debug=False):  # TODO: define output using named tuple from visitor
        """
        Parse a Scrall activity

        :param scrall_text: The text of a complete activity written in Scrall
        :param debug: Debug mode prints out diagnostic .dots and pdfs of the grammar and parse
        :return: A list of parsed Scrall statements
        """
        # Read the grammar file
        try:
            cls.scrall_grammar = open(cls.grammar_file, 'r').read()
        except OSError as e:
            raise ScrallGrammarFileOpen(cls.grammar_file)

        cls.scrall_text = scrall_text # Text is passed in directly as argument, so no need to read file


        # Create an arpeggio parser for our model grammar that does not eliminate whitespace
        # We interpret newlines and indents in our grammar, so whitespace must be preserved
        parser = ParserPEG(cls.scrall_grammar, cls.root_rule_name, ignore_case=True, skipws=False, debug=debug)
        if debug:
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
        result = visit_parse_tree(parse_tree, ScrallVisitor(debug=debug))

        if debug:
            # Transform dot files into pdfs
            os.system(f'dot -Tpdf {cls.parse_tree_dot} -o {cls.parse_tree_pdf}')
            # Delete dot files since we are only interested in the generated PDFs
            # Comment this part out if you want to retain the dot files
            cls.parse_tree_dot.unlink(True)

        return result