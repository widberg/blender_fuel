import bpy
import os
import json
from itertools import chain

def load_mesh_buffers(object_json):
    obs = []
    for i in range(0, len(object_json['body']['mesh_buffers']['index_buffers'])):
        me = bpy.data.meshes.new("Mesh" + str(i))

        positions = [[x['position'][0], x['position'][1], x['position'][2]] for x in object_json['body']['mesh_buffers']['vertex_buffers'][i]['vertices']]

        indices = object_json['body']['mesh_buffers']['index_buffers'][i]['indices']
        faces = [[indices[i + 2], indices[i + 1], indices[i + 0]] for i in range(0, len(indices), 3)]

        me.from_pydata(positions, [], faces)

        uv_layer = me.uv_layers.new()
        for face in me.polygons:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                uv_layer.data[loop_idx].uv = object_json['body']['mesh_buffers']['vertex_buffers'][i]['vertices'][vert_idx]['uv']

        normals = [[x['normal'][0], x['normal'][1], x['normal'][2]] for x in object_json['body']['mesh_buffers']['vertex_buffers'][i]['vertices']]
        me.normals_split_custom_set_from_vertices(normals)
        
        me.calc_tangents()

        me.validate(clean_customdata=False)
        me.update()
        obs.append(bpy.data.objects.new("Mesh" + str(i), me))
    return obs


def import_from_object_directory_path(directory_path):
    object_json_path = os.path.join(directory_path, 'object.json')
    with open(object_json_path, 'r') as object_json_file:
        object_json = json.load(object_json_file)
    hash = os.path.basename(os.path.dirname(directory_path)).split('.')[0]
    collection = bpy.data.collections.new(hash + '.Mesh_Z')

    for mesh_bufffer_object in load_mesh_buffers(object_json):
        collection.objects.link(mesh_bufffer_object)

    return collection

def normalize_mesh_object_for_export(ob):
    """Clean up the mesh before export"""
    bpy.ops.object.transform_apply(location = True, scale = True, rotation = True)
    # TODO: Split vertices if multiple UV coordinates
    # https://github.com/OpenSAGE/OpenSAGE.BlenderPlugin/issues/63
    # https://blender.stackexchange.com/a/121741
    # TODO: Apply normalization only to exported data. Do not modify any objects in Blender.
    # TODO: Apply rotation to make Y up

def export_to_object_directory_path(directory_path):
    object_json_path = os.path.join(directory_path, 'object.json')
    ob = bpy.context.object
    me = ob.data

    normalize_mesh_object_for_export(ob)

    vertices = [{'position': v.co[0:3], 'tangent': [0, 0, 0], 'pad0': 1, 'normal': v.normal[0:3], 'pad1': 255, 'uv': [0, 0], 'luv': [0, 0]} for v in me.vertices]
    for face in me.polygons:
        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
            uv_coords = me.uv_layers.active.data[loop_idx].uv
            vertices[vert_idx]['uv'] = [uv_coords.x, 1 - uv_coords.y]
            vertices[vert_idx]['tangent'] = me.loops[loop_idx].tangent[0:3]

    indices = list(chain.from_iterable([[l.vertices[2], l.vertices[1], l.vertices[0]] for l in me.loop_triangles]))

    object_json = {
        'vertices': vertices,
        'indices': indices,
    }

    with open(object_json_path, 'w') as object_json_file:
        json.dump(object_json, object_json_file, indent=2)
