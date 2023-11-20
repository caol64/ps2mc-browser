import os
from typing import List, Tuple

from error import Error
from icon import Icon, IconSys
from ps2mc import Ps2mc


class Browser:
    def __init__(self, file_path):
        self.ps2mc = Ps2mc(file_path)

    def list_root_dir(self):
        return [e for e in self.ps2mc.entries_in_root if e.is_exists()]

    def lookup_entry(self, entry):
        return self.ps2mc.find_sub_entries(entry)

    def lookup_entry_by_name(self, name):
        filters = [
            e for e in self.ps2mc.entries_in_root if e.name == name and e.is_dir()
        ]
        if len(filters) > 0:
            return self.lookup_entry(filters[0])
        raise Error(f"can't find game {name}")

    def export(self, name, dest):
        dir_path = dest + os.sep + name
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        entries = self.lookup_entry_by_name(name)
        for entry in entries:
            if entry.is_file():
                with open(dir_path + os.sep + entry.name, "wb") as f:
                    f.write(self.ps2mc.read_data_cluster(entry))

    def list_all(self):
        root_dirs = self.list_root_dir()
        for d in root_dirs:
            print(d.name)
            entries = self.lookup_entry(d)
            for entry in entries:
                print(f"    {entry.name}")

    def get_icon(self, name) -> Tuple[IconSys, List[Icon]]:
        entries = self.lookup_entry_by_name(name)

        icon_sys_entry = [e for e in entries if e.is_file() and e.name == "icon.sys"][0]
        icon_sys = IconSys(self.ps2mc.read_data_cluster(icon_sys_entry))

        icon_names_ = [icon_sys.icon_file_normal, icon_sys.icon_file_copy, icon_sys.icon_file_delete]
        icon_names = []
        for icon_name in icon_names_:
            if icon_name not in icon_names:
                icon_names.append(icon_name)
        icon_entries = [[e for e in entries if e.is_file() and e.name == icon_name][0] for icon_name in icon_names]
        icons = [Icon(self.ps2mc.read_data_cluster(icon_entry)) for icon_entry in icon_entries]
        return icon_sys, icons

    def destroy(self):
        self.ps2mc.destroy()
