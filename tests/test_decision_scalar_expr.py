""" test_decision_scalar_expr.py -- Ensure scalar expression works as true result in a decision"""

# This verifies that we don't have a regression on a bug fix where scalar_expr true results were eating the colon
# and failing the parse

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import *

actions = [
    ("fwd dest? =>> fwd dest : {\n"
     "    rev dest .= Ping( dir: Travel direction.opposite )\n"
     "    !rev dest? Travel direction.toggle : =>> rev dest\n"
     "}",
        Execution_Unit_a(
            statement_set=Seq_Statement_Set_a(
                input_tokens=[],
                statement=Decision_a(
                    input=N_a(name='fwd dest'),
                    true_result=Comp_Statement_Set_a(
                        statement=Output_Flow_a(output=N_a(name='fwd dest')), block=None),
                    false_result=Comp_Statement_Set_a(
                        statement=None, block=[
                            Execution_Unit_a(
                                statement_set=Seq_Statement_Set_a(
                                    input_tokens=[],
                                    statement=Inst_Assignment_a(
                                    lhs=Flow_Output_a(name=N_a(name='rev dest'), exp_type=None), card='1',
                                    rhs=INST_a(components=
                                        [N_a(name='Ping'),
                                        Criteria_Selection_a(
                                        card='ALL',
                                        criteria=BOOL_a(op='==',
                                        operands=[N_a(name='dir'),
                                            INST_PROJ_a(
                                                iset=N_a(name='Travel direction'),
                                                projection=Projection_a(
                                                expand=None,
                                                attrs=[N_a(name='opposite')]), op_chain=None)
                                                  ]))]), X=(31, 81)), block=None),
                                output_token=None),
                            Execution_Unit_a(
                                statement_set=Seq_Statement_Set_a(
                                    input_tokens=[],
                                    statement=Decision_a(
                                        input=BOOL_a(op='NOT', operands=N_a(name='rev dest')),
                                        true_result=Comp_Statement_Set_a(
                                            statement=Call_a(
                                                call=N_a(name='Travel direction'),
                                                op_chain=Op_chain_a(components=[N_a(name='toggle')])), block=None),
                                        false_result=Comp_Statement_Set_a(
                                            statement=Output_Flow_a(
                                                output=N_a(name='rev dest')), block=None)), block=None),
                                output_token=None)
                        ]
                    )
                ), block=None
            ), output_token=None),
     )
]

@pytest.mark.parametrize("text, expected", actions)
def test_decision_scalar_true_result(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse[0] == expected
