from abc import ABC, abstractmethod


class AstNode(ABC):
    @abstractmethod
    def accept(self, visitor: 'AstNodeVisitor'):
        pass
