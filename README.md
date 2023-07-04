# Scrall Action Language
Scrall = Starr's Concise Relational Action Language

This is an action language that supports Shlaer-Mellor executable UML. It allows you to specify computation
inside states, methods, and external entity operations.

This language is consistent with the [Shlaer Mellor Metamodel](https://github.com/modelint/shlaer-mellor-metamodel),
 another repository on this site.

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