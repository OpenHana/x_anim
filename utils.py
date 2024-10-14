import math
import mathutils
from mathutils import Matrix
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
                pb.keyframe_insert(data_path='location', index=i, group=pb.name)
    if rot:
        rot_dp = 'rotation_quaternion' if pb.rotation_mode == 'QUATERNION' else 'rotation_euler' 
        rot_locks = [i for i in pb.lock_rotation]
        if rot_dp == 'rotation_quaternion':
            rot_locks.insert(0, pb.lock_rotation_w)
        for i, j in enumerate(rot_locks):
            if not j or keyf_locked:
                pb.keyframe_insert(data_path=rot_dp, index=i, group=pb.name)
        
    if scale:
        for i, j in enumerate(pb.lock_scale):
            if not j or keyf_locked:
                pb.keyframe_insert(data_path='scale', index=i, group=pb.name)


# def update_transform():   
#     # hack to trigger the update with a blank rotation operator
#     bpy.ops.transform.rotate(value=0, orient_axis='Z', orient_type='VIEW', orient_matrix=((0.0, 0.0, 0), (0, 0.0, 0.0), (0.0, 0.0, 0.0)), orient_matrix_type='VIEW', mirror=False)



def get_world_location(obj):
    return obj.matrix_world.to_translation()


def get_world_position_of_pose_bone(pose_bone : bpy.types.PoseBone):
    return (pose_bone.id_data.matrix_world @ pose_bone.matrix).to_translation()

def get_world_position_of_pose_bone_tail(pose_bone : bpy.types.PoseBone):
    return pose_bone.id_data.matrix_world @ pose_bone.tail



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


# set position at current frame
def set_bone_position(bone : bpy.types.PoseBone, pos, world_space = False, key = True):
    if pos == None:
        print("Bone position shouldn't be none!")
        return

    if world_space:

        armature : bpy.types.Armature = bone.id_data

        matrix_world = armature.convert_space(pose_bone=bone, 
            matrix=bone.matrix, 
            from_space='POSE', 
            to_space='WORLD')
        matrix_world.translation = pos

        has_child_of_constraint = False
        parent_matrix = None
        # TODO: only consider the condition when it has subtarget and influence == 1 for now.
        for c in bone.constraints: 
            if c.type == 'CHILD_OF' and c.target != None and c.influence >= 0.99:
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

    if key:
        bone.keyframe_insert('location', group=bone.name)


def force_clear_transforms_for_selected_bones():
	# Make sure we're in Pose Mode
	if bpy.context.object.mode != 'POSE':
		bpy.ops.object.posemode_toggle()
	
	obj = bpy.context.active_object
	if obj is None or obj.type != 'ARMATURE':
		print("No active armature object found")
		return
	
	# Function to clear transformations without modifying lock states
	def clear_transform(bone):
		bone.location = (0.0, 0.0, 0.0)
		
		# Check rotation mode and clear accordingly
		if bone.rotation_mode == 'QUATERNION':
			bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
		else:
			bone.rotation_euler = (0.0, 0.0, 0.0)
		
		bone.scale = (1.0, 1.0, 1.0)

		bone.keyframe_insert(data_path="location", group=bone.name)
		bone.keyframe_insert(data_path="rotation_quaternion", group=bone.name)
		bone.keyframe_insert(data_path="scale", group=bone.name)
	
	# Iterate through all selected pose bones
	for bone in obj.pose.bones:
		if bone.bone.select:
			clear_transform(bone)


def get_parent_to_rest_matrix(pose_bone):
	'''	matrix that converts vectors from: given pose_bone's parent to given post_bone's rest'''

	rest_matrix = pose_bone.bone.matrix_local
	
	if pose_bone.parent:
		return rest_matrix.inverted() @ pose_bone.parent.bone.matrix_local
	else:
		# Return identity matrix when there is no parent
		return Matrix.Identity(4)
	
def get_final_current_to_rest_matrix(pose_bone, parent_to_rest_matrix=None):
	'''	final(visual) transform matrix relative to rest.
		visual means after animation, driver and constraints'''
	
	if pose_bone.parent:
		
		# If parent_to_rest_matrix is None, use the get_parent_to_rest_matrix function to get it
		if parent_to_rest_matrix is None:
			parent_to_rest_matrix = get_parent_to_rest_matrix(pose_bone)
		
		parent_pose_matrix = pose_bone.parent.matrix
		
		# Calculate the current-to-parent matrix
		current_to_parent_matrix = parent_pose_matrix.inverted() @ pose_bone.matrix
		
		# Calculate the current-to-rest matrix
		current_to_rest_matrix = parent_to_rest_matrix @ current_to_parent_matrix
		
	else:
		
		rest_matrix = pose_bone.bone.matrix_local
		
		# No parent, so simply invert the rest pose matrix
		current_to_rest_matrix = rest_matrix.inverted() @ pose_bone.matrix

	return current_to_rest_matrix


def get_final_local_location(pose_bone, parent_to_rest_matrix=None):
	'''	final(visual) local location, "local" is relative to rest
		visual means after animation, driver and constraints'''
	
	current_to_rest_matrix = get_final_current_to_rest_matrix(pose_bone, parent_to_rest_matrix)
	
	return current_to_rest_matrix.to_translation()

def set_frame_fast(frame):
	'''	set frame and only update the depsgraph,
		which means only updating what's enabled in the scene
	'''

	# Directly set the scene's frame_current property
	bpy.context.scene.frame_current = frame

	# Update the necessary parts of the dependency graph
	depsgraph = bpy.context.evaluated_depsgraph_get()
	depsgraph.update()

'''
# LEGACY
# [start, end - 1] 
def set_bone_pose(bone, pose, start, end, world_space = False, armature = None):
    set_bone_position(bone, pose["location"], start, end, world_space, armature)
    set_rotation(bone, pose["rotation_quaternion"], start, end)

# LEGACY
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


# LEGACY
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
'''
