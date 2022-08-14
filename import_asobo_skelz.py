import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from mathutils import Matrix
import io, struct, collections, math, numpy

class SkelZ:
    bones = []
    
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
        bs.seek(1 * 5 * 4, io.SEEK_CUR)
        
        bone_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, bone_count):
            bs.seek(4 + 160, io.SEEK_CUR)
            trs = numpy.frombuffer(bs.read(64), dtype=numpy.float32, count=16)
            bs.seek(1 * 1 * 4, io.SEEK_CUR)
            parent_index = int.from_bytes(bs.read(4), byteorder='little', signed=True)
            bs.seek(1 * 3 * 4, io.SEEK_CUR)
            self.bones.append((Matrix(trs.reshape((4, 4))), parent_index))
        print(bone_count)
        
        material_crc32_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(material_crc32_count * 1 * 4, io.SEEK_CUR)
        print(material_crc32_count)
        
        mesh_data_crc32_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(mesh_data_crc32_count * 1 * 4, io.SEEK_CUR)
        print(mesh_data_crc32_count)
        
        animation_node_names_arrays = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        for i in range(0, animation_node_names_arrays):
            crc32s = int.from_bytes(bs.read(4), byteorder='little', signed=False)
            bs.seek(crc32s * 1 * 4, io.SEEK_CUR)
        print(animation_node_names_arrays)
        
        some_names_crc32_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(some_names_crc32_count * 1 * 4, io.SEEK_CUR)
        print(some_names_crc32_count)
        
        sphere_col_bones0_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(sphere_col_bones0_count * 7 * 4, io.SEEK_CUR)
        print(sphere_col_bones0_count)
        
        sphere_col_bones1_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(sphere_col_bones1_count * 7 * 4, io.SEEK_CUR)
        print(sphere_col_bones1_count)
        
        box_col_bones_count = int.from_bytes(bs.read(4), byteorder='little', signed=False)
        bs.seek(box_col_bones_count * 19 * 4, io.SEEK_CUR)
        print(box_col_bones_count)
        
        
def bone_traversal(current):    
    for child in current.children:
        child.translate(current.tail)
        bone_traversal(child)


class ImportAsoboSkelZ(Operator, ImportHelper):
    """Import Asobo Skel_Z"""
    bl_idname = "import_asobo.skel_z"
    bl_label = "Import Asobo Skel_Z"

    filename_ext = ".Skel_Z"
    
    filter_glob: StringProperty(
        default="*.Skel_Z",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):    
        f = open(self.filepath, 'rb')
        data = f.read()
        f.close()

        skel = SkelZ(data)
        
        armature = bpy.data.armatures.new("Armature")
        rig = bpy.data.objects.new("Armature", armature)
        context.scene.collection.objects.link(rig)
        context.view_layer.objects.active = rig
        bpy.ops.object.editmode_toggle()
        for i in range(0, len(skel.bones)):
            bone = skel.bones[i]
            trs = bone[0]
            rot = trs.to_quaternion()
            pos = trs.to_translation()
            scale = trs.to_scale()
            
            current_bone = armature.edit_bones.new("bone" + str(i))
            current_bone.head = [0, 0, 0]
            current_bone.tail = [0, 0, 1]
            current_bone.transform(trs)
            
        for i in range(0, len(skel.bones)):
            if skel.bones[i][1] != -1:
                current = armature.edit_bones[i]
                parent = armature.edit_bones[skel.bones[i][1]]
                
                current.parent = parent
                parent.children.append(current)
                
        for i in range(0, len(skel.bones)):
            if skel.bones[i][1] == -1:
                current = armature.edit_bones[i]
                bone_traversal(current)
        bpy.ops.object.editmode_toggle()
        
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportAsoboMeshZ.bl_idname, text="Asobo Skel_Z (.Skel_Z)")


def register():
    bpy.utils.register_class(ImportAsoboSkelZ)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportAsoboSkelZ)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    bpy.ops.import_asobo.skel_z('INVOKE_DEFAULT')
