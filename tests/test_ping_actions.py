# simple tests

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import Execution_Unit_a, Signal_a, Signal_Dest_a, N_a, INST_a, PATH_a, R_a,\
    Inst_Assignment_a, Flow_Output_a, Selection_a, BOOL_a

actions = [
    ("shaft aslevs ..= /R2/R28/Shaft Level/R3/Accessible Shaft Level\n",
     Execution_Unit_a(input_tokens=None, output_tokens=None,
                      action_group=Inst_Assignment_a(
                          lhs=Flow_Output_a(name=N_a(name='shaft aslevs'), exp_type=None), card='Mc',
                          rhs=INST_a(components=[
                              PATH_a(hops=[R_a(rnum='R2'),
                                           R_a(rnum='R28'),
                                           N_a(name='Shaft Level'),
                                           R_a(rnum='R3'),
                                           N_a(name='Accessible Shaft Level')])])))
     ),
    ("requested stops ..= shaft aslevs( Stop requested: avalue )\n",
     Execution_Unit_a(input_tokens=None, output_tokens=None,
                      action_group=Inst_Assignment_a(
                          lhs=Flow_Output_a(name=N_a(name='requested stops'), exp_type=None), card='Mc',
                          rhs=INST_a(components=[N_a(name='shaft aslevs'),
                                                 Selection_a(card='*',
                                                             criteria=BOOL_a(op=['=='],
                                                                             operands=[
                                                                                 [N_a(name='Stop requested')],
                                                                                 [N_a(name='avalue')]]))])))
     ),
]


@pytest.mark.parametrize("text, expected", actions)
def test_signal_action(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse == expected
