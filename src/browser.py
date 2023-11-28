import os
from typing import List, Tuple

from error import Error
from icon import Icon, IconSys
from ps2mc import Entry, Ps2mc


class Browser:
    """
    The browser wraps Ps2mc and holds a Ps2mc instance for interacting
    with PS2 memory card files.
    """

    def __init__(self, file_path: str):
        """
        Initialize the Browser with the path to a PS2 memory card file.

        Parameters:
        - file_path (str): The path to the PS2 memory card file.
        """
        self.ps2mc = Ps2mc(file_path)

    def list_root_dir(self) -> List[Entry]:
        """
        List entries in the root directory of the memory card.

        Returns:
        List: A list of entries in the root directory.
        """
        return [e for e in self.ps2mc.entries_in_root if e.is_exists()]

    def lookup_entry(self, entry) -> List[Entry]:
        """
        Look up sub-entries for a given entry.

        Parameters:
        - entry: The entry for which sub-entries need to be looked up.

        Returns:
        List: A list of sub-entries.
        """
        return self.ps2mc.find_sub_entries(entry)

    def lookup_entry_by_name(self, name: str) -> List[Entry]:
        """
        Look up entries based on the name of a game.

        Parameters:
        - name (str): The name of the game.

        Returns:
        List: A list of entries associated with the specified game name.

        Raises:
        - Error: If the specified game name cannot be found.
        """
        filters = [
            e for e in self.ps2mc.entries_in_root if e.name == name and e.is_dir()
        ]
        if filters:
            return self.lookup_entry(filters[0])
        raise Error(f"can't find game {name}")

    def export(self, name: str, dest: str):
        """
        Utility method to export files associated with a specified game.

        Parameters:
        - name (str): The name of the game to be exported.
        - dest (str): The destination directory where the files will be exported.

        Raises:
        - Error: If the specified game name cannot be found.
        """
        dir_path = os.path.join(dest, name)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        entries = self.lookup_entry_by_name(name)
        for entry in entries:
            if entry.is_file():
                with open(os.path.join(dir_path, entry.name), "wb") as f:
                    f.write(self.ps2mc.read_data_cluster(entry))

    def print_all(self):
        """
        Utility method to print all entries in the memory card.
        """
        root_dirs = self.list_root_dir()
        for d in root_dirs:
            print(d.name)
            entries = self.lookup_entry(d)
            for entry in entries:
                print(f"    {entry.name}")

    def get_icon(self, name: str) -> Tuple[IconSys, List[Icon]]:
        """
        Get icon information for a specified game.

        Parameters:
        - name (str): The name of the game.

        Returns:
        Tuple: A tuple containing IconSys and a list of Icons associated with the game.
        """
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
        """
        Destroy the Ps2mc instance associated with the Browser.
        """
        self.ps2mc.destroy()
