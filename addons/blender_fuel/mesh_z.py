import bpy
import os
import json

def load_mesh_buffers(object_json):
    obs = []
    for i in range(0, len(object_json['body']['mesh_buffers']['index_buffers'])):
        me = bpy.data.meshes.new("Mesh" + str(i))

        positions = [x['position'] for x in object_json['body']['mesh_buffers']['vertex_buffers'][i]['vertices']]

        indices = object_json['body']['mesh_buffers']['index_buffers'][i]['indices']
        faces = [indices[i:i + 3] for i in range(0, len(indices), 3)]

        me.from_pydata(positions, [], faces)

        uv_layer = me.uv_layers.new()
        for face in me.polygons:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                uv_layer.data[loop_idx].uv = object_json['body']['mesh_buffers']['vertex_buffers'][i]['vertices'][vert_idx]['uv']

        normals = [x['normal'] for x in object_json['body']['mesh_buffers']['vertex_buffers'][i]['vertices']]
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
