from abc import ABC, abstractmethod
from functools import reduce
from collections import defaultdict

# Chain of Responsibility
class Handler(ABC):
    @abstractmethod
    def handle(self, defect):
        pass

    @abstractmethod
    def set_next(self, handler):
        pass


class AbstractHandler(Handler):
    _next_handler = None

    def set_next(self, handler):
        self._next_handler = handler
        return handler

    def handle(self, defect):
        if self._next_handler:
            return self._next_handler.handle(defect)
        return None


# Parser
def sexp_parser(sexp):
    if sexp[0] in "xyhw":
        return lambda d: eval(f"d.{sexp}")


def line_parser(line):
    key, *sexps = line.split()

    class LineHandler(AbstractHandler):
        def handle(self, defect):
            if all(map(lambda f: f(defect), map(sexp_parser, sexps))):
                return f"{sexps}"
            return super().handle(defect)

    return key, LineHandler()


class DefaultFactory:
    def __init__(self):
        self.head = AbstractHandler()
        self.next = None

    def add(self, handler):
        if self.next:
            self.next.set_next(handler)
        else:
            self.head.set_next(handler)
        self.next = handler

    def handle(self, defect):
        return self.head.handle(defect)


class Ruleset:
    def __init__(self, rule_text):
        self.rules = defaultdict(DefaultFactory)
        self._parse(rule_text)

    def _parse(self, rule_text):
        for line in [l for l in rule_text.splitlines() if l.strip()]:
            key, handler = line_parser(line)
            self.rules[key].add(handler)

    def __call__(self, defect):
        return self.rules[defect.name].handle(defect)
