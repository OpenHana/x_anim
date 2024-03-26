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
    
    
#
# panel
#


class X_ANIM_PT_nla_utils(Panel):
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

#
# register
#

def register():
    bpy.types.Scene.x_anim_nla_utils = bpy.props.PointerProperty(type=x_anim_nla_utils_properties)

def unregister():
    del bpy.types.Scene.x_anim_nla_utils