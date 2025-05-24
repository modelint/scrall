# selection tests

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import Execution_Unit_a, Signal_a, Signal_Dest_a, N_a, INST_a, PATH_a, R_a,\
    Inst_Assignment_a, Flow_Output_a, Rank_Selection_a, Criteria_Selection_a, BOOL_a, Op_a, Enum_a, MATH_a, Seq_Statement_Set_a

actions = [
    ("s ..= Shaft(Inservice; Cleared)",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
           statement=Inst_Assignment_a(
               lhs=Flow_Output_a(name=N_a(name='s'), exp_type=None), card='M',
               rhs=INST_a(components=[N_a(name='Shaft'), Criteria_Selection_a(card='*',
                          criteria=BOOL_a(op='AND', operands=[N_a(name='Inservice'), N_a(name='Cleared')]))]),
               X=(0, 31)), block=None), output_token=None)
     ),
    ("c ..= Cabin(Speed > slowest + buffer)",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
           statement=Inst_Assignment_a(
               lhs=Flow_Output_a(name=N_a(name='c'), exp_type=None), card='M',
               rhs=INST_a(components=[N_a(name='Cabin'), Criteria_Selection_a(card='*',
                  criteria=BOOL_a(op='>', operands=[N_a(name='Speed'),
                           MATH_a(op='+', operands=[N_a(name='slowest'), N_a(name='buffer')])]))]),
               X=(0, 37)), block=None), output_token=None)
    ),
    ("c ..= Cabin(Speed > slowest)",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
           statement=Inst_Assignment_a(
               lhs=Flow_Output_a(name=N_a(name='c'), exp_type=None), card='M',
               rhs=INST_a(components=[N_a(name='Cabin'), Criteria_Selection_a(card='*',
                       criteria=BOOL_a(op='>', operands=[N_a(name='Speed'), N_a(name='slowest')]))]),
           X=(0, 28)), block=None), output_token=None)
     ),
    ("s ..= Shaft(In service: TRUE)",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
             statement=Inst_Assignment_a(
                 lhs=Flow_Output_a(name=N_a(name='s'), exp_type=None), card='M',
                 rhs=INST_a(components=[N_a(name='Shaft'), Criteria_Selection_a(card='*',
                        criteria=BOOL_a(op='==', operands=[N_a(name='In service'), 'TRUE']))]),
             X=(0, 29)), block=None), output_token=None)
     ),
    ("s ..= Shaft(In service)",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
              statement=Inst_Assignment_a(lhs=Flow_Output_a(name=N_a(name='s'), exp_type=None), card='M',
                                          rhs=INST_a(components=[N_a(name='Shaft'), Criteria_Selection_a(card='*',
                                              criteria=N_a(name='In service'))]),
              X=(0, 23)), block=None), output_token=None)
     ),
    ("x .= Bank(Max close attempts: (v or x) or Average cabin speed > mspeed)",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
              statement=Inst_Assignment_a(
                  lhs=Flow_Output_a(name=N_a(name='x'), exp_type=None), card='1',
                  rhs=INST_a(components=[N_a(name='Bank'), Criteria_Selection_a(card='*',
                      criteria=BOOL_a(op='OR', operands=[
                          BOOL_a(op='==', operands=[
                              N_a(name='Max close attempts'),
                              BOOL_a(op='OR', operands=[N_a(name='v'), N_a(name='x')])]),
                          BOOL_a(op='>', operands=[N_a(name='Average cabin speed'), N_a(name='mspeed')])]))]),
              X=(0, 71)), block=None), output_token=None)
    ),
    ("x ..= car.findsome()(color: _red)",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
              statement=Inst_Assignment_a(
                  lhs=Flow_Output_a(name=N_a(name='x'), exp_type=None), card='M',
                  rhs=INST_a(components=[Op_a(owner='car', op_name='findsome', supplied_params=[]),
                                         Criteria_Selection_a(card='*', criteria=BOOL_a(op='==',
                                             operands=[N_a(name='color'), Enum_a(value=N_a(name='red'))]))]),
              X=(0, 33)), block=None), output_token=None)
     ),
]


@pytest.mark.parametrize("text, expected", actions)
def test_selection(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text + '\n', debug=False)[0]
    print(parse)
    assert parse[0] == expected
