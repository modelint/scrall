# simple tests

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import (Execution_Unit_a, Signal_a, Signal_Dest_a, N_a, INST_a, PATH_a, R_a,
    Seq_Statement_Set_a, Supplied_Parameter_a, External_Signal_a, Decision_a, Comp_Statement_Set_a)

actions = [
    ("Time to close ->* me",
     Execution_Unit_a(
         statement_set=Seq_Statement_Set_a(
             input_tokens=[],
             statement=Signal_a(
                 event='Time to close',
                 supplied_params=[],
                 dest=Signal_Dest_a(target_iset=N_a(name='me'), assigner_dest=None, delay=0, cancel=True)),
             block=None),
         output_token=None)
     ),
    ("Goto floor( Dest floor: my level) -> ~",
     Execution_Unit_a(
         statement_set=Seq_Statement_Set_a(
             input_tokens=[],
             statement=External_Signal_a(
                 event='Goto floor',
                 supplied_params=[
                     [Supplied_Parameter_a(pname='Dest floor', sval=N_a(name='my level'))]
                 ]), block=None),
         output_token=None)
     ),
    ("Change requested -> me",
        Execution_Unit_a(
            statement_set=Seq_Statement_Set_a(
                input_tokens=[],
                statement=Signal_a(
                    event='Change requested',
                    supplied_params=[],
                    dest=Signal_Dest_a(target_iset=N_a(name='me'), assigner_dest=None, delay=0, cancel=False)),
                block=None),
            output_token=None)
     ),
    ("Ready to go -> /R53/Transfer",
        Execution_Unit_a(
            statement_set=Seq_Statement_Set_a(
                input_tokens=[],
                statement=Signal_a(
                    event='Ready to go',
                    supplied_params=[],
                    dest=Signal_Dest_a(target_iset=INST_a(
                        components=[PATH_a(hops=[R_a(rnum='R53'), N_a(name='Transfer')])]
                    ), assigner_dest=None, delay=0, cancel=False)
                ),
                block=None),
            output_token=None)
     ),
    ("destination aslev?\n"
     "    Transfer created -> : No destination -> me",
     Execution_Unit_a(
         statement_set=Seq_Statement_Set_a(
             input_tokens=[],
             statement=Decision_a(
                 input=N_a(name='destination aslev'),
                 true_result=Comp_Statement_Set_a(
                     statement=Signal_a(
                         event='Transfer created',
                         supplied_params=[], dest=None), block=None),
                 false_result=Comp_Statement_Set_a(
                     statement=Signal_a(
                         event='No destination',
                         supplied_params=[],
                         dest=Signal_Dest_a(
                             target_iset=N_a(name='me'), assigner_dest=None, delay=0, cancel=False
                         )), block=None
                 )), block=None), output_token=None)
     ),
]


@pytest.mark.parametrize("text, expected", actions)
def test_signal_action(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse[0] == expected
