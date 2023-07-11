# Scrall Action Language
Scrall = Starr's Concise Relational Action Language

### Why you need this

You are building or exploring Executable UML models using the Shlaer-Mellor methodology and you need a text language
for specifying actions that:

* perform computations
* access and traverse the class model
* synchronize states
* communicate internally and with external entities

With these qualities:
* platorm independent action sequencing
* platform independent data types
* ability to manipulate both instances and attributres as well as relations (tables)
* conforms to Date and Darwen's formulation of relational and type theory

Scroll down for more about these qualities.

### Installation

Create or use a python 3.10+ environment. Then

% pip install scrall

At this point you can invoke the parser via the command line or from your python script.

#### From your python script

You need this import statement at a minimum:

    from scrall.parse.parser import ScrallParser

You can then either specify a path or a text variable using the appropriate method:

    result = ScrallParser.parse_text(scrall_text=action_text, debug=False)

OR

    result = ScrallParser.parse_file(file_input=path_to_file, debug=False)

Check the code in `parser.py` to verify I haven't changed these parameters on you wihtout updating the readme.

In either case, `result` will be a list of parsed scrall statements. You may find the header of the `visitor.py`
file helpful in interpreting these results.

#### From the command line

This is not the intended usage scenario, but may be helpful for testing or exploration. Since scrall may generate
some diagnostic info you may want to create a fresh working directory and cd into it first. From there...

    % scrall -f somefile.scrall

The .scrall extension is not necessary, but the file must contain scrall text. See this repository's wiki for
more about the scrall language. The grammar is defined in the [scrall.peg](https://github.com/modelint/scrall/blob/master/src/scrall/scrall.peg) file. (if the link breaks after I do some update to the code, 
just browse through the code looking for the scrall.peg file, and let me know so I can fix it)

You can also specify a debug option like this:

    % scrall -f somefile.scrall -D

This will create a scrall-diagnostics folder in your current working directory and deposite a coupel of PDFs defining
the parse of both the scrall grammar: `scrall_parse_tree.pdf` and your supplied text: `scrall_model.pdf`.

You should also see a file named `scrall.log`

### Compatibility

This language is consistent with the [Shlaer Mellor Metamodel](https://github.com/modelint/shlaer-mellor-metamodel),
 another [repository](https://github.com/modelint/class-model-dsl/wiki) on this site. In that repository the metamodel
is used to define a schema for a database where user models can be stored and accessed.

### Older documentation

NOTE: If you have the Scrall version 1.0.0 PDF, consider it superceded by the wiki on this site where the language spec is now maintained and updated.

### Platform independent action sequencing

This language is designed to support data flow execution, so that there is no arbitrary sequencing built in. You can transform
any chunk of action language (a method, operation, or state activity) into a data flow graph where each action may execute
as soon as all of its inputs are satisfied. So the only sequencing is that demanded by the application, independent of any
particular target platform.

### Relational operations supported
You can manipulate both instances of classes and relations (tables) interchangeably. Data access is decidely NOT Sql-like. Instead
C.J. Date's Tutorial D semantics are supported. This means that relational operations are closed under the algebra such that any given
operation yields a relation, so you can readily nest expressions to specify powerful data manipulation.

Class instances may be converted to relations and vice versa.

See the wiki on this repository for a full description of the language features.

### UPDATE 2023-7-04

For the last couple of years all of the primary scrall development has been managed in the class-model-dsl
(metamodel db) repository. I had it there as a matter of convenience while populating action semantics into the
Shlaer-Mellor metamodel. But the time has come to refactor what is becoming a bit of a monolith over there and
today, I am permanently moving all the latest scrall code back here to its proper home.

When the migration is complete, you will be able to grab the latest Scrall parser from PyPI without having to
download the whole Shlaer-Mellor metamodel database populator. This separation is essential since you might want
to define your own action language and parser to use with the metamodel, or just play with Scrall on its own.

I will post another update when it's ready here and on PyPI. The parser is currently in decent shape, so it's just
a matter of putting a command line interface on it and a bit of packaging.