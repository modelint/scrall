# test delete action

import pytest
from scrall.parse.parser import ScrallParser
from scrall.parse.visitor import Execution_Unit_a, N_a, INST_a, PATH_a, R_a, Seq_Statement_Set_a, Delete_Action_a

actions = [
    ("!* siamese, /R1/Cat",
        Execution_Unit_a(statement_set=Seq_Statement_Set_a(
            input_tokens=None, statement=Delete_Action_a(
                instance_sets=[N_a(name='siamese'),
                   INST_a(components=[PATH_a(hops=[R_a(rnum='R1'),
                       N_a(name='Cat')])])]), block=None), output_token=None)
     ),
]


@pytest.mark.parametrize("text, expected", actions)
def test_delete_action(text, expected):
    parse = ScrallParser.parse_text(scrall_text=text, debug=False)[0]
    print(parse)
    assert parse[0] == expected
