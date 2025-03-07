from io import SEEK_CUR
from io import BufferedReader
from pathlib import Path
from struct import unpack

from mathutils import Quaternion
from mathutils import Vector

from io_soulworker.core.vis_chunk_id import VisChunkId
from io_soulworker.core.vis_color import VisColor
from io_soulworker.core.vis_index_format import VisIndexFormat
from io_soulworker.core.vis_lighting_method import VisLightingMethod
from io_soulworker.core.vis_prim_type import VisPrimitiveType
from io_soulworker.core.vis_transparency_type import VisTransparencyType
from io_soulworker.core.vis_render_state_flags import VisRenderStateFlag
from io_soulworker.core.vis_surface_flags import VisSurfaceFlags
from io_soulworker.core.vis_vector_2_int import VisVector2Int


class BinaryReader(BufferedReader):
    def read_float_vector4(self):
        return Vector([self.read_float(), self.read_float(), self.read_float(), self.read_float()])
    
    def read_float_vector3(self):
        return Vector([self.read_float(), self.read_float(), self.read_float()])

    def read_float_vector2(self):
        return Vector([self.read_float(), self.read_float()])

    def read_uint8_vector2(self):
        return VisVector2Int(self.read_uint8(), self.read_uint8())

    def read_quaternion(self):
        x = self.read_float()
        y = self.read_float()
        z = self.read_float()
        w = self.read_float()

        return Quaternion([w, x, y, z])

    def skip_utf8_uint32_string(self):
        length = self.read_uint32()
        self.seek(length, SEEK_CUR)

    def read_utf8_uint32_string(self) -> str:
        length = self.read_uint32()
        if(length <= 0):
            return ""
        value, = unpack("<%ds" % length, self.read(length))

        return value.decode('cp949')

    def read_color(self) -> VisColor:
        return VisColor(self.read_uint8(), self.read_uint8(), self.read_uint8(), self.read_uint8())

    def read_primitive_type(self) -> VisPrimitiveType:
        return VisPrimitiveType(self.read_uint32())

    def read_surface_flags(self) -> VisSurfaceFlags:
        return VisSurfaceFlags(self.read_uint32())

    def read_lighting_method(self) -> VisLightingMethod:
        return VisLightingMethod(self.read_uint8())

    def read_index_format(self) -> VisIndexFormat:
        return VisIndexFormat(self.read_uint32())

    def read_transparency(self) -> VisTransparencyType:
        return VisTransparencyType(self.read_uint8())

    def read_render_state_flags(self) -> VisRenderStateFlag:
        return VisRenderStateFlag(self.read_uint16())

    def read_cid(self) -> VisChunkId:
        """ Chunk Id """

        return self.read_uint32()

    def read_float(self) -> float: return float(unpack("<f", self.read(4))[0])

    def read_int8(self) -> int: return int(unpack("<b", self.read(1))[0])
    def read_uint8(self) -> int: return int(unpack("<B", self.read(1))[0])

    def read_int16(self) -> int: return int(unpack("<h", self.read(2))[0])
    def read_uint16(self) -> int: return int(unpack("<H", self.read(2))[0])

    def read_uint16_array(self, count: int):
        for _ in range(count):
            yield self.read_uint16()

    def read_uint32_array(self, count: int):
        for _ in range(count):
            yield self.read_uint32()

    def read_int32(self) -> int: return int(unpack("<i", self.read(4))[0])
    def read_uint32(self) -> int: return int(unpack("<I", self.read(4))[0])

    def __init__(self, path: Path) -> None:
        super().__init__(open(path, "rb"))

# https://youtu.be/K741PecDK3c
