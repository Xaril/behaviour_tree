from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List


class Status(Enum):
    """The different status codes when iterating through the behaviour tree."""
    SUCCESS = 0
    RUNNING = 1
    FAIL = 2


class Node(ABC):
    """An interface defining a node in the behaviour tree.
    Subclasses must implement the run function.
    """
    @abstractmethod
    def run(self) -> Status:
        pass


class CompositeNode(Node):
    """An abstract class defining non-leaf nodes in the behaviour tree.
    Subclasses must implement the run function.
    """

    def __init__(self):
        self._children: List[Node] = []

    @abstractmethod
    def run(self) -> Status:
        pass

    def add_child(self, child: Node) -> "CompositeNode":
        """Adds a child to the node of the tree."""
        self._children.append(child)
        return self

    def insert_child(self, index: int, child: Node) -> "CompositeNode":
        """Inserts a child at the given index at the node of the tree."""
        self._children.insert(index, child)
        return self


class Fallback(CompositeNode):
    """The fallback node in a behaviour tree."""

    def run(self) -> Status:
        """Returns upon finding a success or running. Otherwise runs all
        children and returns fail.
        """
        for child in self._children:
            status = child.run()
            if status == Status.SUCCESS:
                return Status.SUCCESS
            elif status == Status.RUNNING:
                return Status.RUNNING
        return Status.FAIL


class Sequence(CompositeNode):
    """The sequence node in a behaviour tree."""

    def run(self) -> Status:
        """Returns upon finding a fail or running. Otherwise runs all children
        and returns success.
        """
        for child in self._children:
            status = child.run()
            if status == Status.FAIL:
                return Status.FAIL
            elif status == Status.RUNNING:
                return Status.RUNNING
        return Status.SUCCESS


class Condition(Node):
    """Defines a condition in the behaviour tree. Only checks if condition
    holds, and performs no state changes.
    """

    def __init__(self, condition: Callable[[], bool]):
        self.__condition = condition

    def run(self) -> Status:
        """Returns success if condition holds and failure otherwise."""
        if self.__condition():
            return Status.SUCCESS
        else:
            return Status.FAIL


class Action(Node):
    """Defines an action in the behaviour tree. Performs the action and returns
    the status.
    """

    def __init__(self, action: Callable[[], Status]):
        self._status = Status.RUNNING
        self.__action = action

    def run(self) -> Status:
        """Returns the status of performing an action."""
        self._status = self.__action()
        return self._status
