# selection tests

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import Execution_Unit_a, Signal_a, Signal_Dest_a, N_a, INST_a, PATH_a, R_a,\
    Inst_Assignment_a, Flow_Output_a, Selection_a, BOOL_a, Op_a, Enum_a, MATH_a

actions = [
    ("s ..= Shaft(Inservice; Cleared)", Execution_Unit_a(input_tokens=None, output_tokens=None,
        action_group=Inst_Assignment_a(lhs=Flow_Output_a(name=N_a(name='s'), exp_type=None), card='M',
           rhs=INST_a(components=[N_a(name='Shaft'), Selection_a(card='*',
                 criteria=BOOL_a(op='AND', operands=[N_a(name='Inservice'), N_a(name='Cleared')]))])))
     ),
    ("c ..= Cabin(Speed > slowest + buffer)", Execution_Unit_a(input_tokens=None, output_tokens=None,
        action_group=Inst_Assignment_a(lhs=Flow_Output_a(name=N_a(name='c'), exp_type=None), card='M',
            rhs=INST_a(components=[N_a(name='Cabin'), Selection_a(card='*',
                criteria=BOOL_a(op='>', operands=[N_a(name='Speed'),
                                                  MATH_a(op='+', operands=[
                                                      N_a(name='slowest'), N_a(name='buffer')])]))])))
    ),
    ("c ..= Cabin(Speed > slowest)", Execution_Unit_a(input_tokens=None, output_tokens=None,
        action_group=Inst_Assignment_a(lhs=Flow_Output_a(name=N_a(name='c'), exp_type=None), card='M',
            rhs=INST_a(components=[N_a(name='Cabin'), Selection_a(card='*',
                criteria=BOOL_a(op='>', operands=[N_a(name='Speed'), N_a(name='slowest')]))])))
     ),
    ("s ..= Shaft(In service: True)", Execution_Unit_a(input_tokens=None, output_tokens=None,
        action_group=Inst_Assignment_a(lhs=Flow_Output_a(name=N_a(name='s'), exp_type=None), card='M',
            rhs=INST_a(components=[N_a(name='Shaft'), Selection_a(card='*',
               criteria=BOOL_a(op=['=='], operands=[N_a(name='In service'), 'true']))])))
     ),
    ("s ..= Shaft(In service)", Execution_Unit_a(input_tokens=None, output_tokens=None,
        action_group=Inst_Assignment_a(lhs=Flow_Output_a(name=N_a(name='s'), exp_type=None), card='M',
            rhs=INST_a(components=[N_a(name='Shaft'), Selection_a(card='*',
               criteria=N_a(name='In service'))])))
     ),
    ("x .= Bank(Max close attempts: (v or x) or Average cabin speed > mspeed)",
     Execution_Unit_a(input_tokens=None, output_tokens=None,
                      action_group=Inst_Assignment_a(lhs=Flow_Output_a(name=N_a(name='x'), exp_type=None), card='1',
                      rhs=INST_a(components=[
                          N_a(name='Bank'),
                          Selection_a(card='*',
                                      criteria=BOOL_a(op='OR', operands=[BOOL_a(op=['=='],
                                        operands=[N_a(name='Max close attempts'),
                                                  BOOL_a(op='OR', operands=[N_a(name='v'), N_a(name='x')])]),
                                                                   BOOL_a(op='>', operands=[
                                                                       N_a(name='Average cabin speed'),
                                                                       N_a(name='mspeed')])]))])))
     ),
    ("x ..= car.findsome()(color: _red)",
     Execution_Unit_a(input_tokens=None, output_tokens=None,
                      action_group=Inst_Assignment_a(lhs=Flow_Output_a(name=N_a(name='x'), exp_type=None), card='M',
                                                     rhs=INST_a(components=[
                                                         Op_a(owner='car', op_name='findsome', supplied_params=[],
                                                              order=None),
                                                         Selection_a(card='*', criteria=BOOL_a(op=['=='], operands=[
                                                                 N_a(name='color'), Enum_a(value=N_a(name='red'))]))])
                                                     ))
     ),
]


@pytest.mark.parametrize("text, expected", actions)
def test_signal_action(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text + '\n', debug=False)[0]
    print(parse)
    assert parse == expected
