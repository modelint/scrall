# simple tests

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import Execution_Unit_a, Signal_a, Signal_Dest_a, N_a, INST_a, PATH_a, R_a, \
    Seq_Statement_Set_a

actions = [
    ("Change requested -> ME",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
           statement=Signal_a(event='Change requested', supplied_params=[],
                              dest=Signal_Dest_a(target_iset=N_a(name='ME'),
                              assigner_partition=N_a(name=None), delay=0)),
           block=None), output_token=None)
     ),
    ("Ready to go -> /R53/Transfer",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(input_tokens=None,
           statement=Signal_a(event='Ready to go', supplied_params=[], dest=Signal_Dest_a(
               target_iset=INST_a(
                   components=[PATH_a(hops=[R_a(rnum='R53'), N_a(name='Transfer')])]),
               assigner_partition=N_a(name=None), delay=0)),
           block=None), output_token=None)
     ),
]


@pytest.mark.parametrize("text, expected", actions)
def test_signal_action(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse[0] == expected
