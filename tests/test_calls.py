""" test_calls.py - Test method calls and calls to an external service """

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import *

actions = [
    ("~.Goto floor( Dest floor: ^new dest )",
    Execution_Unit_a(
        statement_set=Seq_Statement_Set_a(
            input_tokens=[],
            statement=Call_a(
                call=INST_a(
                    components=[
                        Op_a(owner='_external', op_name='Goto floor',
                             supplied_params=[
                                 Supplied_Parameter_a(
                                     pname='Dest floor', sval=IN_a(name='new dest')
                                 )
                             ])]), op_chain=None), block=None), output_token=None)
     ),
    #  Execution_Unit_a(
    #      statement_set=Seq_Statement_Set_a(
    #          input_tokens=[],
    #          statement=Call_a(
    #              call=None,
    #              op_chain=Op_chain_a(
    #                  components=[
    #                      Scalar_op_a(
    #                          name=N_a(name='Goto floor'),
    #                          supplied_params=[
    #                              Supplied_Parameter_a(
    #                                  pname='Dest floor',
    #                                  sval=IN_a(name='new dest')
    #                              )
    #                          ]
    #                      )
    #                  ]
    #              )
    #          ), block=None),
    #      output_token=None)
    #  ),
    (".Ping( dir: Travel direction.opposite )",
    Execution_Unit_a(
        statement_set=Seq_Statement_Set_a(
            input_tokens=[],
            statement=Call_a(
                call=INST_a(
                    components=[
                        Op_a(
                            owner='_implicit',
                            op_name='Ping',
                            supplied_params=[
                                Supplied_Parameter_a(
                                    pname='dir',
                                    sval=INST_PROJ_a(
                                        iset=N_a(name='Travel direction'),
                                        projection=Projection_a(
                                            expand=None, attrs=[N_a(name='opposite')]
                                        ),
                                        op_chain=None
                                    )
                                )
                            ]
                        )
                    ]
                ),
                op_chain=None),
            block=None),
        output_token=None)
     ),
]

@pytest.mark.parametrize("text, expected", actions)
def test_call_action(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse[0] == expected
