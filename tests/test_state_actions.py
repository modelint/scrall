# simple tests

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import Execution_Unit_a, Signal_a, Signal_Dest_a, N_a, INST_a, PATH_a, R_a,\
    Inst_Assignment_a, Flow_Output_a, Criteria_Selection_a, BOOL_a, Supplied_Parameter_a, Call_a, Op_a, IN_a, \
    Table_Assignment_a, TEXPR_a, Projection_a, Seq_Statement_Set_a, Scalar_Assignment_a, Scalar_RHS_a, \
    Sequence_Token_a, Case_a, Switch_a, Enum_a, Output_Flow_a, INST_PROJ_a, Comp_Statement_Set_a, \
    Decision_a

actions = [
    (
"""
!(/R2/Shaft.In service) ?
    // this case
    Take out of service -> ME
""",
    Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
        statement=Decision_a(input=BOOL_a(
            op='NOT', operands=INST_PROJ_a(iset=INST_a(
                components=[PATH_a(hops=[R_a(rnum='R2'), N_a(name='Shaft')])]),
                projection=Projection_a(expand=None, attrs=[N_a(name='In service')]))),
            true_result=Comp_Statement_Set_a(statement=
                    Signal_a(event='Take out of service', supplied_params=[],
                             dest=Signal_Dest_a(target_iset=N_a(name='ME'),
                             assigner_partition=N_a(name=None), delay=0)), block=None),
            false_result=None),
        block=None), output_token=None)
    ),
    ("!(/R2/Shaft.In service) ? Take out of service -> ME",
    Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
         statement=Decision_a(input=BOOL_a(
             op='NOT', operands=INST_PROJ_a(iset=INST_a(
                 components=[PATH_a(hops=[R_a(rnum='R2'), N_a(name='Shaft')])]),
                 projection=Projection_a(expand=None, attrs=[N_a(name='In service')]))),
             true_result=Comp_Statement_Set_a(statement=
                     Signal_a(event='Take out of service', supplied_params=[],
                              dest=Signal_Dest_a(target_iset=N_a(name='ME'),
                              assigner_partition=N_a(name=None), delay=0)), block=None),
             false_result=None),
         block=None), output_token=None))]


@pytest.mark.parametrize("text, expected", actions)
def test_state_action(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse[0] == expected
