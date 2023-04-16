import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import io, struct, collections, math, numpy

import random


def snorm_to_float(x):
    return x / 255.0 * 2 - 1

def get_material(material_crc32):
    material_name = str(material_crc32)
    mat = bpy.data.materials.get(material_name)

    if mat:
        return mat
    
    mat = bpy.data.materials.new(name=material_name)

    random.seed(material_crc32)
    r = random.uniform(0, 1)
    g = random.uniform(0, 1)
    b = random.uniform(0, 1)
    mat.diffuse_color = (r, g, b, 1)
    return mat

class MeshZ:
    header_points = []
    
    material_crc32s = []
    cylindre_cols = []
    unknown7s = []
    vertex_buffers = []
    index_buffers = []
    unknown11s = []
    vertex_groups = []
    unknown12s = []
    unknown16s = []
    unknown15s = []
    unknown15_indicies = []
    
    def __init__(self, data):
        # Header
        bs = io.BytesIO(data)
        s = struct.Struct('<IIIIII')
        ClassHeader = collections.namedtuple('ClassHeader', 'data_size links_size decompressed_size compressed_size class_crc32 crc32')
        class_header = ClassHeader._make(s.unpack(bs.read(s.size)))
        
        assert class_header.compressed_size == 0, "Compressed objects not allowed"
        
        # Links
        bs.seek(1 * 24 * 4 + 1 * 1 * 2, io.SEEK_CUR)
        
        crc32_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(crc32_count * 1 * 4, io.SEEK_CUR)
        print(crc32_count)
        
        bs.seek(1 * 3 * 4, io.SEEK_CUR)
        
        unknown3_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, unknown3_count):
            (x, y, z) = struct.unpack('<fff', bs.read(12))
            (a) = struct.unpack('<f', bs.read(4))
            unknown4 = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            name_crc32 = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            self.header_points.append((x, y, z))
        print(unknown3_count)
        
        unknown4_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, unknown4_count):
            bs.seek(1 * 16 * 4, io.SEEK_CUR)
            bs.seek(1 * 2 * 4, io.SEEK_CUR)
        print(unknown4_count)
        
        # Data
        strip_vertices_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(strip_vertices_count * 3 * 4, io.SEEK_CUR)
        print(strip_vertices_count)
        
        unknown0_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(unknown0_count * 4 * 4, io.SEEK_CUR)
        print(unknown0_count)
        
        texcoord_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(texcoord_count * 2 * 4, io.SEEK_CUR)
        print(texcoord_count)
        
        normal_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(normal_count * 3 * 4, io.SEEK_CUR)
        print(normal_count)
        
        strip_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, strip_count):
            strip_vertices_index_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            bs.seek(strip_vertices_index_count * 1 * 2 + 2 * 4, io.SEEK_CUR)
        print(strip_count)
        
        unknown4_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, unknown4_count):
            unknown0_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            bs.seek(unknown0_count * 2 * 4, io.SEEK_CUR)
        print(unknown4_count)
        
        material_crc32_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, material_crc32_count):
            material_crc32 = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            self.material_crc32s.append(material_crc32)
        print(material_crc32_count)
        
        cylindre_col_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, cylindre_col_count):
            (x, y, z) = struct.unpack('<fff', bs.read(12))
            min_vertex = (x,y,z)
            bs.seek(2 * 2, io.SEEK_CUR)
            (x, y, z) = struct.unpack('<fff', bs.read(12))
            max_vertex = (x,y,z)
            unknown7s_index = int.from_bytes(bs.read(2), byteorder='little', signed=False)
            unknown = int.from_bytes(bs.read(2), byteorder='little', signed=False)
            self.cylindre_cols.append((min_vertex, max_vertex))
        print(cylindre_col_count)
        
        unknown7_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, unknown7_count):
            x = int.from_bytes(bs.read(2), byteorder='little', signed=False)
            y = int.from_bytes(bs.read(2), byteorder='little', signed=False)
            z = int.from_bytes(bs.read(2), byteorder='little', signed=False)
            unknown = int.from_bytes(bs.read(2), byteorder='little', signed=False)
            self.unknown7s.append((x, y, z))
        print(unknown7_count)
        
        unknown8_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(unknown8_count * 8 * 4, io.SEEK_CUR)
        print(unknown8_count)
        
        s = struct.Struct('<fffBBBBBBBBffff')
        Vertex = collections.namedtuple('Vertex', 'x y z tx ty tz tp nx ny nz np u0 v0 u1 v1')
        VertexBuffer = collections.namedtuple('VertexBuffer', 'id positions normals tangents uvs')
        vertex_buffer_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, vertex_buffer_count):
            vertex_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            vertex_size = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            id = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            positions = []
            normals = []
            tangents = []
            uvs = []
            for j in range(0, vertex_count):
                vertex = Vertex._make(s.unpack(bs.read(s.size)))
                positions.append((vertex.x, vertex.y, vertex.z))
                tangents.append((snorm_to_float(vertex.tx), snorm_to_float(vertex.ty), snorm_to_float(vertex.tz)))
                normals.append((snorm_to_float(vertex.nx), snorm_to_float(vertex.ny), snorm_to_float(vertex.nz)))
                uvs.append((vertex.u0, vertex.v0))
                bs.seek(vertex_size - s.size, io.SEEK_CUR)
            self.vertex_buffers.append(VertexBuffer._make((id, positions, normals, tangents, uvs)))
        print(vertex_buffer_count)
        
        IndexBuffer = collections.namedtuple('IndexBuffer', 'id data')
        index_buffer_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, index_buffer_count):
            index_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            id = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            data = []
            for j in range(0, int(index_count / 3)):
                # invert winding order for blender
                a = int.from_bytes(bs.read(2), byteorder='little', signed=False)
                b = int.from_bytes(bs.read(2), byteorder='little', signed=False)
                c = int.from_bytes(bs.read(2), byteorder='little', signed=False)
                data.append((c, b, a))
            self.index_buffers.append(IndexBuffer._make((id, data)))
        print(index_buffer_count)
        
        unknown11_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, unknown11_count):
            (x, y, z) = struct.unpack('<fff', bs.read(12))
            self.unknown11s.append((x,y,z))
            (x, y, z) = struct.unpack('<fff', bs.read(12))
            self.unknown11s.append((x,y,z))
            (x, y, z) = struct.unpack('<fff', bs.read(12))
            self.unknown11s.append((x,y,z))
            (x, y, z) = struct.unpack('<fff', bs.read(12))
            self.unknown11s.append((x,y,z))
            (x, y, z) = struct.unpack('<fff', bs.read(12))
            self.unknown11s.append((x,y,z))
        print(unknown11_count)

        s = struct.Struct('<LLLLLHHLLLLLHH')
        VertexGroup = collections.namedtuple('VertexGroup', 'vertex_buffer_index index_buffer_index z0 z1 flags vertex_buffer_index_begin vertex_buffer_index_end vertex_count index_buffer_index_begin face_count z2 z3 vertex_size material_index')
        vertex_groups_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, vertex_groups_count):
            vertex_group = VertexGroup._make(s.unpack(bs.read(s.size)))
            self.vertex_groups.append(vertex_group)
            unknown1_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            bs.seek(unknown1_count * 7 * 4, io.SEEK_CUR)
        print(vertex_groups_count)
        
        unknown16_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, unknown16_count):
            (x, y, z) = struct.unpack('<fff', bs.read(12))
            min_vertex = (x,y,z)
            bs.seek(2 * 2, io.SEEK_CUR)
            (x, y, z) = struct.unpack('<fff', bs.read(12))
            max_vertex = (x,y,z)
            pairs_index = int.from_bytes(bs.read(2), byteorder='little', signed=False)
            unknown = int.from_bytes(bs.read(2), byteorder='little', signed=False)
            self.unknown16s.append((min_vertex, max_vertex))
        print(unknown16_count)
        
        pair_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(pair_count * 2 * 2, io.SEEK_CUR)
        print(pair_count)
        
        unknown15s_indices = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(unknown15s_indices * 1 * 2, io.SEEK_CUR)
        print(unknown15s_indices)
        
        morph_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, morph_count):
            name_size = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            bs.seek(name_size * 1 * 1, io.SEEK_CUR)
            bs.seek(1 * 4 + 1 * 2, io.SEEK_CUR)
            unknown15_indicies_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            for j in range(0, unknown15_indicies_count):
                x = int.from_bytes(bs.read(2), byteorder='little', signed=False)
                self.unknown15_indicies.append(x)
            unknown15_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            for j in range(0, unknown15_count):
                x = int.from_bytes(bs.read(2), byteorder='little', signed=True) / 1024
                y = int.from_bytes(bs.read(2), byteorder='little', signed=True) / 1024
                z = int.from_bytes(bs.read(2), byteorder='little', signed=True) / 1024
                self.unknown15s.append((x, y, z))
                bs.seek(1 * 2, io.SEEK_CUR)
        print(morph_count)
        
        unknown12_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, unknown12_count):
            x = int.from_bytes(bs.read(2), byteorder='little', signed=True) / 1024
            y = int.from_bytes(bs.read(2), byteorder='little', signed=True) / 1024
            z = int.from_bytes(bs.read(2), byteorder='little', signed=True) / 1024
            self.unknown12s.append((x, y, z))
        print(unknown12_count)


class ImportAsoboMeshZ(Operator, ImportHelper):
    """Import Asobo Mesh_Z"""
    bl_idname = "import_asobo.mesh_z"
    bl_label = "Import Asobo Mesh_Z"

    filename_ext = ".Mesh_Z"
    
    filter_glob: StringProperty(
        default="*.Mesh_Z",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):    
        f = open(self.filepath, 'rb')
        data = f.read()
        f.close()

        mesh = MeshZ(data)
        
        for i in range(0, len(mesh.index_buffers)):
            ob_name = "meshz" + str(i)
            me = bpy.data.meshes.new(ob_name + "Mesh")
            ob = bpy.data.objects.new(ob_name, me)
            me.from_pydata(mesh.vertex_buffers[i].positions, [], mesh.index_buffers[i].data)
            uv_layer = me.uv_layers.new()
            for face in me.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    uv_layer.data[loop_idx].uv = mesh.vertex_buffers[i].uvs[vert_idx]
            for face in me.polygons:
                face.use_smooth = True
            me.use_auto_smooth = True
            me.normals_split_custom_set_from_vertices(mesh.vertex_buffers[i].normals)
            me.calc_tangents()
            #if i == 1:
            #    color_layer = me.vertex_colors.new()
            #    for face in me.polygons:
            #        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
            #            (r,g,b) = mesh.vertex_buffers[2].positions[vert_idx]
            #            color_layer.data[loop_idx].color = (r*10000,g*10000,b*10000,1)
            me.validate(clean_customdata=False)
            me.update()
            context.scene.collection.objects.link(ob)
        
        for ob in bpy.data.objects:
            for i in range(0, len(mesh.material_crc32s)):
                material_crc32 = mesh.material_crc32s[i]
                ob.data.materials.append(get_material(material_crc32))

        for vertex_group in mesh.vertex_groups:
            ob = bpy.data.objects["meshz" + str(vertex_group.index_buffer_index)]
            polygon_index_begin = vertex_group.index_buffer_index_begin // 3
            polygon_index_end = polygon_index_begin + vertex_group.face_count
            for j in range(polygon_index_begin, polygon_index_end):
                p = ob.data.polygons[j]
                p.material_index = vertex_group.material_index

        #if mesh.unknown12s:
        #    ob_name = "meshz" + str(10)
        #    me = bpy.data.meshes.new(ob_name + "Mesh")
        #    ob = bpy.data.objects.new(ob_name, me)
        #    me.from_pydata(mesh.unknown12s, [], [])
        #    me.update()
        #    context.scene.collection.objects.link(ob)
        
        #if mesh.unknown15s:
        #    ob_name = "meshz" + str(20)
        #    me = bpy.data.meshes.new(ob_name + "Mesh")
        #    ob = bpy.data.objects.new(ob_name, me)
        #    me.from_pydata(mesh.unknown15s, [], [])
        #    me.update()
        #    context.scene.collection.objects.link(ob)
        
        if mesh.unknown16s:
            ob_name = "meshz" + str(30)
            me = bpy.data.meshes.new(ob_name + "Mesh")
            ob = bpy.data.objects.new(ob_name, me)
            vertices = []
            for e in mesh.unknown16s:
                vertices.append(e[0])
                vertices.append(e[1])
            me.from_pydata(vertices, [(i * 2, i * 2 + 1) for i in range(0, len(mesh.unknown16s))], [])
            me.update()
            context.scene.collection.objects.link(ob)
    
        if mesh.cylindre_cols:
            ob_name = "meshz" + str(40)
            me = bpy.data.meshes.new(ob_name + "Mesh")
            ob = bpy.data.objects.new(ob_name, me)
            vertices = []
            for e in mesh.cylindre_cols:
                vertices.append(e[0])
                vertices.append(e[1])
            me.from_pydata(vertices, [(i * 2, i * 2 + 1) for i in range(0, len(mesh.cylindre_cols))], [])
            me.update()
            context.scene.collection.objects.link(ob)
        
        if mesh.unknown7s:
            ob_name = "meshz" + str(50)
            me = bpy.data.meshes.new(ob_name + "Mesh")
            ob = bpy.data.objects.new(ob_name, me)
            indices = []
            for x in mesh.unknown7s:
                indices.append((x[0], x[1], x[2]))
            me.from_pydata(mesh.unknown12s, [], indices)
            me.update()
            context.scene.collection.objects.link(ob)
        
        if mesh.unknown11s:
            ob_name = "meshz" + str(60)
            me = bpy.data.meshes.new(ob_name + "Mesh")
            ob = bpy.data.objects.new(ob_name, me)
            indices = []
            me.from_pydata(mesh.unknown11s, [], [])
            me.update()
            context.scene.collection.objects.link(ob)
        
        if mesh.header_points:
            ob_name = "meshz" + str(70)
            me = bpy.data.meshes.new(ob_name + "Mesh")
            ob = bpy.data.objects.new(ob_name, me)
            indices = []
            me.from_pydata(mesh.header_points, [], [])
            me.update()
            context.scene.collection.objects.link(ob)
        
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportAsoboMeshZ.bl_idname, text="Asobo Mesh_Z (.Mesh_Z)")


def register():
    bpy.utils.register_class(ImportAsoboMeshZ)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportAsoboMeshZ)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    bpy.ops.import_asobo.mesh_z('INVOKE_DEFAULT')
