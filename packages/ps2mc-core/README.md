# ps2mc
A Python library for working with PlayStation 2 memory card files.

## Installation

```
pip install ps2mc
```

## Quick Start

### Example 1: Use the high-level `Browser` wrapper

```python
with Browser("my_memory_card.ps2") as browser:
    root_dir = browser.list_root_dir()
    browser.export("game_name", ".")
```

### Example 2: Subclass `Ps2mc` for custom parsing

```python
class MemcardReader(Ps2mc):
    def read_save_entries(self) -> list[Saka04SaveEntry]:
        save_entries: list[Saka04SaveEntry] = list()
        root_entries = [e for e in self.entries_in_root if e.is_exists()]
        for entry in [e for e in root_entries if e.name.startswith("BISLPM-65530Saka_G")]:
            sub_entries = self.lookup_entry_by_name(entry.name)
            for sub_entry in sub_entries:
                if sub_entry.is_file():
                    if sub_entry.name == entry.name:
                        main_save_entry = self.read_data_cluster(sub_entry)
                    if sub_entry.name == 'head.dat':
                        save_head_entry = self.read_data_cluster(sub_entry)
                    if sub_entry.name == 'icon.sys':
                        sys_icon_entry = self.read_data_cluster(sub_entry)
            save_entries.append(Saka04SaveEntry(entry.name, main_save_entry, save_head_entry, sys_icon_entry))
        return save_entries
```

## Documentation
- [Analyze the file system of the PS2 memory card](https://babyno.top/en/posts/2023/09/parsing-ps2-memcard-file-system/)
- [Export save files from the PS2 memory card](https://babyno.top/en/posts/2023/09/exporting-file-from-ps2-memcard/)

## Reference
- [gothi - icon.sys format](https://www.ps2savetools.com/documents/iconsys-format/)
- [Martin Akesson - PS2 Icon Format v0.5](http://www.csclub.uwaterloo.ca:11068/mymc/ps2icon-0.5.pdf)
- [Florian Märkl - mymcplus](https://git.sr.ht/~thestr4ng3r/mymcplus)
- [Ross Ridge - PlayStation 2 Memory Card File System](https://www.ps2savetools.com/ps2memcardformat.html)

## License
MIT License
