import struct
import numpy as np
import utils
from error import Error


class Ps2mc:

    def __init__(self, file_path):
        self.file_path = file_path
        (self.byte_val,
         self.page_size,
         self.pages_per_cluster,
         self.ifc_list,
         self.rootdir_cluster,
         self.alloc_offset,
         ) = self.open()
        self.spare_size = (self.page_size // 128) * 4
        self.raw_page_size = self.page_size + self.spare_size
        self.cluster_size = self.page_size * self.pages_per_cluster
        self.fat_per_cluster = self.cluster_size // 4
        self.fat_matrix = self.__build_fat_matrix()
        self.root_entry = self.get_root_entry()
        self.entries_in_root = self.find_sub_entries(self.root_entry)

    def open(self):
        with open(self.file_path, 'rb') as f:
            byte_val = f.read()
        sb = SuperBlock(byte_val)
        return byte_val, sb.page_len, sb.pages_per_cluster, sb.ifc_list, sb.rootdir_cluster, sb.alloc_offset

    def read_page(self, n):
        offset = self.raw_page_size * n
        return self.byte_val[offset: offset + self.page_size]

    def read_cluster(self, n):
        page_index = n * self.pages_per_cluster
        byte_buffer = bytearray()
        for i in range(self.pages_per_cluster):
            byte_buffer += self.read_page(page_index + i)
        return bytes(byte_buffer)

    def get_fat_value(self, n):
        value = self.fat_matrix[(n // self.fat_per_cluster) % self.fat_per_cluster, n % self.fat_per_cluster]
        return value ^ Fat.ALLOCATED_BIT if value & Fat.ALLOCATED_BIT > 0 else value

    def get_root_entry(self):
        entries = self.read_entry_cluster(self.rootdir_cluster)
        return entries[0].unpack()

    def read_entry_cluster(self, cluster_offset):
        """
        read the entries from an "entry cluster"
        :param cluster_offset: the relative offset of the cluster
        :return: entry list
        """
        cluster_value = self.read_cluster(cluster_offset + self.alloc_offset)
        return Entry.build(cluster_value)

    def find_sub_entries(self, parent_entry):
        chain_start = parent_entry.cluster
        sub_entries = []
        while chain_start != Fat.CHAIN_END:
            entries = self.read_entry_cluster(chain_start)
            for e in entries:
                if len(sub_entries) < parent_entry.length:
                    sub_entries.append(e.unpack())
            chain_start = self.get_fat_value(chain_start)
        return [x for x in sub_entries if not x.name.startswith('.')]

    def read_data_cluster(self, entry):
        """
        read a file's data from a chain of "data cluster"
        :param entry: the entry of the file
        :return: the data bytes of the file
        """
        byte_buffer = bytearray()
        chain_start = entry.cluster
        bytes_read = 0
        while chain_start != Fat.CHAIN_END:
            to_read = min(entry.length - bytes_read, self.cluster_size)
            byte_buffer += self.read_cluster(chain_start + self.alloc_offset)[:to_read]
            bytes_read += to_read
            chain_start = self.get_fat_value(chain_start)
        return bytes(byte_buffer)

    def __build_matrix(self, cluster_list):
        matrix = np.zeros((len(cluster_list), self.fat_per_cluster), np.uint32)
        for index, v in enumerate(cluster_list):
            cluster_value = self.read_cluster(v)
            cluster_value_unpacked = np.frombuffer(cluster_value, np.uint32)
            for index0, v0 in enumerate(cluster_value_unpacked):
                matrix[index, index0] = v0
        return matrix

    def __build_fat_matrix(self):
        indirect_fat_matrix = self.__build_matrix(self.ifc_list)
        indirect_fat_matrix = indirect_fat_matrix.reshape(indirect_fat_matrix.size)
        indirect_fat_matrix = [x for x in indirect_fat_matrix if x != Fat.UNALLOCATED]
        fat_matrix = self.__build_matrix(indirect_fat_matrix)
        return fat_matrix


class SuperBlock:
    """
    struct SuperBlock {
        char magic[28];
        char version[12];
        uint16 page_len;
        uint16 pages_per_cluster;
        uint16 pages_per_block;
        uint16 unknown; // ignore
        uint32 clusters_per_card;
        uint32 alloc_offset;
        uint32 alloc_end;
        uint32 rootdir_cluster;
        uint32 backup_block1; // ignore
        uint32 backup_block2; // ignore
        uint32 unknown[2]; // ignore
        uint32 ifc_list[32];
        uint32 bad_block_list[32]; // ignore
        byte card_type;
        byte card_flags;
        byte unknown; // ignore
        byte unknown; // ignore
    };
    SuperBlock size = 340bytes
    """

    __size = 340
    __struct = struct.Struct("<28s12sHHH2xLLLL4x4x8x128s128xbbxx")
    __magic = b"Sony PS2 Memory Card Format "
    assert __size == __struct.size

    def __init__(self, byte_val):
        if len(byte_val) < SuperBlock.__size:
            raise Error('SuperBlock length invalid.')
        if not byte_val.startswith(SuperBlock.__magic):
            raise Error('SuperBlock magic invalid.')
        (self.magic,
         self.version,
         self.page_len,
         self.pages_per_cluster,
         self.pages_per_block,
         self.clusters_per_card,
         self.alloc_offset,
         self.alloc_end,
         self.rootdir_cluster,
         self.ifc_list,
         self.card_type,
         self.card_flags
         ) = SuperBlock.__struct.unpack(byte_val[:SuperBlock.__size])
        self.ifc_list = [x for x in np.frombuffer(self.ifc_list, np.uint32) if x > 0]


class Entry:
    """
    struct Entry {
        uint16 mode;
        uint16 unknown; // ignore
        uint32 length;
        char created[8];
        uint32 cluster;
        uint32 dir_entry; // ignore
        char modified[8];
        uint32 attr; // ignore
        char padding[28]; // ignore
        char name[32];
        char padding[416]; // ignore
    };
    Entry size = 512bytes
    """

    MODE_PROTECTED = 0x0008
    MODE_FILE = 0x0010
    MODE_DIR = 0x0020
    MODE_HIDDEN = 0x2000
    MODE_EXISTS = 0x8000

    __size = 512
    __struct = struct.Struct("<H2xL8sL4x8s4x28x32s416x")
    __tod_struct = struct.Struct("<xBBBBBH")  # secs, mins, hours, mday, month, year
    assert __size == __struct.size

    def __init__(self, byte_val):
        self.byte_val = byte_val
        self.mode = None
        self.length = None
        self.created = None
        self.cluster = None
        self.modified = None
        self.name = None

    def unpack(self):
        (self.mode,
         self.length,
         self.created,
         self.cluster,
         self.modified,
         self.name
         ) = Entry.__struct.unpack(self.byte_val)
        self.created = Entry.__tod_struct.unpack(self.created)
        self.modified = Entry.__tod_struct.unpack(self.modified)
        self.name = utils.decode_name(utils.zero_terminate(self.name))
        return self

    @staticmethod
    def build(byte_val):
        entry_count = len(byte_val) // Entry.__size
        entries = []
        for i in range(entry_count):
            entries.append(Entry(byte_val[i * Entry.__size: i * Entry.__size + Entry.__size]))
        return entries

    def is_dir(self):
        return self.mode & (Entry.MODE_DIR | Entry.MODE_EXISTS) == (Entry.MODE_DIR | Entry.MODE_EXISTS)

    def is_file(self):
        return self.mode & (Entry.MODE_FILE | Entry.MODE_EXISTS) == (Entry.MODE_FILE | Entry.MODE_EXISTS)

    def is_exists(self):
        return self.mode & Entry.MODE_EXISTS > 0


class Fat:
    ALLOCATED_BIT = 0x80000000
    UNALLOCATED = 0xFFFFFFFF
    CHAIN_END = 0x7FFFFFFF
