from typing import List

from .defect import Defect


class FilterParser:
    def __init__(self):
        pass

    def parse(self, filter_str: str, d_list: List[Defect]) -> List[Defect]:
        new_list = []
        if filter_str == "":
            return d_list
        if filter_str == "A":
            for i in d_list:
                if (i.x>120 and i.x<535) or (i.x>1330 and i.x<1710):
                    new_list.append(i)
            return new_list
        elif filter_str == "B":
            for i in d_list:
                if (i.x>536 and i.x<815) or (i.x>1711 and i.x<1960):
                    new_list.append(i)
            return new_list
        elif filter_str == "C":
            for i in d_list:
                if (i.x>816 and i.x<1085) or (i.x>1961 and i.x<2215):
                    new_list.append(i)
            return new_list
        for f in filter_str.split(" "):
            d_list = self._parse_filter(f, d_list)
        return d_list

    def _parse_filter(self, filter_cmd: str, d_list: List[Defect]) -> List[Defect]:
        if "name=" in filter_cmd:
            new_list= []
            filter_cmd1 = filter_cmd[5:]        #需要筛选出来的信息
            if len(filter_cmd1) == 5:
                filter_cmd3 = filter_cmd[5:-1]    #名称
                filter_cmd2 = filter_cmd1[-1]      #区域
                print(filter_cmd3)
                z1,z2,z3,z4 = self.qy_choice(filter_cmd2)
                for i in d_list:
                    if i.name == filter_cmd3 and ((i.x>int(z1) and i.x<int(z2)) or (i.x>int(z3) and i.x<int(z4))):
                        new_list.append(i)
                return new_list
            else:
                name = filter_cmd1
                return list(filter(lambda d: d.name in name, d_list))
            
        if filter_cmd.startswith("-mark"):
            return list(filter(lambda d: not d.mark, d_list))
        if filter_cmd.startswith("mark"):
            return list(filter(lambda d: d.mark, d_list))
        if filter_cmd.startswith("mod"):
            return list(filter(lambda d: d.lens.modified, d_list))
        if filter_cmd.startswith("-mod"):
            return list(filter(lambda d: not d.lens.modified, d_list))
        if filter_cmd.startswith("fn"):
            xml = filter_cmd[3:]
            return list(filter(lambda d: xml in str(d.lens.xml_path), d_list))
        # if filter_cmd.startswith("name="):
        #     names = filter_cmd[5:].split("+")
        #     return list(filter(lambda d: d.name in names, d_list))
        if (f := filter_cmd[0]) in "xyhw" and filter_cmd[1] in "=<>":
            f_func = eval(f"lambda d: d.{f} {filter_cmd[1]} {filter_cmd[2:]}")
            return list(filter(f_func, d_list))
        if filter_cmd.endswith == "A":
            return list(filter(lambda d: ((d.x>120 and d.x<535) or (d.x>1330 and d.x<1710)), d_list))

        return d_list

    def qy_choice(self,qy):
        if qy == "A":
            return 120,535,1330,1710
        elif qy =="B":
            return 536,815,1711,1960
        elif qy=="C":
            return 816,1085,1961,2215

class QuickSearchSlot:
    def __init__(self):
        self._default_slot = {
            "1": "-mark",
            "2": "mark",
            "3": "mod",
        }

    def set_slot(self, slot: str, filter_str: str):
        self._default_slot[slot] = filter_str

    def get_slot(self, slot: str) -> str:
        return self._default_slot.get(slot, "")
