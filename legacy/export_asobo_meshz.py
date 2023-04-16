import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportAsoboMeshZ(Operator, ExportHelper):
    """Export Asobo Mesh_Z"""
    bl_idname = "export_asobo.mesh_z"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Asobo Mesh_Z"

    # ExportHelper mixin class uses this
    filename_ext = ".Mesh_Z"

    filter_glob: StringProperty(
        default="*.Mesh_Z",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        f = open(filepath, 'wb')
        
        
        
        f.close()

        return {'FINISHED'}


def menu_func_export(self, context):
    self.layout.operator(ExportAsoboMeshZ.bl_idname, text="Asobo Mesh_Z (.Mesh_Z)")


def register():
    bpy.utils.register_class(ExportAsoboMeshZ)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportAsoboMeshZ)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    bpy.ops.export_asobo.mesh_z('INVOKE_DEFAULT')
