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


# Handler Implementation
def property_sexp(sexp):
    class PropertyHandler(AbstractHandler):
        def handle(self, defect):
            if eval(f"defect.{sexp}"):
                return f"{sexp} is not valid"
            return super().handle(defect)

    return PropertyHandler()


# Parser
def sexp_parser(sexp):
    if sexp[0] in "xyhw":
        return property_sexp(sexp)


def line_parser(line):
    key, *sexps = line.split()
    head = AbstractHandler()
    reduce(lambda x, y: x.set_next(y), map(sexp_parser, sexps), head)
    return key, head


class Ruleset:
    def __init__(self, rule_text):
        self.rules = defaultdict(AbstractHandler)
        self._parse(rule_text)

    def _parse(self, rule_text):
        for line in [l for l in rule_text.splitlines() if l.strip()]:
            key, handler = line_parser(line)
            self.rules[key] = handler

    def __call__(self, defect):
        return self.rules[defect.name].handle(defect)
