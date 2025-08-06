""" test_calls.py - Test method calls and calls to an external service """

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import (
    Execution_Unit_a, Seq_Statement_Set_a, Call_a, Op_chain_a, Scalar_op_a,
    Supplied_Parameter_a, N_a, IN_a,
)

actions = [
    ("~.Goto floor( Dest floor: ^new dest )",
     Execution_Unit_a(
         statement_set=Seq_Statement_Set_a(
             input_tokens=[],
             statement=Call_a(
                 call=None,
                 op_chain=Op_chain_a(
                     components=[
                         Scalar_op_a(
                             name=N_a(name='Goto floor'),
                             supplied_params=[
                                 Supplied_Parameter_a(
                                     pname='Dest floor',
                                     sval=IN_a(name='new dest')
                                 )
                             ]
                         )
                     ]
                 )
             ), block=None),
         output_token=None)
     ),
]

@pytest.mark.parametrize("text, expected", actions)
def test_signal_action(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse[0] == expected
