
from logging import debug
from pathlib import Path

from xml.etree.ElementTree import Element, parse

from io_soulworker.core.vis_material import VisMaterial
from io_soulworker.core.vis_chunk_file import VisChunkFileReader
from io_soulworker.core.vis_chunk_id import VisChunkId
from io_soulworker.core.binary_reader import BinaryReader
from io_soulworker.chunks.subm_chunk import SubmChunk
from io_soulworker.chunks.mtrs_chunk import MtrsChunk
from io_soulworker.chunks.vmsh_chunk import VMshChunk
from io_soulworker.chunks.skel_chunk import SkelChunk
from io_soulworker.core.vis_transparency_type import VisTransparencyType
from io_soulworker.core.xml_helper.exchange_transparency import exchange_transparency


class ModelFileReader(VisChunkFileReader):

    def on_surface(self, _: MtrsChunk): debug('Not impl callback')
    def on_mesh(self, _: VMshChunk): debug('Not impl callback')
    def on_skeleton(self, _: SkelChunk): debug('Not impl callback')
    def on_skeleton_weights(self): debug('Not impl callback')
    def on_vertices_material(self, _: SubmChunk): debug('Not impl callback')

    def on_chunk_start(self, cid: VisChunkId, reader: BinaryReader) -> None:
        if cid == VisChunkId.MTRS:
            self.__parse_materials(reader)

        elif cid == VisChunkId.VMSH:
            self.__parse_mesh(cid, reader)

        elif cid == VisChunkId.SKEL:
            self.__parse_skeleton(reader)

        elif cid == VisChunkId.WGHT:
            self.on_skeleton_weights()

        elif cid == VisChunkId.SUBM:
            self.__parse_vertices_materials(reader)

    def __parse_skeleton(self, reader: BinaryReader):
        self.on_skeleton(SkelChunk(reader))

    def __parse_vertices_materials(self, reader: BinaryReader):
        self.on_vertices_material(SubmChunk(reader))

    def __parse_mesh(self, cid: VisChunkId, reader: BinaryReader):
        self.on_mesh(VMshChunk(cid, reader))

    def __parse_materials(self, reader: BinaryReader):
        overrides = ModelFileReader.__xml_material(reader)

        count = reader.read_uint32()

        for _ in range(count):
            chunk = MtrsChunk(reader)

            override = overrides.get(chunk.name)
            if override:
                chunk.diffuse_map = override.diffuse

            self.on_surface(chunk)

    def __xml_material(reader: BinaryReader) -> dict[str, VisMaterial]:
        paths = ModelFileReader.__materials_paths(Path(reader.name))

        values = dict()

        for path in paths:
            debug('try load from: %s', path)

            if Path.exists(path):
                debug('load from: %s', path)
                values.update(ModelFileReader.__material_from_file(path))

        return values

    def __material_from_file(path: Path) -> dict[str, VisMaterial]:
        def __float(name: str, node: Element): float(node.attrib.get(name))
        def __int(name: str, node: Element): int(node.attrib.get(name))

        def __color(name: str, node: Element): return [
            int(v) for v in node.attrib.get(name).split(',')]

        def create(node: Element) -> tuple[str, VisMaterial]:
            material = VisMaterial()
            material.name = node.attrib.get("name")

            material.ambient = __color("ambient", node)

            material.diffuse = node.attrib.get("diffuse")
            material.transparency = VisTransparencyType(
                exchange_transparency(node.attrib.get("transparency")))

            material.alphathreshold = __float("alphathreshold", node)

            return [material.name, material]

        xml = parse(path)
        root = xml.getroot()

        materials = root.find('Materials')

        return dict(map(create, (node for node in materials if node.tag == 'Material')))

    def __materials_paths(path: Path):
        # NPC_0001_Mirium.model -> NPC_0001_Mirium.model_data\\materials.xml
        yield path.parent / (path.name + "_data/materials.xml")

        # NPC_0001_Mirium.model -> Overrides\\NPC_0001_Mirium.model_data\\materials.xml
        yield path.parent / "Overrides" / (path.name + "_data/materials.xml")
