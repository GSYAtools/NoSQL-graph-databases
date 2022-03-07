# GSYA-NoSQL

Design and implementation of security policies for NoSQL databases (documental, graph oriented and columnar).

![](img/overview.png)

A security by design approach is used so that a set of metamodels are defined to specify the security aspects at the system design stage. They have been implemented as ecore metamodels in an Eclipse project.

[Metamodels:](metamodels/README.md)
- Security policies
- Structure of documental databases
- Structure of graph oriented databases
- Structure of columnar databases 

On the other hand, a model-driven development approach is applied which, starting from these models, allows to automatically obtain the implementation of security policies in specific tools. For each target tool, the necessary scripts (in Python) are provided packaged in a Docker container.
- Graph-oriented databases
    - Neo4J -> [GraphModelToNeo4J](GraphModelToNeo4J/README.md)
    - OrientDB
- Document databases
    - MongoDB
- Columnar databases
    - Cassandra




