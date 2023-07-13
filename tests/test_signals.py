from src.scrall.parse.parser import ScrallParser


def test_simple():
    action_text = "Change requested -> me\n"
    result = ScrallParser.parse_text(scrall_text=action_text, debug=False)
    print(result)
    assert result
