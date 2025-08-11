""" test_operation.py - Test the invocation of an operation"""

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import *

actions = [
    ("dest aslev .= cabin in shaft.Ping both ways()",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(
            input_tokens=[],
            statement=Inst_Assignment_a(
                lhs=Flow_Output_a(name=N_a(name='dest aslev'), exp_type=None), card='1',
                rhs=INST_a(
                    components=[
                        Op_a(
                            owner='cabin in shaft',
                            op_name='Ping both ways',
                            supplied_params=[])]
                ), X=(0, 45)
            ),
            block=None), output_token=None)
     ),
]


@pytest.mark.parametrize("text, expected", actions)
def test_operation(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse[0] == expected
