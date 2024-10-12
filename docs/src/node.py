from abc import ABC
from dataclasses import dataclass

from docs.src.ast_node import AstNode


class ExprNode(AstNode):
    pass


@dataclass
class BinExprNode(ExprNode):
    left: ExprNode
    op: str
    right: ExprNode

    def accept(self, visitor: 'AstNodeVisitor'):
        return visitor.visit_bin_expr_node(self)


@dataclass
class NumNode(ExprNode):
    value: int

    def accept(self, visitor: 'AstNodeVisitor'):
        return visitor.visit_num_node(self)
