from typing import List

from .defect import Defect


class FilterParser:
    def __init__(self):
        pass

    def parse(self, filter_str: str, d_list: List[Defect]) -> List[Defect]:
        new_list = []
        if filter_str == "":
            return d_list
        if filter_str not in ["72","70","75"]:
            self.area = self.some("72")
        else:
            self.area = self.some(filter_str[:2])

            

        if filter_str == "A" or filter_str[2] == "A":
            for i in d_list:
                if (i.x>self.area[0] and i.x<self.area[1]) or (i.x>self.area[2] and i.x<self.area[3]):
                    new_list.append(i)
            return new_list
        elif filter_str == "B" or filter_str[2] == "B":
            for i in d_list:
                if (i.x>self.area[4] and i.x<self.area[5]) or (i.x>self.area[6] and i.x<self.area[7]):
                    new_list.append(i)
            return new_list
        elif filter_str == "C" or filter_str[2] == "C":
            for i in d_list:
                if (i.x>self.area[8] and i.x<self.area[9]) or (i.x>self.area[10] and i.x<self.area[11]):
                    new_list.append(i)
            return new_list
        elif filter_str == "D" or filter_str[2] == "D":
            for i in d_list:
                if (i.x>self.area[12] and i.x<self.area[13]) or (i.x>self.area[14] and i.x<self.area[15] or (i.x>self.area[16] and i.x<self.area[17])) :
                    new_list.append(i)
            return new_list
        for f in filter_str.split(" "):
            d_list = self._parse_filter(f, d_list)
        return d_list

    def some(self,mm):
        if mm =="70":
            return [120,535,1330,1710,536,815,1711,1960,816,1060,1961,2185,0,119,1061,1329,2186,2400]
        elif mm == "72":
            return [120,535,1330,1710,536,815,1711,1960,816,1085,1961,2215,0,119,1086,1329,2216,2400]
        elif mm == "75":
            return [120,535,1330,1710,536,815,1711,1960,816,1135,1961,2240,0,119,1136,1329,2241,2400]

    def _parse_filter(self, filter_cmd: str, d_list: List[Defect]) -> List[Defect]:
        new_list = []
        if "name=" in filter_cmd:
            defect = filter_cmd.split("name=")[1]
            if "-" in defect:
                defect_name = defect.split("-")[0]
                defect_area = defect.split("-")[1]
                Subdivision_area = self.qy_choice(defect_area)
                if defect_area == "D":
                    for i in d_list:
                        if i.name == defect_name and ((i.x>Subdivision_area[0] and i.x<Subdivision_area[1]) or (i.x>Subdivision_area[2] and i.x<Subdivision_area[3]) or (i.x>Subdivision_area[4] and i.x<Subdivision_area[5]) ):
                            new_list.append(i)
                    return new_list
                else:
                    for i in d_list:
                        if i.name == defect_name and ((i.x>Subdivision_area[0] and i.x<Subdivision_area[1]) or (i.x>Subdivision_area[2] and i.x<Subdivision_area[3])):
                            new_list.append(i)
                    return new_list

            else:
                defect_name = defect
                for i in d_list:
                    if i.name == defect_name:
                        new_list.append(i)
                return new_list
            
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
        return d_list

    def qy_choice(self,area):
        if area == "A":
            return self.area[0:4]
        elif area =="B":
            return self.area[4:8]
        elif area=="C":
            return self.area[8:12]
        elif area == "D":
            return self.area[12:]

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
