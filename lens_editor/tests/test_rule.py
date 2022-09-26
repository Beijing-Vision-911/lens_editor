from pytest import fixture
from dataclasses import dataclass
from ..rule import Ruleset


@dataclass
class Lens:
    defects = []
    left = []


@dataclass
class Defect:
    name: str
    x: int = 0
    y: int = 0
    h: int = 0
    w: int = 0
    lens: Lens = Lens()


def test_rule_x():
    rule = Ruleset("1111 x>10")
    d = Defect("1111", x=11)
    assert rule(d) is not None


def test_rule_multiple():
    rule = Ruleset("1111 x>10 y>10")
    d = Defect("1111", x=11, y=9)
    assert rule(d) is not None


def test_rule_pass():
    rule = Ruleset("1111 x>10 y>5 w>5 h>5")
    d = Defect("1111", x=9, y=4, w=4, h=4)
    assert rule(d) is None


def test_rule_empty():
    rule = Ruleset("1111 x>10")
    d = Defect("2222", x=9)
    assert rule(d) is None


def test_rule_left_contain():
    rule = Ruleset("1111 -01")
    d = Defect("1111", x=9)
    left = [Defect("0001", x=9)]
    d.lens.left = left
    assert rule(d) == "found ['0001'] in left"
