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

def xymapping(x, y) -> bool:
    # 第一象限 > 第三
    if x >= 1200 and y <= 1200:
        xmin = x-1250
        xmax = x-1050
        ymin = 950 + y
        ymax = 1150 + y
        return lambda x,y: (x <= xmax and x >= xmin) and (y >= ymin and y <= ymax)
    # 第四象限
    if x >= 1200 and y > 1200:
        xmin = x-1250
        xmax = x-1050
        ymax = y-1060
        ymin = y-1260
        return lambda x,y: (x <= xmax and x >= xmin) and (y >= ymin and y <= ymax)
    # 第二象限
    if x < 1200 and y <= 1200:
        xmin = x+1050
        xmax = x+1250
        ymin = y+1060
        ymax = y+1260
        return lambda x,y: (x <= xmax and x >= xmin) and (y >= ymin and y <= ymax)

    # 第三象限
    if x < 1200 and y > 1200:
        xmin = x+1050
        xmax = x+1250
        ymin = y-1150
        ymax = y-950
        return lambda x,y: (x <= xmax and x >= xmin) and (y >= ymin and y <= ymax)

# Parser
def sexp_parser(sexp):
    if sexp[0] in "xyhw":
        return lambda d: eval(f"d.{sexp}")
    if sexp[0] == '-':
        def left_check(d):
            fn = xymapping(d.x, d.y)
            # return any([fn(d_.x, d_.y) for d_ in d.lens.left if d_.name.endswith(sexp[1:])])
            mappings = [d_.name for d_ in d.lens.left if fn(d_.x, d_.y)]
            for name in mappings:
                if name.endswith(sexp[1:]):
                    return True
            return False
        return left_check
    if sexp[0] == '+':
        def right_check(d):
            fn = xymapping(d.x, d.y)
            return any([fn(d_.x, d_.y) for d_ in d.lens.right if d_.name.endswith(sexp[1:])])
        return right_check

    if sexp[0] == "W":
        def left_widht(d):
            fn = xymapping(d.x, d.y)
            mappings = [d_.width for d_ in d.lens.left if fn(d_.x, d_.y)]
            for w in mappings:
                if w > eval(sexp[2:]):
                    return True
            return False
        return left_widht

    if sexp[0] == "H":
        def left_height(d):
            fn = xymapping(d.x, d.y)
            mappings = [d_.height for d_ in d.lens.left if fn(d_.x, d_.y)]
            for h in mappings:
                if h > eval(sexp[2:]):
                    return True
            return False
        return left_height


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