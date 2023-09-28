from ps2mc import Ps2mc
from error import Error
import os


class Browser:
    def __init__(self, file_path):
        self.ps2mc = Ps2mc(file_path)

    def list_root_dir(self):
        return [x for x in self.ps2mc.entries_in_root if x.is_exists()]

    def lookup_entry(self, entry):
        return self.ps2mc.find_sub_entries(entry)

    def lookup_entry_by_name(self, name):
        for e in self.ps2mc.entries_in_root:
            if e.name == name and e.is_dir():
                return self.lookup_entry(e)
        raise Error(f'can\'t find game {name}')

    def export(self, name, dest):
        dir_path = dest + os.sep + name
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        entries = self.lookup_entry_by_name(name)
        for e in entries:
            if e.is_file():
                with open(dir_path + os.sep + e.name, 'wb') as f:
                    f.write(self.ps2mc.read_data_cluster(e))

    def list_all(self):
        root_dirs = self.list_root_dir()
        for d in root_dirs:
            print(d.name)
            entries = self.lookup_entry(d)
            for e in entries:
                print(f'    {e.name}')


if __name__ == '__main__':
    browser = Browser('../data/web1.ps2')
    browser.list_all()
