# simple tests

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import Execution_Unit_a, Signal_a, Signal_Dest_a, N_a, INST_a, PATH_a, R_a,\
    Inst_Assignment_a, Flow_Output_a, Criteria_Selection_a, Rank_Selection_a, BOOL_a, Supplied_Parameter_a, Call_a, Op_a, IN_a, \
    Table_Assignment_a, TEXPR_a, Projection_a, Seq_Statement_Set_a, Scalar_Assignment_a, Scalar_RHS_a, \
    Sequence_Token_a, Case_a, Switch_a, Enum_a, Output_Flow_a, INST_PROJ_a, Comp_Statement_Set_a

actions = [
    ("{\n    a = b\n    c = d\n}<1>",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None, statement=None, block=[

            Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
               statement=Scalar_Assignment_a(
                   lhs=[Flow_Output_a(name=N_a(name='a'), exp_type=None)],
                   rhs=Scalar_RHS_a(expr=N_a(name='b'), attrs=None)), block=None), output_token=None),

            Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
               statement=Scalar_Assignment_a(
                  lhs=[Flow_Output_a(name=N_a(name='c'), exp_type=None)],
                  rhs=Scalar_RHS_a(expr=N_a(name='d'), attrs=None)), block=None), output_token=None)]),
               output_token=Sequence_Token_a(name='1'))),
    ("^dir? {\n    _up:\n        a = b\n    _down:\n        a = c\n}\n",
            Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
                statement=Switch_a(input_flow=IN_a(name='dir'), cases=[
                    Case_a(enums=['up'], comp_statement_set=Comp_Statement_Set_a(
                        statement=Scalar_Assignment_a(
                            lhs=[Flow_Output_a(name=N_a(name='a'), exp_type=None)],
                            rhs=Scalar_RHS_a(expr=N_a(name='b'), attrs=None)), block=None)),
                    Case_a(enums=['down'], comp_statement_set=Comp_Statement_Set_a(
                        statement=Scalar_Assignment_a(
                            lhs=[Flow_Output_a(name=N_a(name='a'), exp_type=None)],
                            rhs=Scalar_RHS_a(expr=N_a(name='c'), attrs=None)), block=None))]),
                block=None), output_token=None)
     ),

    ("stop here floors #= shaft aslevs( Stop requested ).Floor",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
            statement=Table_Assignment_a(type='implicit', assign_tuple=False,
                lhs='stop here floors',
                rhs=TEXPR_a(table=INST_a(components=[N_a(name='shaft aslevs')]), hexpr=None,
                            selection=Criteria_Selection_a(card='*', criteria=N_a(name='Stop requested')),
                            projection=Projection_a(expand=None, attrs=[N_a(name='Floor')])),
            X=(0, 56)), block=None), output_token=None)),
    ("Try redirect( ^new dest ) -> /R53/Cabin",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
            statement=Signal_a(event='Try redirect', supplied_params=[
                [Supplied_Parameter_a(pname='new dest', sval=IN_a(name='new dest'))]],
                    dest=Signal_Dest_a(target_iset=
                       INST_a(components=[PATH_a(hops=[R_a(rnum='R53'), N_a(name='Cabin')])]),
                                       assigner_partition=N_a(name=None), delay=0)),
            block=None), output_token=None)
    ),
    ("TRAN.Go to floor( Dest floor: ^new dest, Shaft )",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
            statement=Call_a(call=INST_a(components=[Op_a(owner='TRAN', op_name='Go to floor',
                          supplied_params=[Supplied_Parameter_a(pname='Dest floor', sval=IN_a(name='new dest')),
                                           Supplied_Parameter_a(pname='Shaft', sval=N_a(name='Shaft'))])]
                                         ), op_chain=None),
            block=None), output_token=None)
    ),
    ("Change requested -> ME",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
            statement=Signal_a(event='Change requested', supplied_params=[],
                               dest=Signal_Dest_a(target_iset=N_a(name='ME'),
                               assigner_partition=N_a(name=None), delay=0)),
            block=None), output_token=None)
     ),
    ("shaft aslevs ..= /R2/R28/Shaft Level/R3/Accessible Shaft Level",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
            statement=Inst_Assignment_a(
                lhs=Flow_Output_a(name=N_a(name='shaft aslevs'), exp_type=None), card='M',
                rhs=INST_a(components=[PATH_a(hops=[
                    R_a(rnum='R2'), R_a(rnum='R28'), N_a(name='Shaft Level'), R_a(rnum='R3'),
                    N_a(name='Accessible Shaft Level')])]),
            X=(0, 62)), block=None), output_token=None)
     ),
    ("requested stops ..= shaft aslevs( Stop requested: avalue )",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
            statement=Inst_Assignment_a(
                lhs=Flow_Output_a(name=N_a(name='requested stops'), exp_type=None), card='M',
                rhs=INST_a(components=[N_a(name='shaft aslevs'), Criteria_Selection_a(card='*',
                             criteria=BOOL_a(op='==', operands=[N_a(name='Stop requested'), N_a(name='avalue')]))]),
            X=(0, 58)), block=None), output_token=None)
     ),
    ("=>> Accessible Shaft Level( Floor: nearest dest.Floor; Shaft )",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None, statement=Output_Flow_a(
            output=INST_PROJ_a(iset=INST_a(components=[N_a(name='Accessible Shaft Level'),
                 Criteria_Selection_a(card='*', criteria=BOOL_a(op='AND', operands=[
                     BOOL_a(op='==', operands=[N_a(name='Floor'),
                           INST_PROJ_a(iset=N_a(name='nearest dest'),
                                 projection=Projection_a(expand=None, attrs=[N_a(name='Floor')]))]),
                                 N_a(name='Shaft')]))]), projection=None)), block=None), output_token=None
                         )
    ),
]


@pytest.mark.parametrize("text, expected", actions)
def test_ping_action(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse[0] == expected
