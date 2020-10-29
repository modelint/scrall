// This is an incomplete version of the Scrall grammar
// since the parser is a work in progress
//
// Over time this file will become a complete grammar
//
// See the current examples file to see what sorts of expressions
// can be parsed in the current version
//


// Issues: Selectors are broken
// x = Real[pi]
// After adding inst_set as a scalar component things break
// and moving selector or inst_set around doesn't seem to help things
// 


// An Activity may contain zero or many execution groups
// There are three ways to group a set of actions (action_set)
//      Between {} across one or more lines
//      In one line separatec by ;'s
//      Single action one one line or spread across multiple lines
//

// Activity structure
// --
// An Activity is organized into any number of execution groups.
// Each execution group has any number of control flow inputs and outputs.
// A control flow input enables the group for execution by passing in a sequence token
// visible to the left of the execution group. A control flow output enables the exeuction of
// one or more downstream execution groups by setting any number of sequence tokens on the
// right hand side.

activity = execution_group*

// Each execution group is separated by at least one new line
execution_group = input_ctrl_flow* action_cluster output_ctrl_flow* NEWLINE+

// A sequence token is just a name inside angled brackets
input_ctrl_flow = sequence_token
output_ctrl_flow = sequence_token
sequence_token = SPACE '<' name '>' SPACE  // whitespace, but no newlines breaking up the token set

// There are three ways to group a set of actions (action_set)
//      Between {} across one or more lines
//      In one line separatec by ;'s
//      Single action one one line or spread across multiple lines
//
action_cluster = action_block / line_cluster / action

// One or more executions groups inside {}
// since you may enable a group and then, inside that group
// there may be other groups enabled by other sequence tokens
//
action_block = '{' (__ execution_group __)+ '}'

// One or more actions may share the same line if they have no
// data or control flow interdependencies, in other words, each action
// on the line may execute at the same time or in any order
//
line_cluster = action flow_ind_action+
flow_ind_action = SPACE ACTION_SEP SPACE action // no newlines inside a line cluster
// --


// Scrall actions
// --
// Here is each action that you can specify in Scrall
//
action = (
    conditional_action /
    iteration /
    migration /
    signal /
    op_call /
    assignment /
    link_action /
    inst_creation /
    inst_deletion
) __ // An action that is not in a line cluster may wrap across multiple lines

// Signal
signal = event_name __ SENDTO __ destination
// handle: ready?    go -> : don't go -> me
destination = (__ ':' __) / inst_set __ (DELAY __ duration)?
event_name = name
duration = scalar_expr

// Conditional action
conditional_action =  case_action / guard_action

// Case action
case_action = enum_var __ '?' __ '{' __ case+ __ '}'
enum_var = name
case = enum_val (__ ',' __ enum_val)* __ ':' __ execution_group
enum_val = '.' name

// Guard action
guard_action = guard __ '?' __ execution_group (__ ':' __ execution_group)?
guard = name / '(' __ scalar_expr __ ')'

// Iteration
iteration = '<<' __ inst_set __ '>>' __ action_block

// Assignment
assignment = assign_scalar / assign_inst_set // / assign_table

// Scalar assignment
assign_scalar = scalar_variable type_dec? __ SCALAR_ASSIGN __ scalar_expr
type_dec = TYPE_DEC type_name

// Instance set assignment
assign_inst_set = inst_set_variable __ INST_ASSIGN __ inst_set
inst_set = ME / inst_source selection?
inst_source = op_call / path / inst_creation / class_name / inst_set_variable

class_name = name
inst_set_variable = name

// Instance creation
inst_creation = CREATE __ new_inst_spec
new_inst_spec = class_name __ attr_init_clause? // Needed for migration action
attr_init_clause = '(' __ attr_init_list? __ ')'
attr_init_list = attr_init (__ ',' __ attr_init_list)*
attr_init = attr_name __ ':' __ scalar_expr

// Instance deletion
inst_deletion = DELETE __ inst_set

// Migration
migration = inst_set? __ MIGRATE __ new_inst_spec


// Link action
link_action = link_source? __ link_spec+
link_source = inst_set
link_spec = LINK __ rnum __ link_target
link_target = inst_set __ assoc_class_link?
assoc_class_link = ',' __ inst_set

// path
path = hop+
hop = '/' (name / rnum)
rnum = 'R'[1-9][0-9]*

// Table assignment
// (not specified yet)

// Instance selection
selection = '(' __ criteria? __ ')'
criteria = (op_card __ ',' __ restriction) / op_card / restriction
op_card = CARD
restriction = attr_criteria ( __ ',' __ attr_criteria)*
attr_criteria = attr_order / value_comparison
attr_order = ORDER attr_name __
value_comparison = ORDER? ITS? attr_name __ (MATCH / EQUAL / COMPARE) __ scalar_expr
attr_name = name

// math and boolean operator precedence
scalar_expr = __ logical_or __
logical_or = logical_and (_ OR _ logical_and)*
logical_and = equality (_ AND _ equality)*
equality = comparison (_ EQUAL _ comparison)*
comparison = addition (_ COMPARE _ addition)*
addition = mult (_ ADD _ mult)*
mult = exponent (_ MULT _ exponent)*
exponent = logical_not (EXP logical_not)*
logical_not = (NOT _)? UNARY_MINUS? INCR? scalar_term

// These can be math expression terms in Scrall
// Dot for attributes or type components
scalar_term = scalar_component '.' scalar_term / scalar_component
// Parenthesized expression, method/op call, type selector or variable name
scalar_component = '(' __ scalar_expr __ ')' / inst_set / input_param / op_call / selector / scalar_variable
input_param = IN name
scalar_variable = name

// Method or operation call
op_call = name signature __


// Signature in an event, method or operation call
signature = '(' __ param_list? __ ')'
param_list = param (__ ',' __ param)*
param = param_full / param_double
param_full = name type_qual
param_double = name
type_qual = __ ':' __ name

// Type selector
selector = type_name value_selection? type_op_call?
type_name = name
value_selection = '[' __ value_name __ ']'
type_op_call = '.' op_call
value_name = alpha_numeric_word word_delim value_name / alpha_numeric_word
alpha_numeric_word = [a-zA-Z0-9]+

// Assignment operators
SCALAR_ASSIGN = '='
INST_ASSIGN = '.=' / '..='
TABLE_ASSIGN = '#='

// Math and logic operators
EXP = '^'
INCR = '++' / '--'
MATCH = ':'
EQUAL = '==' / '!='
COMPARE = [<>][=]?
OR = 'or' { return "OR" }
AND = 'and' { return "AND" }
NOT = '!' / 'not' {return "NOT" }
UNARY_MINUS = '-'
ADD = [+-]
MULT = [*/%]

// Symbols
MIGRATE = '>>'
ACTION_SEP = ';'
LINK = '&'
HIPPITY_HOP = '~|' / '~' 
DELETE = '!*'
CREATE = '*'
TYPE_DEC = '::'
ORDER = '+^' / '-^'
CARD = '1' / '*'
DELAY = '@'
SENDTO = '->'
IN = 'in.'
ITS = 'its.'


// Values
ME = 'me'
TRUE = 'true'
FALSE = 'false'
bool_value = TRUE / FALSE

// Variable or model element name
name = word word_delim name / word
word_delim = [ _]
ignore_keywords = !" true" !"true " !" false" !"false " !" and" !"and " !" or" !"or " !" not" !"not " !" its" !"its " ! " me" !" me"
word = ignore_keywords [a-zA-Z] [a-zA-Z0-9']*

// Whitespace
NEWLINE = '\n'
SPACE = [ \t]* // No new lines or returns
_ = [ ] [ \t\r\n]* // At least one space char
__ = [ \t\r\n]* // Any amount of whitespace
