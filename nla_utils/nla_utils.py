import bpy
import mathutils
from bpy.types import Context, Operator, Panel
from .. import ui_utils, utils
from typing import Callable

#
# util functions
#


#
# operators
#

##       
## center eye lookat
##
class x_anim_nla_utils_properties(bpy.types.PropertyGroup):
	source : bpy.props.PointerProperty(name="source", type=bpy.types.Object)
	target : bpy.props.PointerProperty(name="target", type=bpy.types.Object)

class X_ANIM_OT_copy_nla_stack(Operator):
	bl_idname = "x_anim.copy_nla_stack"
	bl_label = "Copy NLA Stack"
	bl_description = "use this, don't use 'Link Animation Data' to 'copy', that is not really copy, will cause problems"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context: Context):
		
		props = bpy.context.scene.x_anim_nla_utils
		source : bpy.types.Object = props.source
		target : bpy.types.Object = props.target

		# reference: https://blender.stackexchange.com/questions/74183/how-can-i-copy-nla-tracks-from-one-armature-to-another

		'''
		# by xuxing:
		# this will clear all drivers on target, cuz drivers are part of animation data
		# so, don't clear

		if target.animation_data is not None:
			target.animation_data_clear()

		target.animation_data_create()   
		'''

		source_animation_data = source.animation_data
		target_animation_data = target.animation_data

		if source_animation_data is None:
			return {'FINISHED'}

		for src_track in source_animation_data.nla_tracks:

			target_track = target_animation_data.nla_tracks.new()

			target_track.name = src_track.name
			#target_track.active = src_track.active
			target_track.lock = src_track.lock
			target_track.mute = src_track.mute
			target_track.is_solo = src_track.is_solo

			for source_action_strip in src_track.strips:
				bla= target_track.strips.new(
				source_action_strip.action.name,
				int(source_action_strip.frame_start),
				source_action_strip.action)
			
				bla.name = source_action_strip.name
				bla.frame_start = source_action_strip.frame_start
				bla.frame_end = source_action_strip.frame_end 
				bla.extrapolation = source_action_strip.extrapolation
				bla.blend_type = source_action_strip.blend_type
				bla.use_auto_blend = source_action_strip.use_auto_blend       
				bla.blend_in = source_action_strip.blend_in
				bla.blend_out= source_action_strip.blend_out            
				bla.mute = source_action_strip.mute
				bla.use_reverse = source_action_strip.use_reverse
			
				bla.action_frame_start = source_action_strip.action_frame_start
				bla.action_frame_end = source_action_strip.action_frame_end
				bla.scale = source_action_strip.scale
				bla.repeat = source_action_strip.repeat 
				bla.use_animated_influence = source_action_strip.use_animated_influence
				bla.influence = source_action_strip.influence            
				bla.use_animated_time = source_action_strip.use_animated_time
				bla.use_animated_time_cyclic = source_action_strip.use_animated_time_cyclic
				bla.strip_time = source_action_strip.strip_time

		return {'FINISHED'}
	
##
## NLA copy name 
##

def get_active_nla_track(obj: bpy.types.Object) -> bpy.types.NlaTrack:
	if obj is None or obj.type != 'ARMATURE':
		return None
	if obj.animation_data is None:
		return None
	return obj.animation_data.nla_tracks.active

def get_active_nla_strip(obj: bpy.types.Object) -> bpy.types.NlaStrip:
	if obj is None or obj.type != 'ARMATURE':
		return None
	if obj.animation_data is None or obj.animation_data.nla_tracks.active is None:
		return None
	return next((strip for strip in obj.animation_data.nla_tracks.active.strips if strip.select), None)

def get_active_nla_clip(obj: bpy.types.Object) -> bpy.types.Action:
	active_strip = get_active_nla_strip(obj)
	if active_strip is None:
		return None
	return active_strip.action

class X_ANIM_OT_copy_name_clip_to_strip(Operator):
	bl_idname = "x_anim.clip_name_to_strip"
	bl_label = "Clip Name to Strip"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context: Context):
		get_active_nla_strip(context.object).name = get_active_nla_clip(context.object).name
		return {'FINISHED'}
	
class X_ANIM_OT_copy_name_clip_to_track(Operator):
	bl_idname = "x_anim.clip_name_to_track"
	bl_label = "Clip Name to Track"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context: Context):
		get_active_nla_track(context.object).name = get_active_nla_clip(context.object).name
		return {'FINISHED'}

class X_ANIM_OT_copy_name_strip_to_track(Operator):
	bl_idname = "x_anim.strip_name_to_track"
	bl_label = "Strip Name to Track"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context: Context):
		get_active_nla_track(context.object).name = get_active_nla_strip(context.object).name
		return {'FINISHED'}

class X_ANIM_OT_copy_name_strip_to_clip(Operator):
	bl_idname = "x_anim.strip_name_to_clip"
	bl_label = "Strip Name to Clip"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context: Context):
		get_active_nla_clip(context.object).name = get_active_nla_strip(context.object).name
		return {'FINISHED'}

class X_ANIM_OT_copy_name_track_to_clip(Operator):
	bl_idname = "x_anim.track_name_to_clip"
	bl_label = "Track Name to Clip"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context: Context):
		get_active_nla_clip(context.object).name = get_active_nla_track(context.object).name
		return {'FINISHED'}

class X_ANIM_OT_copy_name_track_to_strip(Operator):
	bl_idname = "x_anim.track_name_to_strip"
	bl_label = "Track Name to Strip"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context: Context):
		get_active_nla_strip(context.object).name = get_active_nla_track(context.object).name
		return {'FINISHED'}

def draw_copy_name_buttons_in_panel(self, context):

	layout = self.layout
	layout.label(text="Copy names:")
	row = layout.row()
	row.operator(X_ANIM_OT_copy_name_track_to_strip.bl_idname, text="Track → Strip")
	row.operator(X_ANIM_OT_copy_name_track_to_clip.bl_idname, text="Track → Clip")
	row = layout.row()
	row.operator(X_ANIM_OT_copy_name_strip_to_track.bl_idname, text="Strip → Track")
	row.operator(X_ANIM_OT_copy_name_strip_to_clip.bl_idname, text="Strip → Clip")
	row = layout.row()
	row.operator(X_ANIM_OT_copy_name_clip_to_track.bl_idname, text="Clip → Track")
	row.operator(X_ANIM_OT_copy_name_clip_to_strip.bl_idname, text="Clip → Strip")

def draw_copy_name_buttons_in_menu(self, context):

	layout = self.layout
	layout.label(text="Copy names:")
	layout.operator(X_ANIM_OT_copy_name_track_to_strip.bl_idname)
	layout.operator(X_ANIM_OT_copy_name_track_to_clip.bl_idname)
	layout.operator(X_ANIM_OT_copy_name_strip_to_track.bl_idname)
	layout.operator(X_ANIM_OT_copy_name_strip_to_clip.bl_idname)
	layout.operator(X_ANIM_OT_copy_name_clip_to_track.bl_idname)
	layout.operator(X_ANIM_OT_copy_name_clip_to_strip.bl_idname)

#
# menu
#

class X_ANIM_MT_nla_utils_menu(bpy.types.Menu):
	bl_label = "NLA Utils Menu"
	bl_idname = "X_ANIM_MT_nla_utils_menu"

	def draw(self, context):
		layout = self.layout
		layout.operator(X_ANIM_OT_copy_name_clip_to_strip.bl_idname)
		layout.operator(X_ANIM_OT_copy_name_strip_to_track.bl_idname)

def draw_nla_utils_menu(self, context):
	self.layout.label(text="xanim")
	self.layout.menu(X_ANIM_MT_nla_utils_menu.bl_idname)
	self.layout.separator()

#
# panel
#

class X_ANIM_PT_nla_utils_view3d(Panel):
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "x anim"
	bl_label = "NLA Utils"

	def draw(self, context):
		layout = self.layout
		props = bpy.context.scene.x_anim_nla_utils

		row = layout.row()
		row.prop(props, "source")
		row = layout.row()
		row.prop(props, "target")

		row = layout.row()
		ui_utils.default_operator_button(row, X_ANIM_OT_copy_nla_stack)


class X_ANIM_PT_nla_utils_nla_editor(Panel):
	bl_space_type = "NLA_EDITOR"
	bl_region_type = "UI"
	bl_category = "Strip"
	bl_label = "x anim"

	def draw(self, context):
		layout = self.layout

		layout.label(text="Copy Names:")

		# Display names of current active (or selected) Track, Strip, Clip as props that can be edited
		obj = context.object
		if obj and obj.type == 'ARMATURE' and obj.animation_data:

			# track
			active_track = get_active_nla_track(obj)
			if active_track:

				layout.prop(active_track, "name", text="Track")

				# strip
				active_strip = get_active_nla_strip(obj)
				if active_strip:

					row = layout.row()
					row.operator(X_ANIM_OT_copy_name_track_to_strip.bl_idname, text="↓")
					row.operator(X_ANIM_OT_copy_name_strip_to_track.bl_idname, text="↑")

					layout.prop(active_strip, "name", text="Strip")

					# clip
					active_clip = get_active_nla_clip(obj)
					if active_clip:

						row = layout.row()
						row.operator(X_ANIM_OT_copy_name_strip_to_clip.bl_idname, text="↓")
						row.operator(X_ANIM_OT_copy_name_clip_to_strip.bl_idname, text="↑")

						layout.prop(active_clip, "name", text="Clip")

#
# register
#

def register():
	bpy.types.Scene.x_anim_nla_utils = bpy.props.PointerProperty(type=x_anim_nla_utils_properties)
	bpy.types.NLA_MT_context_menu.prepend(draw_nla_utils_menu)
	bpy.types.NLA_MT_strips.prepend(draw_nla_utils_menu)
	

def unregister():
	del bpy.types.Scene.x_anim_nla_utils
	bpy.types.NLA_MT_context_menu.remove(draw_nla_utils_menu)
	bpy.types.NLA_MT_strips.remove(draw_nla_utils_menu)
	
