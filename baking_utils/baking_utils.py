import bpy
import time

from bpy.types import Context, Operator, Panel
from .. import ui_utils, utils
from typing import Callable

#
# util functions
#

def fast_bake_selected_bones_location(start_frame, end_frame, progress: ui_utils.ProgressCallback = None):
	"""
	Bake the location keyframes for the selected bones in the active armature.
	"""

	obj = bpy.context.active_object

	if obj is None or obj.type != 'ARMATURE':
		print("No active armature object.")
		return
	
	# Ensure we are in pose mode
	bpy.context.view_layer.objects.active = obj
	bpy.ops.object.mode_set(mode='POSE')

	# Gather the selected pose bones
	selected_bones = [bone.name for bone in obj.pose.bones if bone.bone.select]
	if not selected_bones:
		print("No bones selected.")
		return
	
	# total child tasks = num of frames * num of bones
	
	start_time = time.time()  # Start timing
	
	# Build a map from selected bone to its parent_to_rest_matrix
	parent_to_rest_matrix_map = {bone_name: utils.get_parent_to_rest_matrix(obj.pose.bones[bone_name]) for bone_name in selected_bones}

	# Collect final locations without inserting keyframes
	## this is to avoid changing the animation curves while we are still evaluating them

	cached_locations = {bone_name: [] for bone_name in selected_bones} # bone_name to (frame, location) map

	total_child_tasks = (end_frame - start_frame + 1)

	for frame in range(start_frame, end_frame + 1):

		# call progress for this loop
		## this is called only on first level loop for performance issues
		if callable(progress):
			progress(frame - start_frame, total_child_tasks)

		# 

		utils.set_frame_fast(frame)

		for bone_name in selected_bones:
			bone = obj.pose.bones[bone_name]
			location = utils.get_final_local_location(bone, parent_to_rest_matrix_map[bone_name])
			cached_locations[bone_name].append((frame, location))
			

	# Insert keyframe

	child_task_index = 0
	total_child_tasks = len(selected_bones)

	for bone_name in selected_bones:
		
		# call progress for this loop
		## this is called only on first level loop for performance issues
		child_task_index += 1
		if callable(progress):
			progress(child_task_index, total_child_tasks)

		#

		bone = obj.pose.bones[bone_name]
		
		for frame, location in cached_locations[bone_name]:
			bone.location = location
			
			for i in range(3):
				if not bone.lock_location[i]:
					bone.keyframe_insert(data_path='location', frame=frame, index=i, group=bone_name)


	end_time = time.time()  # End timing
	duration = end_time - start_time
	print(f"Animation baking completed in {duration:.2f} seconds.")


def clear_locked_channels_fcurves():
	# Get the active object
	armature = bpy.context.object
	if armature.type != 'ARMATURE':
		print("Active object is not an armature.")
		return

	# Get the active action
	action = armature.animation_data.action if armature.animation_data else None
	if not action:
		print("No active action found for the armature.")
		return

	# Generate a map of selected bones
	selected_bones = {bone.name: bone for bone in armature.pose.bones if bone.bone.select}
	if not selected_bones:
		print("No bones selected.")
		return

	def is_locked_transform_channel(bone, data_path, array_index):
		lock_index = array_index % 3
		
		if "location" in data_path and bone.lock_location[lock_index]:
			return True
		if "rotation_quaternion" in data_path and bone.lock_rotation[lock_index]:
			return True
		if "rotation_euler" in data_path and bone.lock_rotation[lock_index]:
			return True
		if "scale" in data_path and bone.lock_scale[lock_index]:
			return True
		
		return False

	# Loop through all fcurves in the action
	for fcurve in action.fcurves[:]:
		data_path = fcurve.data_path
		
		# Extract the bone name from the data path
		if data_path.startswith("pose.bones"):
			bone_name = data_path.split('"')[1]
			
			# Check if the bone is selected
			bone = selected_bones.get(bone_name)
			if bone and is_locked_transform_channel(bone, data_path, fcurve.array_index):
				action.fcurves.remove(fcurve)
	
	print("Finished removing locked transform fcurves.")
#
# operators
#

##       
## fast bake locations
##
class x_fast_bake_locations_properties(bpy.types.PropertyGroup):
	start_frame : bpy.props.IntProperty(name="start frame")
	end_frame : bpy.props.IntProperty(name="end frame")

class X_ANIM_OT_fast_bake_locations(Operator):
	bl_idname = "x_anim.fast_bake_locations"
	bl_label = "Fast Bake Locations"
	bl_description = ""
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context: Context):
		
		props = bpy.context.scene.x_fast_bake_locations_properties
		start_frame = props.start_frame
		end_frame = props.end_frame

		ui_utils.default_progress_begin()

		fast_bake_selected_bones_location(start_frame, end_frame, ui_utils.default_progress_update)

		ui_utils.default_progress_end()

		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout

		props = bpy.context.scene.x_fast_bake_locations_properties

		row = layout.row()

		row.prop(props, "start_frame")
		row.prop(props, "end_frame")
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)
	

##
## Force Clear Transform
##
   
class X_ANIM_OT_force_clear_transform(Operator):
	bl_idname = "x_anim.force_clear_transform"
	bl_label = "Force Clear Transform"
	bl_description = "Clear transform regardless of locks and insert keyframe"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context: Context):

		utils.force_clear_transforms_for_selected_bones()

		return {'FINISHED'}

##
## Delete Locked Channel's Animation
##
   
class X_ANIM_OT_clear_locked_channels_anim(Operator):
	bl_idname = "x_anim.clear_locked_channels_anim"
	bl_label = "Clear Locked Channels' Anim"
	bl_description = "Clear animation curves of all channels that are locked"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context: Context):

		clear_locked_channels_fcurves()

		return {'FINISHED'}


#
# panel
#


class x_anim_PT_baking_utils(Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "x anim"
	bl_label = "Baking Utils"

	def draw(self, context):
		layout = self.layout
		props = bpy.context.scene.x_anim

		row = layout.row()
		ui_utils.default_operator_button(row, X_ANIM_OT_fast_bake_locations)
		row = layout.row()
		ui_utils.default_operator_button(row, X_ANIM_OT_force_clear_transform)
		row = layout.row()
		ui_utils.default_operator_button(row, X_ANIM_OT_clear_locked_channels_anim)

#
# register
#

class XANIM_MT_submenu(bpy.types.Menu):
	bl_label = "xanim"
	bl_idname = "XANIM_MT_submenu"  # Add bl_idname

	def draw(self, context):
		layout = self.layout
		layout.operator("x_anim.clear_locked_channels_anim")

def draw_in_context_menu(self, context):
	layout = self.layout
	layout.label(text="xanim")
	layout.menu(XANIM_MT_submenu.bl_idname)
	layout.separator()
	
def register():
	bpy.types.Scene.x_fast_bake_locations_properties = bpy.props.PointerProperty(type=x_fast_bake_locations_properties)
	bpy.types.GRAPH_MT_channel.prepend(draw_in_context_menu)
	bpy.types.GRAPH_MT_context_menu.prepend(draw_in_context_menu)
	bpy.types.DOPESHEET_MT_channel_context_menu.prepend(draw_in_context_menu)

def unregister():
	del bpy.types.Scene.x_fast_bake_locations_properties
	bpy.types.GRAPH_MT_channel.remove(draw_in_context_menu)
	bpy.types.GRAPH_MT_context_menu.remove(draw_in_context_menu)
	bpy.types.DOPESHEET_MT_channel_context_menu.remove(draw_in_context_menu)