
from .xml_parser import Defect
from typing import List


class FilterParser:
    def __init__(self):
        pass


    def parse(self, filter_str: str, d_list: List[Defect]) -> List[Defect]:
        if filter_str == '':
            return d_list
        for f in filter_str.split(' '):
            d_list = self._parse_filter(f, d_list)
        return d_list


    def _parse_filter(self, filter_cmd: str, d_list: List[Defect]) -> List[Defect]:
        if filter_cmd.startswith('-mark'):
            return list(filter(lambda d: not d.mark, d_list))
        if filter_cmd.startswith('mark'):
            return list(filter(lambda d: d.mark, d_list))
        if filter_cmd.startswith('mod'):
            return list(filter(lambda d: d.modified, d_list))
        if filter_cmd.startswith('-mod'):
            return list(filter(lambda d: not d.modified, d_list))

        return list(filter(lambda d: d.name.startswith(filter_cmd), d_list))


class QuickSearchSlot:
    def __init__(self):
        self._default_slot = {
            '1': '-mark',
            '2': 'mark',
            '3': 'mod',
        }

    def set_slot(self, slot: str, filter_str: str):
        self._default_slot[slot] = filter_str


    def get_slot(self, slot: str) -> str:
        return self._default_slot.get(slot, '')
