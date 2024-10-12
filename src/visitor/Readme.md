# Visitors

`NodeVisitor` is an abstract class that defines
a method for each subclasses of the `SqlAstNode`.

Any concrete visitor implements this class and
purpose of the class is to ensure that visitors implement
visit methods for all types of nodes.

## Collector Visitor

`CollectorVisitor` is implemented based on the following
assumptions:

- Using a visitor on a node returns some data, that is
  the result of visiting that node
- The result of visiting each node is a combination of
  the results of visiting its children nodes
