import math
import mathutils
import bpy



####interpolation####
def lerp(a, b, t):
    return (1 - t) * a + t * b

def lerp_vector(a, b, t):
    r = [0, 0, 0]
    r[0] = lerp(a[0], b[0], t)
    r[1] = lerp(a[1], b[1], t)
    r[2] = lerp(a[2], b[2], t)
    return r




####vector math####
def check_invalid_vector(v):
    if v == None:
        print("vector is none!")
        return True
    if len(v) != 3:
        print("invalid vector length!")
        return True
    return False


def dot(a, b):
    if check_invalid_vector(a) or check_invalid_vector(b):
        return None
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def cross(a, b):
    if check_invalid_vector(a) or check_invalid_vector(b):
        return None
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]
    return c

def magnitude(v):
    if check_invalid_vector(v):
        return None
    return math.sqrt(dot(v, v))

def normalize(v):
    if check_invalid_vector(v):
        return None
    mag = magnitude(v)
    return [v[0] / mag, v[1] / mag, v[2] / mag]

def scale(v, m):
    if check_invalid_vector(v):
        return None
    return [v[0] * m, v[1] * m, v[2] * m]

def vector_add(a, b):
    if check_invalid_vector(a) or check_invalid_vector(b):
        return None
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


 

####blender related things####

def get_object(name):
    return bpy.data.objects.get(name)


def get_data_bone(object, name):
    return object.data.bones.get(name)
    

def get_pose_bone(object, name):
    return object.pose.bones.get(name)
    
    
def get_edit_bone(object, name):
    return object.data.edit_bones.get(name)


def get_data_on_keyframe(object, name, keyframe, index=0):
    if object.animation_data == None:
        print("No animation data!")
        return None
    fcurve = object.animation_data.action.fcurves.find(name, index=index)
    if fcurve != None:
        return fcurve.evaluate(keyframe)
    return None


def has_keyframe(object, name, frame, index=0):
    if object.animation_data == None:
        print("No animation data!")
        return None
    fcurve = object.animation_data.action.fcurves.find(name, index=index)
    if fcurve != None:
        for keyframe in fcurve.keyframe_points:
            if int(keyframe.co[0]) == frame:
                return True
    return False


def keyframe_pb_transforms(pb, loc=True, rot=True, scale=True, keyf_locked=False):
    if loc:
        for i, j in enumerate(pb.lock_location):
            if not j or keyf_locked:
                pb.keyframe_insert(data_path='location', index=i)  
    if rot:
        rot_dp = 'rotation_quaternion' if pb.rotation_mode == 'QUATERNION' else 'rotation_euler' 
        rot_locks = [i for i in pb.lock_rotation]
        if rot_dp == 'rotation_quaternion':
            rot_locks.insert(0, pb.lock_rotation_w)
        for i, j in enumerate(rot_locks):
            if not j or keyf_locked:
                pb.keyframe_insert(data_path=rot_dp, index=i)
        
    if scale:
        for i, j in enumerate(pb.lock_scale):
            if not j or keyf_locked:
                pb.keyframe_insert(data_path='scale', index=i)


# def update_transform():   
#     # hack to trigger the update with a blank rotation operator
#     bpy.ops.transform.rotate(value=0, orient_axis='Z', orient_type='VIEW', orient_matrix=((0.0, 0.0, 0), (0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='VIEW', mirror=False)



def get_world_location(obj):
    return obj.matrix_world.to_translation()


def get_world_location_of_pose_bone(pose_bone):
    return pose_bone.id_data.matrix_world @ pose_bone.matrix @ pose_bone.location



def convert_to_local_direction(obj, bone, global_direction):
    matrix_world = obj.convert_space(pose_bone=bone, 
        matrix=mathutils.Matrix.Identity(4), 
        from_space='WORLD', 
        to_space='LOCAL')
    return matrix_world @ mathutils.Vector([global_direction[0], global_direction[1], global_direction[2], 0])


def convert_to_local_location(obj, bone, global_location):
    matrix = mathutils.Matrix.Translation(mathutils.Vector(global_location))
    matrix_local = obj.convert_space(pose_bone=bone, 
        matrix=matrix, 
        from_space='WORLD', 
        to_space='LOCAL')
    return matrix_local.to_translation()


def find_layer_collection_recursive(root_layer_collection, name):
    result = None
    if (root_layer_collection.name == name):
        return root_layer_collection
    for child in root_layer_collection.children:
        result = find_layer_collection_recursive(child, name)
        if result != None:
            return result



####pose library related things####
def load_pose(action, bone_name):
    location = [0, 0, 0]
    rotation_quaternion = [1, 0, 0, 0]
    for fcurve in action.fcurves:
        # path_array = fcurve.data_path.split(".")
        path = fcurve.data_path
        if path == f"pose.bones[\"{bone_name}\"].location":
            location[fcurve.array_index] = fcurve.keyframe_points[0].co[1]
        if path == f"pose.bones[\"{bone_name}\"].rotation_quaternion":
            rotation_quaternion[fcurve.array_index] = fcurve.keyframe_points[0].co[1]

    return {"location": mathutils.Vector(location), "rotation_quaternion": mathutils.Quaternion(rotation_quaternion)}


# [start, end - 1] 
def set_bone_pose(bone, pose, start, end, world_space = False, armature = None):
    set_bone_position(bone, pose["location"], start, end, world_space, armature)
    set_rotation(bone, pose["rotation_quaternion"], start, end)

# [start, end - 1] 
def set_bone_position(bone, pos, start, end, world_space = False, armature = None):
    if pos == None:
        print("Bone position shouldn't be none!")
        bone.location = (0, 0, 0)
        bone.keyframe_insert('location', frame=start)
        bone.keyframe_insert('location', frame=end - 1)
        return

    if world_space:

        #get bone matrix in start frame
        if bpy.context.scene.frame_current != start:
            bpy.context.scene.frame_set(start)


        matrix_world = armature.convert_space(pose_bone=bone, 
            matrix=bone.matrix, 
            from_space='POSE', 
            to_space='WORLD')
        matrix_world.translation = pos

        has_child_of_constraint = False
        parent_matrix = None
        # TODO: only consider the condition when it has subtarget and influence == 1 so far.
        for c in bone.constraints: 
            if c.type == 'CHILD_OF' and c.target != None and c.influence == 1.0:
                has_child_of_constraint = True
                parent_bone = get_pose_bone(c.target, c.subtarget)
                parent_matrix = c.inverse_matrix.inverted() @ parent_bone.matrix.inverted()


        if has_child_of_constraint:
            bone.matrix = parent_matrix @ matrix_world
        else:
            bone.matrix = armature.convert_space(pose_bone=bone, 
            matrix=matrix_world, 
            from_space='WORLD', 
            to_space='POSE')
               

    else:
        bone.location = pos


    bone.keyframe_insert('location', frame=start)
    bone.keyframe_insert('location', frame=end - 1)
    # print(f"set {bone} to {pos} at {start}-{end}")

# [start, end - 1] 
def set_rotation(bone, quaternion, start, end):
    if quaternion == None:
        print("Quaternion is None")
        # bone.rotation_quaternion = (1, 0, 0, 0)
        # bone.keyframe_insert('rotation_quaternion', frame=start)
        # bone.keyframe_insert('rotation_quaternion', frame=end - 1)
        return

    bone.rotation_quaternion = quaternion
    bone.keyframe_insert('rotation_quaternion', frame=start)
    bone.keyframe_insert('rotation_quaternion', frame=end - 1)
    # print(f"set {bone} to {quaternion} at {start}-{end}")

