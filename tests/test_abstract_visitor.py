from src.sql_parser.node import SqlAstNode
from src.visitor.node_visitor import NodeVisitor
from src.util.meta_utils import get_all_subclasses
from src.util.str_utils import pascal_to_snake


def get_visit_method_name(node_class_name: str):
    name = node_class_name
    name = pascal_to_snake(name)
    name = name.replace("_node", "")
    name = f'visit_{name}'
    return name


def test_verify_node_visitor():
    required_methods = set(map(lambda cls: get_visit_method_name(cls.__name__), get_all_subclasses(SqlAstNode)))
    print(f"Required methods: {required_methods}")

    actual_methods = set([method for method in dir(NodeVisitor) if
                          callable(getattr(NodeVisitor, method)) and not method.startswith("__")])
    print(f"Actual methods: {actual_methods}")

    assert required_methods.issubset(actual_methods), f"Difference: {required_methods.difference(actual_methods)}"

    print(f"All required methods exists in {NodeVisitor.__name__}")
