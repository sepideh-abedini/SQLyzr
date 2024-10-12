- [How it Works?](#how-it-works)
  - [What is AST?](#what-is-ast)
  - [How Parser Works?](#how-parser-works)
  - [What is Visitor?](#what-is-visitor)
  - [Reading Next](#reading-next)
    - [Simple PLY + Visitor Example](#simple-ply--visitor-example)

# How it Works?

The high-level mechanism is simple:

- The SQL string is parsed and an `ASTNode` object is created
- A visitor traverse the tree and collects the desired information

## What is AST?

AST stands for Abstract Syntax Tree.
It is a tree object representing a SQL statement.

Let's put away SQL for a moment and use a simple expression
to understand the ASTs and parsing.
Consider the expression `1 + 3 - 2`.
The AST of this expression looks like this:

![ast-figure](ast.png)

If we parse the string `1 + 3 - 2` and create an AST object,
it is a tree with the `-` as root and two children: a subtree of
the `1 + 3` expression and `2`.
The subtree of `1 + 3` is again an AST with `+` as root
and `1` and `3` as children.

Similar to arithmetic expressions, we can do the same
for SQL statements.
For instance, for the `SELECT * FROM bar`
we can have an AST that has two children, select clause `SELECT *` and
from clause `FROM bar`.
Each child then can be AST itself.

## How Parser Works?

To create AST objects for a given string, we use the
[PLY](http://www.dabeaz.com/ply/index.html)
library.
Parsing consists of two main step, lexing and parsing itself.
PLY parser uses a BNF grammar to parse a given string.
> You can generate the BNF grammar using instructions described [here](../Readme.md#generating-bnf-grammar).

We just need to specify the grammar, and how to create the AST object
when string matches a grammar rule.
The rest is done by the library.
Let's go back to the `1 + 3 - 2` expression.
To parse this expression, we can have a very specific rule like:
`expr := 1 + 3 - 2`.
But, this rule is too specific, right?
We wish our expression work with any other number
other than 1, 2 or 3.
So, a better rule might be:
`expr := NUM + NUM - NUM`.
Here we are representing any number with the symbol `NUM`,
which allows us to generalize our rule to work with any number.
But, how we can do that?
Here, lexer comes into the play.
The rule of the lexer is to tokenize the input string.
We define the regular expression for each token and
lexer creates a token, instead of a literal string, when
it founds a match.
For instance, for the `1 + 3 - 2` expression, the output of lexer
is the token list `[NUM, '+', NUM, '-', NUM]`.
Thus, any other variation like `4 + 5 - 6` is also result
in the `[NUM, '+', NUM, '-', NUM]` token list
thus matches our generalized rule `expr := NUM + NUM - NUM`.
The parser, upon a match, calls our specific methods to create
the AST object using the extracted tokens.
For instance lets have the rule `sum_expr := NUM + NUM`.
Given the string `1 + 6`, lexer extracts the following tokens:
`toks = [NUM, '+', NUM]`.
Then, parser founds the match of `sum_expr` rule with
the current tokens list.
It then calls our specified function to create an AST
object:

```python
def match_sum_expr(toks):
    return SumExprASTNode(left=toks[0], right=toks[2])
```

Here, upon a match with `sum_expr` rule we are creating
a `SumExprASTNode` object which is an AST object
with two children left and right.
And we are assigning the first and third tokens (operands of `+` in the string)
as the children.
> This code segment is only for demonstration, PLY exact
> mechanism is a little bit different.

## What is Visitor?

Having a data structure for a SQL query,
enables us to traverse this tree and extract the information
we need.
One way to implement the traversing procedure is
to use [Visitor Pattern](https://refactoring.guru/design-patterns/visitor).
Visitor pattern increase the maintainability of the code and
enables us to easily add new ways of traversing or collecting
information during the traversal.

The main problem that is solved by visitor is decoupling
the logic of processing an AST from the AST nodes themselves.

For instance, assume that for a given AST, we wish to evaluate
its numeric value, export the tree representation of AST as an
image file and count the number of `+`.
One way to achieve these functionalities is to implement three
different function for each node for instance `export_tree`, `evalutae`,
and `count_plus`.
This way, each time we wish to add a new processing, we need to
add a function to each node class.

The alternative approach is to implement these processing in a
separate class, `ExportTreeVisitor`, `EvaluatorVisitor`, and
`CountPlusVisitor`.

We can then use visitor as follows:

```python
ast_node = parse('1 + 3 - 2')
visitor = EvaluatorVisitor()

result = ast_node.accept(visitor)

assert result == 2
```

## Reading Next

### [Simple PLY + Visitor Example](Example)

In the next step a simple parser and visitor implementations
are demonstrated.


