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
Op_a = namedtuple('Op_a', 'owner op_name supplied_params order')
Scalar_op_a = namedtuple('Scalar_op_a', 'name supplied_params')
Call_a = namedtuple('Call_a', 'call op_chain')
Scalar_Call_a = namedtuple('Scalar_Call_a', 'call')
"""The subject of a call could be an instance set (method) or an external entity (ee operation)"""
Attr_Access_a = namedtuple('Attr_Access_a', 'cname its attr')
Selection_a = namedtuple('Selection_a', 'card criteria')
Inst_Assignment_a = namedtuple('Inst_Assignment_a', 'lhs card rhs X')
EE_Signal_a = namedtuple('EE_Signal_a', 'event supplied_params ee')
Signal_a = namedtuple('Signal_a', 'event supplied_params dest')
"""Signal sent to trigger event at destination with optional supplied parameters"""
Signal_Action_a = namedtuple('Signal_Action_a', 'event supplied_params dest delay assigner_partition')
Signal_Dest_a = namedtuple('Signal_Dest_a', 'target_iset assigner_partition delay')
Signal_Choice_a = namedtuple('Signal_Choice_a', 'decision true_signal false_signal')
Block_a = namedtuple('Block_a', 'actions')
Sequence_Token_a = namedtuple('Sequence_Token_a', 'name')
Execution_Unit_a = namedtuple('Execution_Unit_a', 'input_tokens output_tokens action_group')
Decision_a = namedtuple('Decision_a', 'input true_result false_result')
Delete_Action_a = namedtuple('Delete_Action_a', 'instance_set')
Case_a = namedtuple('Case_a', 'enums execution_unit')
Switch_a = namedtuple('Switch_a', 'input_flow cases')
MATH_a = namedtuple('MATH_a', 'op operands')
TOP_a = namedtuple('TABLE_a', 'op operands')
UNARY_a = namedtuple('UNARY_a', 'op operand')
BOOL_a = namedtuple('BOOL_a', 'op operands')
"""Boolean operation returns true or false"""
Scalar_Assignment_a = namedtuple('Scalar_Assignment_a', 'lhs rhs')
Table_Assignment_a = namedtuple('Table_Assignment_a', 'type lhs rhs')
Scalar_RHS_a = namedtuple('Scalar_RHS_a', 'expr attrs')
Flow_Output_a = namedtuple('Flow_Output_a', 'name exp_type')
PATH_a = namedtuple('PATH_a', 'hops')
INST_a = namedtuple('INST_a', 'components')
R_a = namedtuple('R_a', 'rnum')
IN_a = namedtuple('IN_a', 'name')
Enum_a = namedtuple('Enum_a', 'value')
Order_name_a = namedtuple('Order_name_a', 'order name')
N_a = namedtuple('N_a', 'name')
Op_chain_a = namedtuple('Op_chain', 'components')
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
Iteration_a = namedtuple('Iteration_a','order action_group')
Migration_a = namedtuple('Migration_a','from_inst to_subclass')


symbol = {'^+': 'ascending', '^-': 'descending'}

table_op = {
    '%': 'SYMDIFF',
    '^': 'INTERSECT',
    '+': 'UNION',
    '-': 'SUB',
    '*': 'MULT',
    '##': 'JOIN',
}

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
        execution_unit* EOF

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
        return [c for c in children if c]

    @classmethod
    def visit_execution_unit(cls, node, children):
        """
        ( output_flow / (input_tokens? action_group output_tokens?) ) EOL+

        An execution unit is a set of action groups.

        When an action group completes execution it may enable any number of output tokens.
        Each output token represents an outgoing control flow on a data flow diagram.
        Any output token may feed into any number of other action groups in the form of an input token.

        So the syntax defines which input tokens, if any enable this action group to execute and which
        output tokens, if any are enabled upon execution of this action group.

        Every execution unit is terminated by a new line.
        """
        oflow = children.results.get('output_flow')
        if oflow:
            return Output_Flow_a(oflow[0])
        itok = children.results.get('input_tokens')
        otok = children.results.get('output_tokens')
        ag = children.results.get('action_group')[0]
        return Execution_Unit_a(
            input_tokens=None if not itok else itok[0],
            output_tokens=None if not otok else otok[0],
            action_group=ag
        )

    @classmethod
    def visit_block(cls, node, children):
        """
        '{' execution_unit* '}'

        We organize multiple execution units in a block (between brackets) when multiple
        execution units are enabled by the same decision, case, or input tokens.

        This correpsonds to the concept of one or more control flows on a data flow diagram
        enabling multiple processes.
        """
        return Block_a(actions=children)

    @classmethod
    def visit_action(cls, node, children):
        """
        scalar_assignment / delete / scalar_switch / decision / inst_assignment / signal_action / call

        These are (or will be) a complete set of scrall actions. The ordering helps in some cases to prevent
        one type of action from being mistaken for another during the parse. You can't backgrack in a peg
        grammar, so you need to match the pattern right on the first scan.

        There should be only one child element and it will be a named tuple defining the parsed action.
        """
        return children[0]

    # Explicit sequence using control flow input and output tokens
    @classmethod
    def visit_input_tokens(cls, node, children):
        """
        sequence_token+
        """
        return children

    @classmethod
    def visit_output_tokens(cls, node, children):
        """
        sequence_token+
        """
        return children

    @classmethod
    def visit_sequence_token(cls, node, children):
        """
        '<' token_name '>'

         Named control flow
        """
        return Sequence_Token_a(name=children[0])

    @classmethod
    def visit_token_name(cls, node, children):
        """
        r'[A-Za-z0-9_]+'
        No spaces in token names, often single digit: <1>

        Since this is a terminal, we need to grab the name from the node.value
        """
        return node.value

    # Table expressions
    @classmethod
    def visit_table_assignment(cls, node, children):
        """
        explicit_table_assignment / implicit_table_assignment
        """
        return children[0]

    # Explicit table assignment
    @classmethod
    def visit_explicit_table_assignment(cls, node, children):
        """
        table_def TABLE_ASSIGN table_value
        """
        return Table_Assignment_a(type='explicit', lhs=children[0], rhs=children[1])

    @classmethod
    def visit_table_def(cls, node, children):
        """
        name '[' attr_type_set? ']'
        """
        return Table_Def_a(name=children[0].name, header=[] if len(children) < 2 else children[1])

    @classmethod
    def visit_attr_type_set(cls, node, children):
        """
        attr_type_def (',' attr_type_def)*
        """
        return children

    @classmethod
    def visit_attr_type_def(cls, node, children):
        """
        name '::' name
        """
        return Attr_Type_a(attr_name=children[0].name, type_name=children[1].name)

    @classmethod
    def visit_table_value(cls, node, children):
        """
        '{' row* '}'
        """
        return children

    @classmethod
    def visit_row(cls, node, children):
        """
        '{' attr_value_set? '}'
        """
        return [] if not children else children[0]

    @classmethod
    def visit_attr_value_set(cls, node, children):
        """
        scalar_expr (',' scalar_expr)*
        """
        return children

    # Implicit table assignment
    @classmethod
    def visit_implicit_table_assignment(cls, node, children):
        """
        name TABLE_ASSIGN table_expr
        """
        return Table_Assignment_a(type='implicit', lhs=children[0].name, rhs=children[1])

    @classmethod
    def visit_table_expr(cls, node, children):
        """
        table_operation
        """
        return children[0]

    @classmethod
    def visit_table_operation(cls, node, children):
        """
        table_term (TOP table_term)*
        """
        if len(children) == 1:
            return children[0]
        else:
            return TOP_a(children.results['TOP'][0], children.results['table_term'])

    @classmethod
    def visit_table_term(cls, node, children):
        """
        table / "(" table_expr ")" header_expr? selection? projection?
        """
        return children

    @classmethod
    def visit_TOP(cls, node, children):
        """
        '^' / '+' / '-' / '*' / '%' / '##'
        """
        return table_op[children[0]]

    @classmethod
    def visit_table(cls, node, children):
        """
        instance_set header_expr? selection? projection?
        """
        if len(children) == 1:
            return children[0]
        else:
            return children

    # Table header operations
    @classmethod
    def visit_header_expr(cls, node, children):
        """
        '[' column_op (',' column_op)* ']'
        """
        return children

    @classmethod
    def visit_column_op(cls, node, children):
        """
        extend / rename_op
        """
        return children[0]

    @classmethod
    def visit_rename_op(cls, node, children):
        """
        name rename_attr
        """
        return Rename_a(from_name=children[0].name, to_name=children[1].name)

    @classmethod
    def visit_rename_attr(cls, node, children):
        """
        RENAME name
        """
        return children[0]

    # Decision and switch actions
    @classmethod
    def visit_decision(cls, node, children):
        """
        scalar_expr true_result false_result?
        """
        return Decision_a(
            input=children[0],
            true_result=children[1],
            false_result=None if len(children) < 3 else children[2]
        )

    @classmethod
    def visit_true_result(cls, node, children):
        """
        DECISION_OP action_group

        Actions to be executed when the decision evaluates to true
        """
        return children[0]

    @classmethod
    def visit_false_result(cls, node, children):
        """
        FALSE_RESULT_OP action_group

        Actions to be executed when the decision evaluates to false
        """
        return children[0]

    # Switch action
    @classmethod
    def visit_switch(cls, node, children):
        """
        (rnum / scalar_expr) DECISION_OP case_block

        Rnum or boolean expr triggers case_block
        If rnum, the enums must be subclass names (verified outside parser)
        """
        input_flow = children.results.get('rnum')
        input_flow = None if not input_flow else input_flow[0]
        input_flow = input_flow if input_flow else children.results['scalar_expr'][0]

        return Switch_a(
            input_flow=input_flow,
            cases=children.results['case_block'][0]
        )

    @classmethod
    def visit_case_block(cls, node, children):
        """
        '{' case+ '}'

        One or more cases between brackets
        """
        return children

    @classmethod
    def visit_case(cls, node, children):
        """
        enum_value+ ':' execution_unit

        One or more enumerated values that triggers an execution unit
        """
        return Case_a(
            enums=children.results['enum_value'],
            execution_unit=children.results['execution_unit'][0]
        )

    @classmethod
    def visit_enum_value(cls, node, children):
        """
        '.' name
        """
        return Enum_a(children[0])

    # # Asynch service
    # @classmethod
    # def visit_asynch_service(cls, node, children):
    #     """
    #     name '.' signal_spec ASYNCH ee
    #     """
    #     return Asynch_a(*children)

    # Signal action
    @classmethod
    def visit_signal_action(cls, node, children):
        """
        signal_choice / signal
        """
        return children[0]

    @classmethod
    def visit_signal(cls, node, children):
        """
        signal_spec (signal_dest / ee_dest)
        """
        sdest = children.results.get('signal_dest')
        if sdest:
            return Signal_a(
                event=children[0]['name'],
                supplied_params=children[0]['params'],
                dest=children[1]
            )
        else:
            return EE_Signal_a(
                event=children[0]['name'],
                supplied_params=children[0]['params'],
                ee=children[1]
            )

    @classmethod
    def visit_signal_choice(cls, node, children):
        """
        scalar_expr DECISION_OP signal_spec ':' signal_spec signal_dest
        """
        expr = children[0]
        # Both signals in a choice always have the same destination and delay
        true_signal = Signal_a(
            event=children[1]['name'],
            supplied_params=children[1]['params'],
            dest=children[3]
        )
        false_signal = Signal_a(
            event=children[2]['name'],
            supplied_params=children[2]['params'],
            dest=children[3]
        )
        return Signal_Choice_a(
            decision=expr,
            true_signal=true_signal,
            false_signal=false_signal,
        )

    @classmethod
    def visit_signal_spec(cls, node, children):
        """
        name supplied_params?
        """

        params = children.results.get('supplied_params', [])
        return {'name': children[0].name, 'params': params}

    @classmethod
    def visit_ee_dest(cls, node, children):
        """
        ASYNCH name
        """
        return children[0]

    @classmethod
    def visit_signal_dest(cls, node, children):
        """
        SIGNAL_OP instance_set assigner_partition? delay?
        """
        iset = children[0]
        ap = children.results.get('assigner_partition')
        ap = None if not ap else ap[0]
        delay = children.results.get('delay')
        delay = 0 if not delay else delay[0]
        return Signal_Dest_a(target_iset = iset, assigner_partition=N_a(ap), delay=delay)

    @classmethod
    def visit_assigner_partition(cls, node, children):
        """
        '(' instance_set ')'

        An instance set that partitions an assigner
        """
        return children[0]

    @classmethod
    def visit_delay(cls, node, children):
        """
        DELAY_OP scalar_expr

        A time or time interval
        """
        return children[0]

    # Instance set assignment and selection
    @classmethod
    def visit_inst_assignment(cls, node, children):
        """
        name INST_ASSIGN instance_set
        """
        return Inst_Assignment_a(
            lhs=children.results['flow_output'][0],
            card='1' if children.results['INST_ASSIGN'][0] == '.=' else 'M',
            rhs=children.results['instance_set'][0],
            X=(node.position, node.position_end)
        )


    # Table header operations
    @classmethod
    def visit_header_expr(cls, node, children):
        """
        '[' column_op (',' column_op)* ']'
        """
        return children

    @classmethod
    def visit_column_op(cls, node, children):
        """
        extend / rename
        """
        return children[0]

    @classmethod
    def visit_extend(cls, node, children):
        """
        rename_attr '(' op_chain ')'
        """
        return children

    @classmethod
    def visit_ITS(cls, node, children):
        return 'ITS'




    # Synchronous method or operation
    @classmethod
    def visit_call(cls, node, children):
        """
        instance_set op_chain?
        Post-parse verify that last element is an operation, otherwise invalid call
        """
        iset = children.results['instance_set'][0]
        opc = children.results.get('op_chain')
        return Call_a(
            call=iset,
            op_chain=None if not opc else opc[0]
        )

    @classmethod
    def visit_operation(cls, node, children):
        """
        ORDER? owner? '.' name supplied_params

        The results of an operation can be ordered ascending, descending
        The operation is invoked on the owner which may or may not be explicitly named
        If the owner is implicit, it could be 'me' (the local instance) or an operation on a type
        as determined from its parameters

        Name is the name of the operation
        """
        owner = children.results.get('owner')
        o = children.results.get('ORDER')
        p = children.results.get('supplied_params')
        return Op_a(
            owner='implicit' if not owner else owner[0],
            op_name=children.results['name'][0].name,
            supplied_params=[] if not p else p[0],
            order=None if not o else symbol[o[0]]
        )

    @classmethod
    def visit_supplied_params(cls, node, children):
        """
        '(' (param (',' param)*)? ')'

        Could be () or a list of multiple parameters
        """
        return children if children else []

    @classmethod
    def visit_param(cls, node, children):
        """
        (name ':')? scalar_expr

        If only a scalar_expr is present, it means that the supplied expr has the same name
        Ex: ( shaft id ) as that of the required parameter. Short for ( shaft id : shaft id ). This
        is a convenience that eliminates the need for name doubling in a supplied parameter set
        """
        s = children.results['scalar_expr']
        s = s if len(s) > 1 else s[0]
        p = children.results.get('name')
        if not p and not (isinstance(s, N_a) or isinstance(s, IN_a)):
            _logger.error(f"Paramenter name not supplied with expression value: [{children.results}]")
            raise ScrallMissingParameterName(children.results)
        return Supplied_Parameter_a(pname=s.name if not p else p[0].name, sval=s)

    # Subclass migration
    @classmethod
    def visit_migration(cls, node, children):
        """
        instance_set? SP* '>>' SP* new_inst_int
        """
        iset = children.results.get('instance_set')
        iset = 'me' if not iset else iset[0]
        dest_iset = children.results['new_inst_init'][0]
        return Migration_a(from_inst=iset, to_subclass=dest_iset)

    # Iteration
    @classmethod
    def visit_iteration(cls, node, children):
        """
        '<<' instance_set '>>' action_group
        """
        return Iteration_a(*children)

    # Instance set
    @classmethod
    def visit_instance_set(cls, node, children):
        """
        new_instance / ((operation / prefix_name / path) (reflexive_selection / selection / operation / path)*)

        An instance set begins with a required name (instance flow) or a path. The path can then be followed
        by any sequence of selection, operation, and paths. The parser won't find two paths in sequence since
        any encounter path will be fully consumed
        """
        if len(children) == 1 and isinstance(children[0],N_a):
            return children[0]
        else:
            return INST_a(children)

    @classmethod
    def visit_selection(cls, node, children):
        """
        '(' select_phrase ')'
        """
        return Selection_a(card=children[0][0], criteria=None if len(children[0]) < 2 else children[0][1])

    @classmethod
    def visit_select_phrase(cls, node, children):
        """
        (CARD ',' criteria) / CARD / criteria
        """
        explicit_card = children.results.get('CARD')
        card = '*' if not explicit_card else explicit_card[0]
        criteria = children.results.get('scalar_expr')
        if criteria:
            return [card, criteria[0]]
        else:
            return [card]

    # Creation, deletion, and references
    @classmethod
    def visit_new_instance(cls, node, children):
        """
        '*' new_inst_init
        create an instance of a class as an action
        """
        return children[0]

    @classmethod
    def visit_new_lineage(cls, node, children):
        """
        '*[' new_inst_init (',' new_inst_init)+ ']'

        create all instances of a lineage
        """
        return New_lineage_a(children)

    @classmethod
    def visit_new_inst_init(cls, node, children):
        """
        name attr_init? to_ref*

        specify class, attr inits, and any required references
        """
        a = children.results.get('attr_init')
        r = children.results.get('to_ref')
        return New_inst_a(cname=children[0], attrs=None if not a else a[0], rels=None if not r else r[0])

    @classmethod
    def visit_attr_init(cls, node, children):
        """
        '(' (attr_value_init (',' attr_value_init)* ')'

        all attrs to init for a new instance
        """
        return children

    @classmethod
    def visit_attr_value_init(cls, node, children):
        """
        (name ':' scalar_expr )*
        """
        return Attr_value_init_a(attr=children[0], scalar_expr=children[1])

    @classmethod
    def visit_update_ref(cls, node, children):
        """
        instance_set? to_ref

        A standalone reference
        """
        iset = children.results.get('instance_set')
        iset = 'me' if not iset else iset[0]
        return Update_ref_a(iset=iset, to_ref=children[-1])

    @classmethod
    def visit_to_ref(cls, node, children):
        """
        '&' rnum instance_set (',' instance_set)?

        non-associative or associative reference
        """
        ref1 = None if len(children) < 2 else children[1]
        ref2 = None if len(children) < 3 else children[2]
        return To_ref_a(rnum=children[0], iset1=ref1, iset2=ref2)

    @classmethod
    def visit_delete(cls, node, children):
        """
        '!*' instance_set
        """
        iset = children.results.get('instance_set')
        return Delete_Action_a(instance_set=iset)

    # Scalar call
    @classmethod
    def visit_scalar_call(cls, node, children):
        """
        scalar_expr
        """
        return Scalar_Call_a(children)

    # Math and boolean operator precedence
    @classmethod
    def visit_scalar_assignment(cls, node, children):
        """
        scalar_output_set SP* SCALAR_ASSIGN SP* scalar_expr projection?
        """
        sout_set = children.results['scalar_output_set'][0]
        expr = children.results['scalar_expr'][0]
        proj = children.results.get('projection')
        proj = None if not proj else proj[0]
        return Scalar_Assignment_a(lhs=sout_set, rhs=Scalar_RHS_a(expr,proj))

    @classmethod
    def visit_scalar_output_set(cls, node, children):
        """
        flow_output (',' flow_output)*
        """
        return children

    @classmethod
    def visit_flow_output(cls, node, children):
        """
        name (TYPE_ASSIGN name)?
        """
        etyp = None if len(children) < 2 else children[1]
        return Flow_Output_a(name=children[0], exp_type=etyp)

    @classmethod
    def visit_projection(cls, node, children):
        """
        '.' '(' ( (ALL / (name (',' name)*) )? ')')
        """
        all = children.results.get('ALL')
        n = children.results.get('name')
        exp = 'ALL' if all else 'EMPTY' if not all and not n else None
        return Projection_a(expand=exp, attrs=n)

    @classmethod
    def visit_ALL(cls, node, children):
        """
        '*'
        """
        return 'ALL'

    @classmethod
    def visit_scalar_expr(cls, node, children):
        """
        scalar_logical_or
        """
        return children[0]

    @classmethod
    def visit_scalar_logical_or(cls, node, children):
        """
        scalar_logical_and (OR scalar_logical_and)*
        """
        if len(children) == 1: # No OR operation
            return children[0]
        else:
            return BOOL_a('OR', children.results['scalar_logical_and'])

    @classmethod
    def visit_scalar_logical_and(cls, node, children):
        """
        equality (AND equality)*
        """
        if len(children) == 1: # No AND operation
            return children[0]
        else:
            return BOOL_a('AND', children.results['equality'])

    @classmethod
    def visit_equality(cls, node, children) -> BOOL_a:
        """
        comparison (EQUAL comparison)*
        """
        if len(children) == 1:
            return children[0]
        else:
            # Convert ':' to '==' if found
            eq_map = ['==' if e in ('==',':') else '!=' for e in children.results['EQUAL']]
            return BOOL_a(eq_map, children.results['comparison'])

    @classmethod
    def visit_comparison(cls, node, children):
        """
        comparison = addition (COMPARE addition)*
        """
        if len(children) == 1:
            return children[0]
        else:
            return BOOL_a(children.results['COMPARE'][0], children.results['addition'])

    @classmethod
    def visit_addition(cls, node, children):
        """
        factor (ADD factor)*
        """
        if len(children) == 1:
            return children[0]
        else:
            return MATH_a(children.results['ADD'][0], children.results['factor'])

    @classmethod
    def visit_factor(cls, node, children):
        """
        term (MULT term)*
        """
        if len(children) == 1:
            return children[0]
        else:
            return MATH_a(children.results['MULT'][0], children.results['term'])

    @classmethod
    def visit_term(cls, node, children):
        """
        NOT? UNARY_MINUS? (scalar / scalar_expr)
        ---
        If the not or unary minus operations are not specified, returns whatever was parsed out earlier,
        either a simple scalar (attribute, attribute access, etc) or any scalar expression

        Otherwise, a unary minus expression nested inside a boolean not operation, or just the boolean not,
        or just the unary minus expressions individually are returned.
        """
        s = children.results.get('scalar')
        s = s if s else children.results['scalar_expr']
        scalar = s[0]
        if len(children) == 1:
            return scalar
        not_op = children.results.get('NOT')
        unary_minus = children.results.get('UNARY_MINUS')
        if unary_minus and not not_op:
            return UNARY_a('-', scalar)
        if not_op and not unary_minus:
            return BOOL_a('NOT', scalar)
        if unary_minus and not_op:
            return BOOL_a('NOT', UNARY_a('-', scalar))


    @classmethod
    def visit_scalar(cls, node, children):
        """
        value / QTY? scalar_chain

        A scalar is either a simple value such as an enum or a variable name, TRUE/FALSE, etc OR
        it is a chain of operations like a.b(x,y).c.d with a preceding instance set such as a path, selection, etc.
        """
        # Return value
        v = children.results.get('value')
        v = None if not v else v[0]
        if v:
            return v

        # Cardinality
        qty = children.results.get('QTY')
        schain = children.results['scalar_chain'][0]
        if qty:
            return qty[0],schain
        else:
            return schain

    @classmethod
    def visit_QTY(cls, node, children):
        """
        '??'
        """
        return 'QTY'

    @classmethod
    def visit_scalar_chain(cls, node, children):
        """
        (ITS op_chain) / ((scalar_source / instance_set projection?) op_chain?)
        """
        # ITS op_chain
        its = children.results.get('ITS')
        if its:
            op_chain = children.results['op_chain'][0]
            return its, op_chain

        if len(children) == 1 and (isinstance(children[0], N_a) or (isinstance(children[0], IN_a))):
            return children[0]

        return children

    @classmethod
    def visit_scalar_source(cls, node, children):
        """
        type_selector / input_param
        """
        its = children.results.get('ITS')
        if its:
            return 'ITS'
        else:
            return children[0]

    @classmethod
    def visit_op_chain(cls, node, children):
        """
        (scalar_op / name)*

        Here we have a chain of alternating operations and names in the form: a.b(x,y).c(a).d
        These correspond to type specific operations
        """
        return Op_chain_a(children)

    @classmethod
    def visit_value(cls, node, children):
        """
        TRUE / FALSE / enum_value / type_selector / input_param
        """
        return children[0]

    @classmethod
    def visit_prefix_name(cls, node, children):
        """
        ORDER? name
        """
        n = children.results['name'][0]
        o = children.results.get('ORDER')
        if o:
            return Order_name_a(order=symbol[o[0]], name=n)
        else:
            return n

    @classmethod
    def visit_scalar_op(cls, node, children):
        """
        name supplied_params
        """
        n = children.results['name'][0]
        p = children.results['supplied_params'][0]
        return Scalar_op_a(
            name=n,
            supplied_params=p
        )

    # Name of type and name of value selected
    @classmethod
    def visit_type_selector(cls, node, children):
        """
        name '[' name? ']'
        """
        s = '<default>' if len(children) == 1 else children[1]
        return Type_expr_a(type=children[0], selector=s)

    # Reflexive selection
    @classmethod
    def visit_reflexive_selection(cls, node, children):
        """
        HIPPITY_HOP scalar_expr ('|' COMPARE '|')?

        HIPPITY_HOP is either nearest or furthest occurrence in reflexive search
        (This operator is also what tells the parser that this is a reflexive search)

        There must be a scalar expression to evaluate to determine whether or not a given instance
        meets the selection criteria.

        A comparison operator is provided when the scalar expression is simply an its.<attr> reference
        so that we can say "its.Altitude" (the Altitude of the currently tested instance) is greater than
        that of the instance at the beginning of the search.
        """
        comp = children.results.get('COMPARE')
        return Reflexive_select_a(
            expr=children.results['scalar_expr'],
            compare=None if not comp else comp[0],
            position=children.results['HIPPITY_HOP'][0]
        )

    @classmethod
    def visit_HIPPITY_HOP(cls, node, children):
        """
        FAR_HOP / NEAR_HOP

        Select the furthest or nearest qualifying instance
        """
        return 'nearest' if 'NEAR_HOP' in children.results else 'furthest'

    @classmethod
    def visit_input_param(cls, node, children):
        """
        IN '.' name

        An input parameter is signified by the 'in' keyword
        """
        return IN_a(children[0].name)

    # Relationship traversal
    @classmethod
    def visit_path(cls, node, children):
        """
        hop+
        """
        return PATH_a(children)

    @classmethod
    def visit_hop(cls, node, children):
        """
        '/' (rnum / name)
        """
        return children[0]

    # Names
    @classmethod
    def visit_name(cls, node, children):
        """ Join words and delimiters """
        return N_a(''.join(children))

    @classmethod
    def visit_rnum(cls, node, children):
        """
        r'O?R[1-9][0-9]*'
        Relationship number such as R23

        This is how relationships are named
        """
        return R_a(node.value)

    # Discarded whitespace and comments
    @classmethod
    def visit_LINEWRAP(cls, node, children):
        """
        EOL SP*
        end of line followed by optional indent on next line
        """
        return None

    @classmethod
    def visit_EOL(cls, node, children):
        """
        SP* COMMENT? '\n'

        end of line: Spaces, Comments, blank lines, whitespace we can omit from the parser result
        """
        return None

    @classmethod
    def visit_SP(cls, node, children):
        """ ' '  Single space character (SP) """
        return None