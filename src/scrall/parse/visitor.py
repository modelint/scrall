""" visitor.py - current tests """
from arpeggio import PTNodeVisitor
from collections import namedtuple
from scrall.exceptions import ScrallMissingParameterName
import logging

_logger = logging.getLogger(__name__)

# Here we define named tuples that we use to package up the parsed data
# and return in the visit result.
Supplied_Parameter_a = namedtuple('Supplied_Parameter_a', 'pname sval')
"""Parameter name and flow name pair for a set of supplied parameters"""
Op_a = namedtuple('Op_a', 'owner op_name supplied_params')
Scalar_op_a = namedtuple('Scalar_op_a', 'name supplied_params')
Call_a = namedtuple('Call_a', 'call op_chain')
Scalar_Call_a = namedtuple('Scalar_Call_a', 'call')
"""The subject of a call could be an instance set (method) or an external entity (ee operation)"""
Attr_Access_a = namedtuple('Attr_Access_a', 'cname its attr')
Rank_Selection_a = namedtuple('Rank_Selection_a', 'card rankr attr')
Criteria_Selection_a = namedtuple('Criteria_Selection_a', 'card criteria')
Inst_Assignment_a = namedtuple('Inst_Assignment_a', 'lhs card rhs X')
EE_Signal_a = namedtuple('EE_Signal_a', 'event supplied_params ee')
Signal_a = namedtuple('Signal_a', 'event supplied_params dest')
"""Signal sent to trigger event at destination with optional supplied parameters"""
Signal_Action_a = namedtuple('Signal_Action_a', 'event supplied_params dest delay assigner_partition')
Signal_Dest_a = namedtuple('Signal_Dest_a', 'target_iset assigner_partition delay')
Signal_Choice_a = namedtuple('Signal_Choice_a', 'decision true_signal false_signal')
Sequence_Token_a = namedtuple('Sequence_Token_a', 'name')
Execution_Unit_a = namedtuple('Execution_Unit_a', 'statement_set output_token')
Seq_Statement_Set_a = namedtuple('Seq_Statement_Set_a', 'input_tokens statement block')
Comp_Statement_Set_a = namedtuple('Comp_Statement_Set_a', 'statement block')
Decision_a = namedtuple('Decision_a', 'input true_result false_result')
Delete_Action_a = namedtuple('Delete_Action_a', 'instance_sets')
Case_a = namedtuple('Case_a', 'enums comp_statement_set')
Switch_a = namedtuple('Switch_a', 'input_flow cases')
MATH_a = namedtuple('MATH_a', 'op operands')
TOP_a = namedtuple('TOP_a', 'op operands')
UNARY_a = namedtuple('UNARY_a', 'op operand')
BOOL_a = namedtuple('BOOL_a', 'op operands')
"""Boolean operation returns true or false"""
Scalar_Assignment_a = namedtuple('Scalar_Assignment_a', 'lhs rhs')
Table_Assignment_a = namedtuple('Table_Assignment_a', 'type assign_tuple lhs rhs X')
Scalar_RHS_a = namedtuple('Scalar_RHS_a', 'expr attrs')
Flow_Output_a = namedtuple('Flow_Output_a', 'name exp_type')
PATH_a = namedtuple('PATH_a', 'hops')
INST_a = namedtuple('INST_a', 'components')
INST_PROJ_a = namedtuple('INST_PROJ_a', 'iset projection')
TEXPR_a = namedtuple('TEXPR_a', 'table hexpr selection projection')
R_a = namedtuple('R_a', 'rnum')
IN_a = namedtuple('IN_a', 'name')
Enum_a = namedtuple('Enum_a', 'value')
Order_name_a = namedtuple('Order_name_a', 'order name')
N_a = namedtuple('N_a', 'name')
Op_chain_a = namedtuple('Op_chain_a', 'components')
"""Input parameter"""
Reflexive_select_a = namedtuple('Reflexive_select_a', 'expr compare position')
Type_expr_a = namedtuple('Type_expr_a', 'type selector')
Attr_value_init_a = namedtuple('Attr_value_init_a', 'attr scalar_expr')
To_ref_a = namedtuple('To_ref_a', 'rnum iset1 iset2')
Update_ref_a = namedtuple('Update_ref_a', 'iset to_ref')
New_inst_a = namedtuple('New_inst_a', 'cname attrs rels')
New_lineage_a = namedtuple('New_lineage_a', 'inits')
Output_Flow_a = namedtuple('Output_Flow_a', 'output')
Projection_a = namedtuple('Projection_a', 'expand attrs')
# Tables
Attr_Type_a = namedtuple('Attr_Type_a', 'attr_name type_name')
Attr_Val_a = namedtuple('Attr_Val_a', 'attr_name attr_value')
Class_to_Table_a = namedtuple('Class_to_Table_a', 'cname selection projection')
Table_Def_a= namedtuple('Table_Def_a', 'name header')
Rename_a = namedtuple('Rename_a', 'from_name to_name')
Iteration_a = namedtuple('Iteration_a', 'order statement_set')
Migration_a = namedtuple('Migration_a','from_inst to_subclass')
Rank_a = namedtuple('Rank_a', "card extent")


rank_symbol = {'^+': "greatest", '^-': "least"}

table_op = {
    '^': 'INTERSECT',
    '+': 'UNION',
    '-': 'MINUS',
    '*': 'TIMES',
    '##': 'JOIN',
}

def logop(c):
    """
    If an operator is detected at some level of nesting, log its detection.
    This makes it easy to ignore nested levels where the operand is simply passed through.

    :param c:  visited children
    :return:
    """
    found_keys = c.results.keys()
    if len(found_keys) > 1:
        key_names = [k for k in found_keys]
        _logger.info(f" >> {key_names[1]} {c.results[key_names[1]][0]}")

def getresult(t: str, c):
    """
    Returns the first element of the specified term in the parse children.results
    dictionary if the term is present, otherwise None.

    :param t:  Name of some parse term
    :param c:  Children
    :return:   The term result or None
    """
    return None if t not in c.results else c.results[t][0]


class ScrallVisitor(PTNodeVisitor):
    """
    Based on Arpeggio's generic node visitor

    Here we visit each node of the abstract tree created by the Scrall parser
    and return data in a format useful for validating a user's action language
    and populating the Shlaer-Mellor metamodel.

    See the scrall.peg file for the formal Scrall grammar.

    The comments for each node visitor includes a more or less recent copy of the
    relevant grammar syntax at the top of each visitor documentation block with
    whitespace elements removed for easy reading.

    When in doubt, consult the scrall.peg file.

    Also consult the wiki in Leon Starr's Scrall repo for a full description of Scrall
    and examples of usage.

    The node and children parameters are rerquired for each visit method and may
    or may not be referenced. Since they are uniform throughout, we do not include
    them in in the comments. See the arpeggio docs for the basics of abstract tree
    visiting.
    """

    # Activity structure
    @classmethod
    def visit_activity(cls, node, children):
        """
        This is the root node. All Scrall language is built up to define a
        single Shlaer-Mellor activity.

        An activity is built up from any number of execution units, including zero.
        It is perfectly okay to define an empty, non-functional activity. This happens
        whenever you define a state, for example, which represents a context, but that does
        not trigger any computation or communication.

        Here we just remove any whitespace and return only the execution units.

        The EOF symbol is a standard terminator at the root level for Arpeggio grammars.
        It signals the parser that there is no more text to parse.
        """
        _logger.info('activity = LINEWRAP* execution_unit* EOF')
        _logger.info(f'  :: {node.value}')

        _logger.info(f"< {children}")
        result = [c for c in children if c]
        _logger.info(f"  -> {result}")
        return result

    @classmethod
    def visit_execution_unit(cls, node, children):
        """
        When a statement_set completes execution it may enable a single output token.

        An output token represents an outgoing Sequence Flow.
        Any output token may feed into any number of other sequenced_statement_sets in the form of an input token.

        Every execution unit is terminated by a new line.
        """
        _logger.info('LINEWRAP* statement_set sequence_token? LINEWRAP+')
        _logger.info(f'  :: {node.value}')
        _logger.info(f">> {[k for k in children.results.keys()]}")

        _logger.info(f"  < {children}")
        output_token = getresult('sequence_token', children)
        st_set = getresult('statement_set', children)
        result = Execution_Unit_a(output_token=output_token, statement_set=st_set)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_statement_set(cls, node, children):

        _logger.info('statement_set = SP* sequenced_statement_set / component_statement_set')
        _logger.info(f'  :: {node.value}')
        _logger.info(f">> {[k for k in children.results.keys()]}")

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_sequenced_statement_set(cls, node, children):

        _logger.info('sequenced_statement_set = sequence_token* (block / statement)')
        _logger.info(f'  :: {node.value}')
        _logger.info(f">> {[k for k in children.results.keys()]}")

        _logger.info(f"  < {children}")
        input_tokens = getresult('sequence_token', children)
        b = getresult('block', children)
        s = getresult('statement', children)
        result = Seq_Statement_Set_a(input_tokens=input_tokens, statement=s, block=b)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_component_statement_set(cls, node, children):

        _logger.info('component_statement_set = block / statement')
        _logger.info(f'  :: {node.value}')
        _logger.info(f">> {[k for k in children.results.keys()]}")

        _logger.info(f"  > {children}")
        # b = None if 'block' not in children.results else children.results['block'][0]
        # s = None if 'statement' not in children.results else children.results['statement'][0]
        b = getresult('block', children)
        s = getresult('statement', children)
        result = Comp_Statement_Set_a(statement=s, block=b)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_block(cls, node, children):
        """
        We organize multiple execution units in a block (between brackets) when multiple
        execution units are enabled by the same decision, case, or input tokens.

        This correpsonds to the concept of one or more control flows on a data flow diagram
        enabling multiple processes.
        """
        _logger.info('block = "{" execution_unit* "}"')
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        _logger.info(f"  > pass")
        return children

    @classmethod
    def visit_statement(cls, node, children):
        """
        These are (or will be) a complete set of scrall statements. The ordering helps in some cases to prevent
        one type of statement from being mistaken for another during the parse. You can't backgrack in a peg
        grammar, so you need to match the pattern right on the first scan.

        There should be only one child element and it will be a named tuple defining the parsed action.
        """
        _logger.info('statement = table_assignment / new_lineage / new_instance / update_ref / delete / migration /'
                     ' scalar_assignment / signal_action / switch / decision / inst_assignment / call / iteration')
        _logger.info(f'  :: {node.value}')
        _logger.info(f">> {[k for k in children.results.keys()]}")

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_sequence_token(cls, node, children):
        """
         Named control flow
        """
        _logger.info(f'sequence_token = "<" token_name ">"')
        _logger.info(f'  :: {node.value}')
        _logger.info(f"  < {children}")
        result = Sequence_Token_a(name=children[0])
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_token_name(cls, node, children):
        """
        r'[A-Za-z0-9_]+'
        No spaces in token names, often single digit: <1>

        Since this is a terminal, we need to grab the name from the node.value
        """
        _logger.info("token_name = r'[A-Za-z0-9_]+'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = node.value
        _logger.info(f"  > {result}")
        return result

    # Table expressions
    @classmethod
    def visit_table_assignment(cls, node, children):
        _logger.info("table_assignment = explicit_table_assignment / implicit_table_assignment")
        _logger.info(f'  :: {node.value}')
        _logger.info(f">> {[k for k in children.results.keys()]}")

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    # Explicit table assignment
    @classmethod
    def visit_explicit_table_assignment(cls, node, children):

        _logger.info("explicit_table_assignment = table_def relation_assign_op table_value")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        atuple = True if children.results['relation_assign_op'][0] == '||=' else False
        result = Table_Assignment_a(assign_tuple=atuple, type='explicit', lhs=children.results['table_def'][0],
                                    rhs=children.results['table_value'][0], X=(node.position, node.position_end))
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_table_def(cls, node, children):

        _logger.info("table_def = name '[' attr_type_set? ']'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = Table_Def_a(name=children[0].name, header=[] if len(children) < 2 else children[1])
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_attr_type_set(cls, node, children):

        _logger.info("attr_type_set = attr_type_def (',' attr_type_def)*")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        _logger.info("  > pass")
        return children

    @classmethod
    def visit_attr_type_def(cls, node, children):

        _logger.info("token = name '::' name")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = Attr_Type_a(attr_name=children[0].name, type_name=children[1].name)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_table_value(cls, node, children):

        _logger.info("table_value = '{' row* '}'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        _logger.info(f"  > pass")
        return children

    @classmethod
    def visit_row(cls, node, children):

        _logger.info("row = '{' attr_value_set? '}'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = [] if not children else children[0]
        _logger.info(f"  > {result}")
        return result


    @classmethod
    def visit_attr_value_set(cls, node, children):

        _logger.info(f"attr_value_set = scalar_expr (',' scalar_expr)*")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        _logger.info(f"  > pass")
        return children

    # Implicit table assignment
    @classmethod
    def visit_implicit_table_assignment(cls, node, children):

        _logger.info("implicit_table_assignment = name relation_assign_op table_expr")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        atuple = True if children.results['relation_assign_op'][0] == '||=' else False
        result = Table_Assignment_a(assign_tuple=atuple, type='implicit', lhs=children[0].name,
                                    rhs=children.results['table_expr'][0], X=(node.position, node.position_end))
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_table_expr(cls, node, children):

        _logger.info("table_expr = table_operation")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_table_operation(cls, node, children):

        _logger.info("table_operation = table_term (TOP table_term)*")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        if len(children) == 1:
            result = children[0]
        else:
            result = TOP_a(children.results['TOP'][0], children.results['table_term'])
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_table_term(cls, node, children):

        _logger.info('table_term = (instance_set / "(" SP* table_expr SP* ")") header_expr? selection? projection?')
        _logger.info(f'  :: {node.value}')
        _logger.info(f">> {[k for k in children.results.keys()]}")

        _logger.info(f"  < {children}")

        # We always receive either an INST_a or an N_a, both instance sets, but N_a is just a name
        # without the trailing components.

        # Optional items
        h = children.results.get('header_expr')
        s = children.results.get('selection')
        p = children.results.get('projection')

        # We either have an instance set as INST_a or N_a or we have a table expression as TEXPR_a
        # Check the iset case first
        iset = children.results.get('instance_set')
        if iset:
            table = iset[0]
            # If we have an INST_a, extract the last component so we can see if it is a selection phrase
            # Otherwise, it's just an N_a and there can't be a selection component
            last_comp = None
            if type(table).__name__ == 'INST_a':
                last_comp = table.components[-1]

            if last_comp and type(last_comp).__name__ == 'Criteria_Selection_a':
                if s:
                    # We have two selection phrases. The first is terminating the instance set and the second is
                    # picked up as 's' above. We will take the first one and ignore the second,
                    # and issue a warning to the user.
                    _logger.warning(f"Two adjacent selection phrases in table assignment: "
                                    f"({last_comp})({s}) @<{node.position}-{node.position_end}>")
                # Make the last component the selection on this table and remove it from the iset
                s = last_comp
                table = INST_a(table.components[:-1])  # Drop the terminating selection component saves as s
        else:
            # It must be a table expression
            table = children.results.get('table_expr')[0]

        result = TEXPR_a(table=table, hexpr=None if not h else h[0], selection=s, projection=None if not p else p[0])
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_TOP(cls, node, children):

        _logger.info("TOP= '^' / '+' / '-' / '*' / '##'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = table_op[children[0]]
        _logger.info(f"  > {result}")
        return result

    # Table header operations
    @classmethod
    def visit_header_expr(cls, node, children):

        _logger.info("header_expr = [' column_op (',' column_op)* ']")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        _logger.info(f"  > pass")
        return children

    @classmethod
    def visit_column_op(cls, node, children):

        _logger.info('column_op = extend / rename_op')
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result


    @classmethod
    def visit_rename_op(cls, node, children):
        """
        """
        _logger.info('rename_op = name rename_attr')
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = Rename_a(from_name=children[0].name, to_name=children[1].name)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_rename_attr(cls, node, children):
        """
        """
        _logger.info('rename_attr = RENAME name')
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    # Decision and switch actions
    @classmethod
    def visit_decision(cls, node, children):
        """
        """
        _logger.info('decision = scalar_expr true_result false_result?')
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = Decision_a(
            input=children[0],
            true_result=children[1],
            false_result=None if len(children) < 3 else children[2]
        )
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_true_result(cls, node, children):
        """
        Actions to be executed when the decision evaluates to true
        """
        _logger.info('true_result = DECISION_OP action_group')
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_false_result(cls, node, children):
        """
        Actions to be executed when the decision evaluates to false
        """
        _logger.info('false_result = FALSE_RESULT_OP action_group')
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    # Switch action
    @classmethod
    def visit_switch(cls, node, children):
        """
        Rnum or boolean expr triggers case_block
        If rnum, the enums must be subclass names (verified outside parser)
        """
        _logger.info('switch = switch_input DECISION_OP SP* case_block')

        _logger.info(f'  :: {node.value}')
        _logger.info(f"  < {children}")

        result = Switch_a(
            input_flow=children.results['switch_input'][0],
            cases=children.results['case_block'][0]
        )
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_case_block(cls, node, children):
        """
        One or more cases between brackets
        """
        _logger.info("case_block = '{' LINEWRAP* case+ LINEWRAP*'}'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_case(cls, node, children):
        """
        One or more enumerated values that triggers an execution unit
        """
        _logger.info("case = LINEWRAP* trigger_set? SP* ':' LINEWRAP* component_statement_set")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        triggers = children.results.get('trigger_set')
        result = Case_a(
            enums=[] if not triggers else triggers[0],
            comp_statement_set=children.results['component_statement_set'][0]
        )
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_trigger_set(cls, node, children):
        """
        """
        _logger.info("trigger_set = enum_value (',' SP+ enum_value)*")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = [c.value.name for c in children]
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_enum_value(cls, node, children):
        """
        """
        _logger.info("enum_value = '.' name")

        result = Enum_a(children[0])
        _logger.info(f"  > {result}")
        return result

    # # Asynch service
    # @classmethod
    # def visit_asynch_service(cls, node, children):
    #     """
    #     name '.' signal_spec ASYNCH ee
    #     """
    #     result = Asynch_a(*children)

    @classmethod
    def visit_signal_action(cls, node, children):
        """
        """
        _logger.info("signal = signal_spec (signal_dest / ee_dest)")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        sdest = children.results.get('signal_dest')
        if sdest:
            result = Signal_a(
                event=children[0]['name'],
                supplied_params=children[0]['params'],
                dest=children[1]
            )
        else:
            result = EE_Signal_a(
                event=children[0]['name'],
                supplied_params=children[0]['params'],
                ee=children[1]
            )
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_signal_spec(cls, node, children):
        """
        """
        _logger.info("signal_spec = name supplied_params?")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        params = children.results.get('supplied_params', [])
        result = {'name': children[0].name, 'params': params}
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_ee_dest(cls, node, children):
        """
        """
        _logger.info("ee_dest = ASYNCH name")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_signal_dest(cls, node, children):
        """
        """
        _logger.info("signal_dest = SIGNAL_OP instance_set assigner_partition? delay?")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        iset = children[0]
        ap = children.results.get('assigner_partition')
        ap = None if not ap else ap[0]
        delay = children.results.get('delay')
        delay = 0 if not delay else delay[0]
        result = Signal_Dest_a(target_iset = iset, assigner_partition=N_a(ap), delay=delay)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_assigner_partition(cls, node, children):
        """
        An instance set that partitions an assigner
        """
        _logger.info("assigner_partition = '(' instance_set ')'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_delay(cls, node, children):
        """
       A time or time interval
        """
        _logger.info("delay = DELAY_OP scalar_expr")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    # Instance set assignment and selection
    @classmethod
    def visit_inst_assignment(cls, node, children):
        """
        """
        _logger.info("inst_assignment = name INST_ASSIGN instance_set")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = Inst_Assignment_a(
            lhs=children.results['flow_output'][0],
            card='1' if children.results['INST_ASSIGN'][0] == '.=' else 'M',
            rhs=children.results['instance_set'][0],
            X=(node.position, node.position_end)
        )
        _logger.info(f"  > {result}")
        return result


    @classmethod
    def visit_extend(cls, node, children):
        """
        """
        _logger.info("extend = rename_attr '(' op_chain ')'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_ITS(cls, node, children):
        _logger.info("ITS = 'ITS'")
        _logger.info(f'  :: {node.value}')

        result = 'ITS'
        _logger.info(f"  > {result}")
        return result

    # Synchronous method or operation
    @classmethod
    def visit_call(cls, node, children):
        """
        Post-parse verify that last element is an operation, otherwise invalid call
        """
        _logger.info("call = instance_set op_chain?")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        iset = children.results['instance_set'][0]
        opc = children.results.get('op_chain')
        result = Call_a(
            call=iset,
            op_chain=None if not opc else opc[0]
        )
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_operation(cls, node, children):
        """
        owner? '.' name supplied_params

        The results of an operation can be ordered ascending, descending
        The operation is invoked on the owner which may or may not be explicitly named
        If the owner is implicit, it could be 'ME' (the executing instance) or an operation on a type
        as determined from its parameters

        Name is the name of the operation
        """
        _logger.info("operation = owner? '.' name supplied_params")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        owner = children.results.get('owner')
        p = children.results.get('supplied_params')
        result = Op_a(
            owner='implicit' if not owner else owner[0],
            op_name=children.results['name'][0].name,
            supplied_params=[] if not p else p[0]
        )
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_supplied_params(cls, node, children):
        """
        Could be () or a list of multiple parameters
        """
        _logger.info("supplied_params = '(' (param (',' param)*)? ')'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children if children else []
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_param(cls, node, children):
        """
        If only a scalar_expr is present, it means that the supplied expr has the same name
        Ex: ( shaft id ) as that of the required parameter. Short for ( shaft id : shaft id ). This
        is a convenience that eliminates the need for name doubling in a supplied parameter set
        """
        _logger.info("param = (name ':')? scalar_expr")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        s = children.results['scalar_expr']
        s = s if len(s) > 1 else s[0]
        p = children.results.get('name')
        if not p and not (isinstance(s, N_a) or isinstance(s, IN_a)):
            _logger.error(f"Parameter name not supplied with expression value: [{children.results}]")
            raise ScrallMissingParameterName(children.results)
        result = Supplied_Parameter_a(pname=s.name if not p else p[0].name, sval=s)
        _logger.info(f"  > {result}")
        return result

    # Subclass migration
    @classmethod
    def visit_migration(cls, node, children):
        """
        """
        _logger.info("migration = instance_set? SP* '>>' SP* new_inst_int")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        iset = children.results.get('instance_set')
        iset = 'ME' if not iset else iset[0]
        dest_iset = children.results['new_inst_init'][0]
        result = Migration_a(from_inst=iset, to_subclass=dest_iset)
        _logger.info(f"  > {result}")
        return result

    # Iteration
    @classmethod
    def visit_iteration(cls, node, children):
        """
        """
        _logger.info("iteration = '<<' instance_set '>>' action_group")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = Iteration_a(*children)
        _logger.info(f"  > {result}")
        return result

    # Output flow
    def visit_output_flow(cls, node, children):
        """
        Final output of a synchronous activity (method, operation)
        """
        _logger.info("output_flow = OUTPUT SP+ scalar_expr")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")

        result = Output_Flow_a(children[0])
        _logger.info(f"  > {result}")
        return result


    # Instance set
    @classmethod
    def visit_instance_set(cls, node, children):
        """
        An instance set begins with a required name (instance flow) or a path. The path can then be followed
        by any sequence of selection, operation, and paths. The parser won't find two paths in sequence since
        any encounter path will be fully consumed
        """
        _logger.info("instance_set = new_instance / ((operation / prefix_name / path) (reflexive_selection / "
                     "selection / operation / path)*)")
        _logger.info(f">> {[k for k in children.results.keys()]}")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        if len(children) == 1 and isinstance(children[0], N_a):
            result = children[0]
        else:
            result = INST_a(children)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_rank_selection(cls, node, children):
        """
        CARD ', ' SP* RANKR name
        """
        _logger.info(f"{node.rule_name} = CARD ', ' SP* RANKR name")
        _logger.info(f">> {[k for k in children.results.keys()]}")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        card = children.results.get('CARD')[0]
        attr = children.results.get('name')
        rankr = children.results.get('RANKR')
        rankr_parse = rank_symbol[rankr[0]]
        result = Rank_Selection_a(card=card, rankr=rankr_parse, attr=attr)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_criteria_selection(cls, node, children):
        """
        (CARD ', ' SP* scalar_expr) / CARD / scalar_expr
        """
        _logger.info(f"{node.rule_name} = (CARD ', ' SP* scalar_expr) / CARD / scalar_expr")
        _logger.info(f">> {[k for k in children.results.keys()]}")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        explicit_card = children.results.get('CARD')
        card = '*' if not explicit_card else explicit_card[0]
        criteria = children.results.get('scalar_expr')
        if criteria:
            result = Criteria_Selection_a(card=card, criteria=criteria[0])
        else:
            result = [card]
        _logger.info(f"  > {result}")
        return result

    # Creation, deletion, and references
    @classmethod
    def visit_new_instance(cls, node, children):
        """
        create an instance of a class as an action
        """
        _logger.info("new_instance = '*' new_inst_init")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_new_lineage(cls, node, children):
        """
        create all instances of a lineage
        """
        _logger.info("new_lineage = '*[' new_inst_init (',' new_inst_init)+ ']'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = New_lineage_a(children)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_new_inst_init(cls, node, children):
        """
        specify class, attr inits, and any required references
        """
        _logger.info("new_inst_init = name attr_init? to_ref*")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        a = children.results.get('attr_init')
        r = children.results.get('to_ref')
        result = New_inst_a(cname=children[0], attrs=None if not a else a[0], rels=None if not r else r[0])
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_attr_init(cls, node, children):
        """
        all attrs to init for a new instance
        """
        _logger.info("attr_init = '(' (attr_value_init (',' attr_value_init)* ')'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_attr_value_init(cls, node, children):
        """
        """
        _logger.info("attr_value_init = (name ':' scalar_expr )*")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = Attr_value_init_a(attr=children[0], scalar_expr=children[1])
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_update_ref(cls, node, children):
        """
        A standalone reference
        """
        _logger.info("update_ref = instance_set? to_ref")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        iset = children.results.get('instance_set')
        iset = 'ME' if not iset else iset[0]
        result = Update_ref_a(iset=iset, to_ref=children[-1])
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_to_ref(cls, node, children):
        """
        non-associative or associative reference
        """
        _logger.info("to_ref = '&' rnum instance_set (',' instance_set)?")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        ref1 = None if len(children) < 2 else children[1]
        ref2 = None if len(children) < 3 else children[2]
        result = To_ref_a(rnum=children[0], iset1=ref1, iset2=ref2)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_delete(cls, node, children):
        """
        '!*' SP* instance_set (',' SP+ instance_set)
        """
        _logger.info("delete = '!*' SP* instance_set (',' SP+ instance_set)")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        iset = children.results.get('instance_set')
        result = Delete_Action_a(instance_sets=iset)
        _logger.info(f"  > {result}")
        return result

    # Scalar call
    @classmethod
    def visit_scalar_call(cls, node, children):
        """
        """
        _logger.info("scalar_call = scalar_expr")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = Scalar_Call_a(children)
        _logger.info(f"  > {result}")
        return result

    # Math and boolean operator precedence
    @classmethod
    def visit_scalar_assignment(cls, node, children):
        """
        """
        _logger.info("scalar_assignment = scalar_output_set SP* SCALAR_ASSIGN SP* scalar_expr projection?")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        sout_set = children.results['scalar_output_set'][0]
        expr = children.results['scalar_expr'][0]
        proj = children.results.get('projection')
        proj = None if not proj else proj[0]
        result = Scalar_Assignment_a(lhs=sout_set, rhs=Scalar_RHS_a(expr, proj))
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_scalar_output_set(cls, node, children):
        """
        """
        _logger.info("scalar_output_set = flow_output (',' flow_output)*")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_flow_output(cls, node, children):
        """
        """
        _logger.info("flow_output = name (TYPE_ASSIGN name)?")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        etyp = None if len(children) < 2 else children[1]
        result = Flow_Output_a(name=children[0], exp_type=etyp)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_projection(cls, node, children):
        """
        """
        _logger.info("projection = '.' '(' ( (ALL / (name (',' name)*) )? ')')")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        all = children.results.get('ALL')
        n = children.results.get('name')
        exp = 'ALL' if all else 'NONE' if not all and not n else None
        result = Projection_a(expand=exp, attrs=n)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_ALL(cls, node, children):
        """
        """
        _logger.info("ALL = '*'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = 'ALL'
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_scalar_expr(cls, node, children):
        """
        """
        _logger.info("scalar_expr = scalar_logical_or")
        # _logger.info(f'  :: {node.value}')

        # _logger.info(f"  < {children}")
        result = children[0]
        return result

    @classmethod
    def visit_scalar_logical_or(cls, node, children):
        """
        """
        if len(children) == 1:  # No OR operation
            result = children[0]
        else:
            result = BOOL_a('OR', children.results['scalar_logical_and'])

        if children[0] != result:
            _logger.info(f"{node.rule_name} = scalar_logical_and (OR scalar_logical_and)*")
            _logger.info(f'  :: {node.value}')
            logop(children)

            _logger.info(f"  < {children}")
            _logger.info(f"  > {result}")
        else:
            _logger.info(f"{node.rule_name} PASS")

        return result

    @classmethod
    def visit_scalar_logical_and(cls, node, children):
        """
        """
        if len(children) == 1:  # No AND operation
            result = children[0]
        else:
            result = BOOL_a('AND', children.results['equality'])

        if children[0] != result:
            _logger.info(f"  > {result}")
            _logger.info(f"{node.rule_name} = equality (AND equality)*")
            _logger.info(f'  :: {node.value}')
            logop(children)
            _logger.info(f"  < {children}")
            _logger.info(f"  > {result}")
        else:
            _logger.info(f"{node.rule_name} PASS")

        return result

    @classmethod
    def visit_equality(cls, node, children) -> BOOL_a:
        """
        """
        if len(children) == 1:
            result = children[0]
        else:
            # Convert ':' to '==' if found
            eq_op = '==' if children.results['EQUAL'][0] == ':' else children.results['EQUAL'][0]
            result = BOOL_a(eq_op, children.results['comparison'])

        if children[0] != result:
            _logger.info(f"{node.rule_name} = comparison (EQUAL comparison)*")
            _logger.info(f'  :: {node.value}')
            logop(children)
            _logger.info(f"  < {children}")
            _logger.info(f"  > {result}")
        else:
            _logger.info(f"{node.rule_name} PASS")

        return result

    @classmethod
    def visit_comparison(cls, node, children):
        """
        """
        if len(children) == 1:
            result = children[0]
        else:
            result = BOOL_a(children.results['COMPARE'][0], children.results['addition'])

        if children[0] != result:
            _logger.info(f"{node.rule_name} = addition (COMPARE addition)*")
            _logger.info(f'  :: {node.value}')
            logop(children)
            _logger.info(f"  < {children}")
            _logger.info(f"  > {result}")
        else:
            _logger.info(f"{node.rule_name} PASS")

        return result

    @classmethod
    def visit_addition(cls, node, children):
        """
        """
        if len(children) == 1:
            result = children[0]
        else:
            result = MATH_a(children.results['ADD'][0], children.results['factor'])

        if children[0] != result:
            _logger.info(f"{node.rule_name} = factor (ADD factor)*")
            _logger.info(f'  :: {node.value}')
            logop(children)
            _logger.info(f"  < {children}")
            _logger.info(f"  > {result}")
        else:
            _logger.info(f"{node.rule_name} PASS")

        return result

    @classmethod
    def visit_factor(cls, node, children):
        """
        """
        if len(children) == 1:
            result = children[0]
        else:
            result = MATH_a(children.results['MULT'][0], children.results['term'])

        if children[0] != result:
            _logger.info(f"{node.rule_name} = term (MULT term)*")
            _logger.info(f'  :: {node.value}')
            logop(children)
            _logger.info(f"  < {children}")
            _logger.info(f"  > {result}")
        else:
            _logger.info(f"{node.rule_name} PASS")

        return result

    @classmethod
    def visit_term(cls, node, children):
        """
        If the not or unary minus operations are not specified, returns whatever was parsed out earlier,
        either a simple scalar (attribute, attribute access, etc) or any scalar expression

        Otherwise, a unary minus expression nested inside a boolean not operation, or just the boolean not,
        or just the unary minus expressions individually are returned.
        """
        _logger.info("term = NOT? UNARY_MINUS? (scalar / scalar_expr)")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        s = children.results.get('scalar')
        s = s if s else children.results['scalar_expr']
        scalar = s[0]
        if len(children) == 1:
            result = scalar
        not_op = children.results.get('NOT')
        unary_minus = children.results.get('UNARY_MINUS')
        if unary_minus and not not_op:
            result = UNARY_a('-', scalar)
        if not_op and not unary_minus:
            result = BOOL_a('NOT', scalar)
        if unary_minus and not_op:
            result = BOOL_a('NOT', UNARY_a('-', scalar))
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_scalar(cls, node, children):
        """
        A scalar is either a simple value such as an enum or a variable name, TRUE/FALSE, etc OR
        it is a chain of operations like a.b(x,y).c.d with a preceding instance set such as a path, selection, etc.
        """
        _logger.info("scalar = value / QTY? scalar_chain")
        _logger.info(f'  :: {node.value}')
        _logger.info(f">> {[k for k in children.results.keys()]}")

        _logger.info(f"  < {children}")
        # Return value
        v = children.results.get('value')
        v = None if not v else v[0]
        if v:
            result = v
            _logger.info(f"  > {result}")
            return result

        # Cardinality
        qty = children.results.get('QTY')
        schain = children.results['scalar_chain'][0]
        if qty:
            result = qty[0], schain
            _logger.info(f"  > {result}")
            return result
        else:
            result = schain
            _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_QTY(cls, node, children):
        """
        """
        _logger.info("QTY = '??'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = 'QTY'
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_scalar_chain(cls, node, children):
        """
        """
        _logger.info("scalar_chain = (ITS op_chain) / ((scalar_source / instance_set projection?) op_chain?)")
        _logger.info(f'  :: {node.value}')
        _logger.info(f">> {[k for k in children.results.keys()]}")

        _logger.info(f"  < {children}")
        # ITS op_chain
        its = children.results.get('ITS')
        if its:
            op_chain = children.results['op_chain'][0]
            result = its, op_chain
            _logger.info(f"  > {result}")
            return result

        if len(children) == 1 and (isinstance(children[0], N_a) or (isinstance(children[0], IN_a))):
            result = children[0]
            _logger.info(f"  > {result}")
            return result

        # Instance set and projection are grouped for scalar ouput flow
        iset = children.results.get('instance_set')
        if iset:
            p = children.results.get('projection')
            result = INST_PROJ_a(iset=iset[0], projection=None if not p else p[0])
            _logger.info(f"  > {result}")
            return result
            # TODO: include opchain if supplied

        result = children
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_scalar_source(cls, node, children):
        """
        """
        _logger.info("scalar_source = type_selector / input_param")
        _logger.info(f'  :: {node.value}')
        _logger.info(f">> {[k for k in children.results.keys()]}")

        _logger.info(f"  < {children}")
        its = children.results.get('ITS')
        if its:
            result = 'ITS'
        else:
            result = children[0]
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_op_chain(cls, node, children):
        """
        Here we have a chain of alternating operations and names in the form: a.b(x,y).c(a).d
        These correspond to type specific operations
        """
        _logger.info("op_chain = (scalar_op / name)*")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = Op_chain_a(children)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_value(cls, node, children):
        """
        """
        _logger.info("value = TRUE / FALSE / enum_value / type_selector / input_param")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_scalar_op(cls, node, children):
        """
        """
        _logger.info("scalar_op = name supplied_params")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        n = children.results['name'][0]
        p = children.results['supplied_params'][0]
        result = Scalar_op_a(
            name=n,
            supplied_params=p
        )
        _logger.info(f"  > {result}")
        return result

    # Name of type and name of value selected
    @classmethod
    def visit_type_selector(cls, node, children):
        """
        """
        _logger.info("type_selector = name '[' name? ']'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        s = '<default>' if len(children) == 1 else children[1]
        result = Type_expr_a(type=children[0], selector=s)
        _logger.info(f"  > {result}")
        return result

    # Reflexive selection
    @classmethod
    def visit_reflexive_selection(cls, node, children):
        """
        HIPPITY_HOP is either nearest or furthest occurrence in reflexive search
        (This operator is also what tells the parser that this is a reflexive search)

        There must be a scalar expression to evaluate to determine whether or not a given instance
        meets the selection criteria.

        A comparison operator is provided when the scalar expression is simply an its.<attr> reference
        so that we can say "its.Altitude" (the Altitude of the currently tested instance) is greater than
        that of the instance at the beginning of the search.
        """
        _logger.info("reflexive_selection = HIPPITY_HOP scalar_expr ('|' COMPARE '|')?")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        comp = children.results.get('COMPARE')
        result = Reflexive_select_a(
            expr=children.results['scalar_expr'],
            compare=None if not comp else comp[0],
            position=children.results['HIPPITY_HOP'][0]
        )
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_HIPPITY_HOP(cls, node, children):
        """
        Select the furthest or nearest qualifying instance
        """
        _logger.info("HIPPITY_HOP = FAR_HOP / NEAR_HOP")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = 'nearest' if 'NEAR_HOP' in children.results else 'furthest'
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_input_param(cls, node, children):
        """
        An input parameter is signified by the 'in' keyword
        """
        _logger.info("input_param = IN '.' name")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = IN_a(children[0].name)
        _logger.info(f"  > {result}")
        return result

    # Relationship traversal
    @classmethod
    def visit_path(cls, node, children):
        """
        """
        _logger.info("path = hop+")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = PATH_a(children)
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_hop(cls, node, children):
        """
        """
        _logger.info("hop = '/' (rnum / name)")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = children[0]
        _logger.info(f"  > {result}")
        return result

    # Names
    @classmethod
    def visit_name(cls, node, children):
        """ Join words and delimiters """
        _logger.info("name = first_word (NAME_GLUE word)*")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = N_a(''.join(children))
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_rnum(cls, node, children):
        """
        Relationship number such as R23

        This is how relationships are named
        """
        _logger.info("rnum = r'O?R[1-9][0-9]*'")
        _logger.info(f'  :: {node.value}')

        _logger.info(f"  < {children}")
        result = R_a(node.value)
        _logger.info(f"  > {result}")
        return result

    # Discarded whitespace and comments
    @classmethod
    def visit_LINEWRAP(cls, node, children):
        """
        end of line followed by optional indent on next line
        """
        _logger.info("LINEWRAP = EOL SP*")

        _logger.info(f"  < {children}")
        result = None
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_EOL(cls, node, children):
        """
        end of line: Spaces, Comments, blank lines, whitespace we can omit from the parser result
        """
        _logger.info(r"EOL = SP* COMMENT? '\n'")

        _logger.info(f"  < {children}")
        result = None
        _logger.info(f"  > {result}")
        return result

    @classmethod
    def visit_SP(cls, node, children):
        """ Single space character (SP) """
        _logger.info("SP = ' '")

        _logger.info(f"  < {children}")
        result = None
        _logger.info(f"  > {result}")
        return result

