from abc import ABC, abstractmethod
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
        xmin = x - 1275
        xmax = x - 1025
        ymin = 925 + y
        ymax = 1175 + y
        return lambda x, y: (x <= xmax and x >= xmin) and (y >= ymin and y <= ymax)
    # 第四象限
    if x >= 1200 and y > 1200:
        xmin = x - 1275
        xmax = x - 1025
        ymax = y - 1035
        ymin = y - 1285
        return lambda x, y: (x <= xmax and x >= xmin) and (y >= ymin and y <= ymax)
    # 第二象限
    if x < 1200 and y <= 1200:
        xmin = x + 1025
        xmax = x + 1275
        ymin = y + 1035
        ymax = y + 1285
        return lambda x, y: (x <= xmax and x >= xmin) and (y >= ymin and y <= ymax)
    # 第三象限
    if x < 1200 and y > 1200:
        xmin = x + 1025
        xmax = x + 1275
        ymin = y - 1175
        ymax = y - 925
        return lambda x, y: (x <= xmax and x >= xmin) and (y >= ymin and y <= ymax)


def linemapping(xmin, ymin, xmax, ymax):
    # 第一象限 > 第三
    if xmax >= 1200 and ymax <= 1200:
        xmin = xmin - 1275
        xmax = xmax - 1025
        ymin = 925 + ymin
        ymax = 1175 + ymax
        return lambda x, y, x_, y_: (x_ <= xmax and x >= xmin) and (
            y >= ymin and y_ <= ymax
        )
    # 第四象限
    if xmax >= 1200 and ymax > 1200:
        xmin = xmin - 1275
        xmax = xmax - 1025
        ymax = ymax - 1035
        ymin = ymin - 1285
        return lambda x, y, x_, y_: (x_ <= xmax and x >= xmin) and (
            y >= ymin and y_ <= ymax
        )
    # 第二象限
    if xmax < 1200 and ymax <= 1200:
        xmin = xmin + 1025
        xmax = xmax + 1275
        ymin = ymin + 1035
        ymax = ymax + 1285
        return lambda x, y, x_, y_: (x_ <= xmax and x >= xmin) and (
            y >= ymin and y_ <= ymax
        )
    # 第三象限
    if xmax < 1200 and ymax > 1200:
        xmin = xmin + 1025
        xmax = xmax + 1275
        ymin = ymin - 1175
        ymax = ymax - 925
        return lambda x, y, x_, y_,: (x_ <= xmax and x >= xmin) and (
            y >= ymin and y_ <= ymax
        )


# Parser
def sexp_parser(sexp):
    if sexp[0] in "xyhw":
        return lambda d: eval(f"d.{sexp}")
    if sexp[0] == "-":

        def left_check(d):
            fn = xymapping(d.x, d.y)
            return any(
                [fn(d_.x, d_.y) for d_ in d.lens.left if d_.name.endswith(sexp[1:])]
            )

        return left_check
    if sexp[0] == "+":

        def right_check(d):
            fn = xymapping(d.x, d.y)
            return any(
                [fn(d_.x, d_.y) for d_ in d.lens.right if d_.name.endswith(sexp[1:])]
            )

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

    if sexp[0] == "L":

        def line_check(d):
            fn = linemapping(d.x, d.y, d.x_, d.y_)
            mappings = [d_.name for d_ in d.lens.left if fn(d_.x, d_.y, d_.x_, d_.y_)]
            for name in mappings:
                if name.endswith(sexp[1:]):
                    return True
            return False

        return line_check


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
