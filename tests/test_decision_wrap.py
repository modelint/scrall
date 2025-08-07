""" test_decision_wrap.py -- Test line wrapping """

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import *

# The expected result is teh same for each input case
expected_parse = Execution_Unit_a(
    statement_set=Seq_Statement_Set_a(
        input_tokens=[],
        statement=Decision_a(
            input=N_a(name='choice'),
            true_result=Comp_Statement_Set_a(
                statement=None,
                block=[
                    Execution_Unit_a(
                        statement_set=Seq_Statement_Set_a(
                            input_tokens=[],
                            statement=New_inst_a(
                                cname=N_a(name='cat'), attrs=[], rels=None),
                            block=None
                        ),
                        output_token=None
                    )
                ]), false_result=None), block=None
    ), output_token=None
)

# Different line wrapping of the same content
@pytest.mark.parametrize("text", [
    "choice? { *cat }",
    "choice? {\n*cat }",
    "choice? {\n    *cat\n}",
    "choice?\n    { *cat }",
])
def test_signal_action(text):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse[0] == expected_parse
