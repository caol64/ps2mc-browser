import struct
from . import utils
from .error import Error


class IconSys:
    """
    The "icon.sys" in the PS2 save file is a fixed-size file
    that provides basic information about the 3D icon.
    See https://babyno.top/en/posts/2023/10/parsing-ps2-3d-icon/ for details.

    Structure:
    ```
    struct IconSys {
        char magic[4];
        uint16 unknown; // ignore
        uint16 subtitle_line_break;
        uint32 unknown; // ignore
        uint32 bg_transparency;
        uint32 bg_color_upper_left[4];
        uint32 bg_color_upper_right[4];
        uint32 bg_color_lower_left[4];
        uint32 bg_color_lower_right[4];
        float32 light_dir1[4];
        float32 light_dir2[4];
        float32 light_dir3[4];
        float32 light_color1[4];
        float32 light_color2[4];
        float32 light_color3[4];
        float32 ambient[4];
        char subtitle[68];
        char icon_file_normal[64];
        char icon_file_copy[64];
        char icon_file_delete[64];
        char zeros[512]; // ignore
    };
    ```
    """

    __size = 964
    __struct = struct.Struct("<4s2xH4xI16I28f68s64s64s64s512x")
    __magic = b"PS2D"
    assert __size == __struct.size

    def __init__(self, byte_val: bytes):
        if len(byte_val) != IconSys.__size:
            raise Error("IconSys length invalid.")
        if not byte_val.startswith(IconSys.__magic):
            raise Error("Not a valid IconSys.")
        __icon_sys = IconSys.__struct.unpack(byte_val)
        subtitle_line_break = __icon_sys[1]
        subtitle = utils.zero_terminate(__icon_sys[47])
        self.subtitle = (
            utils.decode_sjis(subtitle[:subtitle_line_break]),
            utils.decode_sjis(subtitle[subtitle_line_break:]),
        )
        self.background_transparency = __icon_sys[2]
        self.bg_colors = (
            __icon_sys[3:7],
            __icon_sys[7:11],
            __icon_sys[11:15],
            __icon_sys[15:19],
        )

        self.light_dir = (__icon_sys[19:23], __icon_sys[23:27], __icon_sys[27:31])
        self.light_colors = (__icon_sys[31:35], __icon_sys[35:39], __icon_sys[39:43])
        self.ambient = __icon_sys[43:47]

        self.icon_file_normal = utils.zero_terminate(__icon_sys[48]).decode("ascii")
        self.icon_file_copy = utils.zero_terminate(__icon_sys[49]).decode("ascii")
        self.icon_file_delete = utils.zero_terminate(__icon_sys[50]).decode("ascii")

    def print_info(self):
        print("subtitle", self.subtitle)
        print("background_transparency", self.background_transparency)
        print("bg_colors", self.bg_colors)
        print("light_dir", self.light_dir)
        print("light_colors", self.light_colors)
        print("ambient", self.ambient)
        print("icon_file_normal", self.icon_file_normal)
        print("icon_file_copy", self.icon_file_copy)
        print("icon_file_delete", self.icon_file_delete)


class Icon:
    """
    The icon object stores the 3D icon's vertices, normals, textures,
    animation frames, and other related information.
    See https://babyno.top/en/posts/2023/10/parsing-ps2-3d-icon/ for details.
    """
    __magic = 0x010000
    __animation_header_magic = 0x01
    __icon_header_struct = struct.Struct("<5I")
    __vertex_coords_struct = struct.Struct("<3hH")
    __normal_dir_struct = struct.Struct("<3hH")
    __tex_uv_struct = struct.Struct("<2h")
    __vertex_color_struct = struct.Struct("<4B")
    __animation_header_struct = struct.Struct("<IIfII")
    __frame_data_struct = struct.Struct("<4I")
    __frame_key_struct = struct.Struct("<2f")
    __texture_width = 128
    __texture_height = 128
    __texture_size = __texture_width * __texture_height * 2
    __rgb_texture_size = __texture_width * __texture_height * 3

    def __init__(self, byte_val: bytes):
        self.byte_val = byte_val
        offset = 0
        icon_header = Icon.__icon_header_struct.unpack_from(byte_val, offset)
        offset += Icon.__icon_header_struct.size
        if icon_header[0] != Icon.__magic:
            raise Error("Not a valid Icon.")
        self.animation_shapes = icon_header[1]
        self.tex_type = icon_header[2]
        self.vertex_count = icon_header[4]

        self.vertex_data = utils.zeros((self.vertex_count, self.animation_shapes, 4))
        self.normal_data = utils.zeros((self.vertex_count, 4))
        self.uv_data = utils.zeros((self.vertex_count, 2))
        self.color_data = utils.zeros((self.vertex_count, 4))
        self.texture = None

        for i in range(self.vertex_count):
            for s in range(self.animation_shapes):
                r = Icon.__vertex_coords_struct.unpack_from(byte_val, offset)
                self.vertex_data[i][s][0] = r[0]
                self.vertex_data[i][s][1] = r[1]
                self.vertex_data[i][s][2] = r[2]
                self.vertex_data[i][s][3] = r[3]
                offset += Icon.__vertex_coords_struct.size

            r = Icon.__normal_dir_struct.unpack_from(byte_val, offset)
            self.normal_data[i][0] = r[0]
            self.normal_data[i][1] = r[1]
            self.normal_data[i][2] = r[2]
            self.normal_data[i][3] = r[3]
            offset += Icon.__normal_dir_struct.size

            r = Icon.__tex_uv_struct.unpack_from(byte_val, offset)
            self.uv_data[i][0] = r[0]
            self.uv_data[i][1] = r[1]
            offset += Icon.__tex_uv_struct.size

            r = Icon.__vertex_color_struct.unpack_from(byte_val, offset)
            self.color_data[i][0] = r[0]
            self.color_data[i][1] = r[1]
            self.color_data[i][2] = r[2]
            self.color_data[i][3] = r[3]
            offset += Icon.__vertex_color_struct.size

        (
            magic,
            self.frame_length,
            self.anim_speed,
            self.play_offset,
            self.frame_count,
        ) = Icon.__animation_header_struct.unpack_from(byte_val, offset)
        offset += Icon.__animation_header_struct.size

        if magic != Icon.__animation_header_magic:
            raise Error("Not a valid animation header.")

        for i in range(self.frame_count):
            frame_data = Icon.__frame_data_struct.unpack_from(byte_val, offset)
            offset += Icon.__frame_data_struct.size
            key_count = frame_data[1]
            offset += Icon.__frame_key_struct.size * (key_count - 1)

        if self.tex_type & 0b100 > 0:
            self.texture = self.load_texture(offset)
            self.decode_texture()

    def print_info(self):
        """Utility method for debug."""
        print("animation_shapes", self.animation_shapes)
        print("tex_type", bin(self.tex_type))
        print("vertex_count", self.vertex_count)
        # print('vertex_data', self.vertex_data)
        # print('vertex_data', self.vertex_data[..., 0, :3])
        # print('normal_data', self.normal_data)
        # print('normal_data', self.normal_data[..., :3])
        # print('uv_data', self.uv_data)
        # print('color_data', self.color_data)
        print("frame_length", self.frame_length)
        print("anim_speed", self.anim_speed)
        print("play_offset", self.play_offset)
        print("frame_count", self.frame_count)
        # print('texture', len(self.texture))

    def export_texture(self, dest: str):
        """Utility method to export texture file associated with a specified game."""
        with open(dest, "wb") as f:
            f.write(self.texture)

    def load_texture(self, offset: int) -> bytes:
        """
        Load texture according to the texture type.
        """
        if self.tex_type & 0b1000 > 0:
            return self.load_texture_compressed(offset)
        else:
            return self.byte_val[offset: offset + Icon.__texture_size]

    def load_texture_compressed(self, offset: int) -> bytes:
        """
        Load compressed texture.
        See https://babyno.top/en/posts/2023/10/rle-algorithm-in-ps2/ for details.
        """
        compressed_size = struct.Struct("<I").unpack_from(self.byte_val, offset)[0]
        offset += 4
        rle_code_struct = struct.Struct("<H")
        texture_buf = bytearray()
        rle_offset = 0
        while rle_offset < compressed_size:
            rle_code = rle_code_struct.unpack_from(self.byte_val, offset + rle_offset)[0]
            rle_offset += rle_code_struct.size
            if rle_code & 0x8000:
                next_bytes = 0x8000 - (rle_code ^ 0x8000)
                texture_buf += self.byte_val[
                    offset + rle_offset: offset + rle_offset + next_bytes * 2
                ]
                rle_offset += next_bytes * 2
            else:
                times = rle_code
                if times > 0:
                    next_byte = self.byte_val[
                        offset + rle_offset: offset + rle_offset + 2
                    ]
                    for _ in range(times):
                        texture_buf += next_byte
                    rle_offset += 2
        return bytes(texture_buf)

    def decode_texture(self):
        """
        Decode texture with the Run-Length Encoding (RLE) algorithm.
        See https://babyno.top/en/posts/2023/10/ps2-texture-encoding-algorithm-a1b5g5r5/ for details.
        """
        tex_offset = 0
        rgb_tex_offset = 0
        out = bytearray(Icon.__rgb_texture_size)
        tex_struct = struct.Struct("<H")
        while tex_offset < len(self.texture):
            b = tex_struct.unpack_from(self.texture, tex_offset)[0]
            out[rgb_tex_offset] = (b & 0x1F) << 3
            out[rgb_tex_offset + 1] = ((b >> 5) & 0x1F) << 3
            out[rgb_tex_offset + 2] = ((b >> 10) & 0x1F) << 3
            rgb_tex_offset += 3
            tex_offset += tex_struct.size
        self.texture = bytes(out)
