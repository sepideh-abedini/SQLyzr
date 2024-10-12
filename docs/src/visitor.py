from abc import ABC, abstractmethod

from docs.src.node import BinExprNode, NumNode


class AstNodeVisitor(ABC):
    @abstractmethod
    def visit_bin_expr_node(self, node: BinExprNode):
        pass

    @abstractmethod
    def visit_num_node(self, node: NumNode):
        pass
