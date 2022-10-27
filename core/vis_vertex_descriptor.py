from logging import debug, warn

from io_soulworker.core.binary_reader import BinaryReader
from io_soulworker.core.vis_vector_2_int import VisVector2Int


class VisVertexDescriptor(object):

    MAGICK = 0x1020A0B
    MAX_TEXTURES = 16

    stride: int
    """ Stride of the vertex structure; must be set to the size of the vertex structure. """

    pos_offset: VisVector2Int
    """ Offset of the position vector in the structure. Use bitwise OR with format bitflag constants of type VERTEXDESC_FORMAT_xyz to force a specific format. """

    color_offset: VisVector2Int
    """ Offset of the color vector in the structure. Use bitwise OR with format bitflag constants of type VERTEXDESC_FORMAT_xyz to force a specific format. """

    normal_offset: VisVector2Int
    """ Offset of the normal vector in the structure. Use bitwise OR with format bitflag constants of type VERTEXDESC_FORMAT_xyz to force a specific format. """

    tex_coord_offset: list[VisVector2Int]
    """ Offset of the sets of texture coordinates in the structure. Use bitwise OR with format bitflag constants of type VERTEXDESC_FORMAT_xyz to force a specific format. """

    secondary_color_offset: VisVector2Int
    """ Offset of the secondary color. Not supported on all platforms. """

    first_text_coord: VisVector2Int
    """ Index of the first used texture coordinate set. Set automatically by ComputeHash() or at serialization time. """

    last_text_coord: VisVector2Int
    """ Index of the last used texture coordinate set. Set automatically by ComputeHash() or at serialization time. """

    hash: int
    """ Hash value. Set automatically when computing the hash or at serialization time. """

    def __init__(self, reader: BinaryReader) -> None:

        magick = reader.read_uint32()
        assert self.MAGICK == magick

        self.version = reader.read_uint32()
        debug('version: %d', self.version)

        self.stride = reader.read_uint16()
        self.pos_offset = reader.read_uint8_vector2()
        self.color_offset = reader.read_uint8_vector2()
        self.normal_offset = reader.read_uint8_vector2()
        self.tex_coord_offset = self.__read_uv(reader)
        self.secondary_color_offset = reader.read_uint8_vector2()

        if self.version == 42:
            warn('Need recalc hash')

        if self.version == 48:
            self.first_text_coord = reader.read_uint8()
            self.last_text_coord = reader.read_uint8()
            self.hash = reader.read_uint32()

        if self.MAGICK == reader.read_uint32():
            self.secondary_color_offset = -1

    def __read_uv(self, reader: BinaryReader):
        return [reader.read_uint8_vector2() for _ in range(self.MAX_TEXTURES)]

# https://youtu.be/UnIhRpIT7nc
