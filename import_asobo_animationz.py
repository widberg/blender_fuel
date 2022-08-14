import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
import io, struct, collections, math, numpy

class AnimationZ:
    def __init__(self, data):
        # Header
        bs = io.BytesIO(data)
        s = struct.Struct('<IIIIII')
        ClassHeader = collections.namedtuple('ClassHeader', 'data_size links_size decompressed_size compressed_size class_crc32 crc32')
        class_header = ClassHeader._make(s.unpack(bs.read(s.size)))
        
        assert class_header.compressed_size == 0, "Compressed objects not allowed"
        
        # Links
        bs.seek(class_header.links_size, io.SEEK_CUR) # skip links
        
        # Data
        pass
        

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
