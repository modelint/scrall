""" scrall_parser.py """

from scrall_exceptions import ScrallParseError
from scrall_visitor import ScrallVisitor
from arpeggio import visit_parse_tree, NoMatch
from arpeggio.cleanpeg import ParserPEG
from pathlib import Path
import os
from collections import namedtuple
from nocomment import nocomment

class ScrallParser:
    """
    Parses a flatland diagram layout specification for a corresponding model file.

        Attributes

        - grammar_file -- (class based) Name of the system file defining the layout grammar
        - layout_file -- Name of user specified diagram layout specification file
    """
    root_rule_name = "activity"

    # Local directories
    project = Path(__file__).parent.parent  # Top level directory of this project
    diag_dir = project / "Diagnostics"
    grammer_dir = project / "Grammar"
    parser_dir = project / "Parser"

    # File paths
    grammar_file = grammer_dir / "scrall.peg"
    grammar_model_pdf = diag_dir / "scrall_model.pdf"
    parse_tree_pdf = diag_dir / "scrall_parse_tree.pdf"
    parse_tree_dot = parser_dir / f"{root_rule_name}_parse_tree.dot"
    parser_model_dot = parser_dir / f"{root_rule_name}_peg_parser_model.dot"

    def __init__(self, scrall_file_path, debug=True):
        """
        Constructor

        :param layout_file_path: Where to find the user supplied layout file
        :param debug: Debug flag
        """
        self.debug = debug
        self.scrall_file_path = scrall_file_path

        # Read the grammar file
        self.scrall_grammar = nocomment(open(ScrallParser.grammar_file, 'r').read())

        # Read the layout file
        self.scrall_text = nocomment(open(self.scrall_file_path, 'r').read())


    def parse(self):
        """
        Parse the layout file and return the content
        :return: The abstract syntax tree content of interest
        """
        # Create an arpeggio parser for our model grammar that does not eliminate whitespace
        # We interpret newlines and indents in our grammar, so whitespace must be preserved
        parser = ParserPEG(self.scrall_grammar, ScrallParser.root_rule_name, skipws=False, debug=self.debug)
        # Now create an abstract syntax tree from our layout text
        try:
            parse_tree = parser.parse(self.scrall_text)
        except NoMatch as e:
            raise ScrallParseError(e)

        # Transform that into a result that is better organized with grammar artifacts filtered out
        result = visit_parse_tree(parse_tree, ScrallVisitor(debug=self.debug))
        if self.debug:
            # Transform dot files into pdfs

            peg_tree_dot = "peggrammar_parse_tree.dot"
            peg_model_dot = "peggrammar_parser_model.dot"
            os.system(f'dot -Tpdf {ScrallParser.parse_tree_dot} -o {ScrallParser.parse_tree_pdf}')
            os.system(f'dot -Tpdf {ScrallParser.parser_model_dot} -o {ScrallParser.grammar_model_pdf}')
            # Cleanup unneeded dot files, we just use the PDFs for now
            Path(ScrallParser.parse_tree_dot).unlink(True)
            Path(ScrallParser.parse_tree_dot).unlink(True)
            Path(ScrallParser.parser_model_dot).unlink(True)
            Path(peg_tree_dot).unlink(True)
            Path(peg_model_dot).unlink(True)
        return result


if __name__ == "__main__":
    # For diagnostics
    scrall_path = Path(__file__).parent.parent / "Examples" / 'e1.scrall'
    x = ScrallParser(scrall_file_path=scrall_path, debug=True)
    try:
        x.parse()
    except ScrallParseError as e:
        print(e)
