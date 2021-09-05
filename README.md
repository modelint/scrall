# Scrall
Scrall = Starr's Concise Relational Action Language

This is the pseudo-code that we use to write all the action language in our Executable UML models. Since we use the Shlaer-Mellor variation of Executable UML, this language is true to its unique semantics and is tool independent.

See the [wiki](https://github.com/modelint/scrall/wiki) for a full description of this language.

We've been having great success translating this to the open source micca platform (on Fossil, not Github) which generates efficient C code from the complete Executable UML models at the [Toyota Research Institute](https://github.com/ToyotaResearchInstitute/opensafety-mbse/wiki).

I am planning to develop a complete peg grammar to support Scrall using Python's arpeggio parser package. Once we have a parser up and running the status of this language will no longer be 'pseudo'.

This language will be consistent with the [Shlaer Mellor Metamodel](https://github.com/modelint/shlaer-mellor-metamodel) also in development.
