from docs.src.node import NumNode, BinExprNode
from docs.src.visitor import AstNodeVisitor


class EvaluatorVisitor(AstNodeVisitor):

    def visit_bin_expr_node(self, node: BinExprNode):
        left_val = node.left.accept(self)
        right_val = node.right.accept(self)
        if node.op == '+':
            return left_val + right_val
        if node.op == '-':
            return left_val - right_val

    def visit_num_node(self, node: NumNode):
        return node.value
