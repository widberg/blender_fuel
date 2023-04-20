import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator

from . import mesh_z


class ImportFUELMeshZ(Operator, ImportHelper):
    """Import FUEL Mesh_Z"""
    bl_idname = "blender_fuel.import_mesh_z"
    bl_label = "Import FUEL Mesh_Z"

    filename_ext = ".Mesh_Z.d"

    filter_glob: StringProperty(
        default="*.Mesh_Z.d",
        options={'HIDDEN'},
        subtype='DIR_PATH',
        maxlen=2048,
    )

    def execute(self, context):
        collection = mesh_z.import_from_object_directory_path(self.filepath)
        bpy.context.scene.collection.children.link(collection)

        return {'FINISHED'}


def menu_func_import_fuel_mesh_z(self, context):
    self.layout.operator(ImportFUELMeshZ.bl_idname,
                         text="FUEL Mesh_Z (.Mesh_Z.d)")


class ExportFUELMeshZ(Operator, ImportHelper):
    """Export FUEL Mesh_Z"""
    bl_idname = "blender_fuel.export_mesh_z"
    bl_label = "Export FUEL Mesh_Z"

    filename_ext = ".Mesh_Z.d"

    filter_glob: StringProperty(
        default="*.Mesh_Z.d",
        options={'HIDDEN'},
        subtype='DIR_PATH',
        maxlen=2048,
    )

    def execute(self, context):
        mesh_z.export_to_object_directory_path(self.filepath)

        return {'FINISHED'}


def menu_func_export_fuel_mesh_z(self, context):
    self.layout.operator(ExportFUELMeshZ.bl_idname,
                         text="FUEL Mesh_Z (.Mesh_Z.d)")


def register_import():
    bpy.utils.register_class(ImportFUELMeshZ)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_fuel_mesh_z)


def register_export():
    bpy.utils.register_class(ExportFUELMeshZ)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_fuel_mesh_z)


def register():
    register_import()
    register_export()


def unregister_import():
    bpy.utils.unregister_class(ImportFUELMeshZ)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_fuel_mesh_z)


def unregister_export():
    bpy.utils.unregister_class(ExportFUELMeshZ)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_fuel_mesh_z)


def unregister():
    unregister_import()
    unregister_export()


bl_info = {
    "name": "FUEL",
    "author": "widberg",
    "blender": (3, 5, 0),
    "category": "Import-Export",
}

if __name__ == "__main__":
    register()
