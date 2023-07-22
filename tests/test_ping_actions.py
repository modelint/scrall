# simple tests

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import Execution_Unit_a, Signal_a, Signal_Dest_a, N_a, INST_a, PATH_a, R_a,\
    Inst_Assignment_a, Flow_Output_a, Selection_a, BOOL_a, Supplied_Parameter_a, Call_a, Op_a, IN_a

actions = [
    ("Try redirect( ^new dest ) -> /R53/Cabin",
        Execution_Unit_a(input_tokens=None, output_tokens=None,
                         action_group=Signal_a(event='Try redirect', supplied_params=[[
                                 Supplied_Parameter_a(pname='new dest', sval=IN_a(name='new dest'))]],
                                               dest=Signal_Dest_a(target_iset=INST_a(
                                                   components=[
                                                       PATH_a(hops=[R_a(rnum='R53'), N_a(name='Cabin')])]),
                                                   assigner_partition=N_a(name=None), delay=0)))
    ),
    ("TRAN.Go to floor( Dest floor: ^new dest, Shaft )",
        Execution_Unit_a(input_tokens=None, output_tokens=None,
                         action_group=Call_a(call=INST_a(components=[
                             Op_a(owner='TRAN', op_name='Go to floor',
                                  supplied_params=[
                                      Supplied_Parameter_a(pname='Dest floor', sval=IN_a(name='new dest')),
                                      Supplied_Parameter_a(pname='Shaft', sval=N_a(name='Shaft'))], order=None)]),
                             op_chain=None))
    ),
    ("Change requested -> me",
     Execution_Unit_a(input_tokens=None, output_tokens=None,
                      action_group=Signal_a(event='Change requested', supplied_params=[],
                                            dest=Signal_Dest_a(target_iset=N_a(name='me'),
                                                               assigner_partition=N_a(name=None), delay=0)))
     ),
    ("shaft aslevs ..= /R2/R28/Shaft Level/R3/Accessible Shaft Level\n",
     Execution_Unit_a(input_tokens=None, output_tokens=None,
                      action_group=Inst_Assignment_a(
                          lhs=Flow_Output_a(name=N_a(name='shaft aslevs'), exp_type=None), card='M',
                          rhs=INST_a(components=[
                              PATH_a(hops=[R_a(rnum='R2'),
                                           R_a(rnum='R28'),
                                           N_a(name='Shaft Level'),
                                           R_a(rnum='R3'),
                                           N_a(name='Accessible Shaft Level')])]),
                          X=(0, 62)))
     ),
    ("requested stops ..= shaft aslevs( Stop requested: avalue )\n",
     Execution_Unit_a(input_tokens=None, output_tokens=None,
                      action_group=Inst_Assignment_a(
                          lhs=Flow_Output_a(name=N_a(name='requested stops'), exp_type=None), card='M',
                          rhs=INST_a(components=[N_a(name='shaft aslevs'),
                                                 Selection_a(card='*',
                                                             criteria=BOOL_a(op=['=='],
                                                                             operands=[
                                                                                 N_a(name='Stop requested'),
                                                                                 N_a(name='avalue')]))]),
                          X=(0, 58)))
     ),
]


@pytest.mark.parametrize("text, expected", actions)
def test_signal_action(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse == expected
