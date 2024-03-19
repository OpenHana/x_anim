import bpy
import mathutils
from bpy.types import Context, Operator, Panel
from .. import ui_utils, utils
from typing import Callable

#
# util functions
#

def eye_ctrls_insert_keyframe(cur_frame):
    bones = bpy.context.active_object.pose.bones
    bones['c_eye.L'].keyframe_insert('location',frame=cur_frame)
    bones['c_eye.R'].keyframe_insert('location',frame=cur_frame)
    bones['c_eye_lookat'].keyframe_insert('location',frame=cur_frame)

def eye_ctrls_bake(start_frame, end_frame, progress : Callable[[int, int], None]):

    total_frames = int(end_frame - start_frame + 1)

    for i in range(total_frames):
        cur_frame = i + start_frame
        bpy.context.scene.frame_set(cur_frame) # is this really needed?
        eye_ctrls_insert_keyframe(cur_frame)

        if callable(progress):
            progress(i, total_frames)

def bones_insert_keyframe(bone_names : list, cur_frame):

    bones = bpy.context.active_object.pose.bones

    for bone_name in bone_names:
        bones[bone_name].keyframe_insert('location', frame=cur_frame)

def bones_bake(bone_names : list, start_frame, end_frame, progress : Callable[[int, int], None]):
    
    total_frames = int(end_frame - start_frame + 1)

    for i in range(total_frames):
        cur_frame = i + start_frame
        bpy.context.scene.frame_set(cur_frame) # is this really needed?
        bones_insert_keyframe(bone_names, cur_frame)

        if callable(progress):
            progress(i, total_frames)

#
# operators
#

##       
## center eye lookat
##
class x_anim_eye_utils_properties(bpy.types.PropertyGroup):
    start_frame : bpy.props.IntProperty(name="start frame")
    end_frame : bpy.props.IntProperty(name="end frame")

class x_anim_OT_center_eye_lookat(Operator):
    bl_idname = "x_anim.center_eye_lookat"
    bl_label = "Center c_eye_lookat"
    bl_description = "Put c_eye_lookat at the center of c_eye.L and c_eye.R, when using FaceIt mocap, only c_eye.L/R will move, which is a little inconvinient"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context: Context):
        
        props = bpy.context.scene.x_anim_eye_utils
        start_frame = props.start_frame
        end_frame = props.end_frame
        total_frames = int(end_frame - start_frame + 1)

        bones = bpy.context.view_layer.objects.active.pose.bones

        ui_utils.progress_begin()

        # bake the curve to ensure that the evaluated values of subsequent frames 
        # are not affected by inserting new frames
        # add 1 keyframe before start and after end to protect the curve outside the given frame range
        eye_ctrls_bake(start_frame - 1, end_frame + 1, ui_utils.progress_update)

        for i in range(total_frames):

            cur_frame = i + start_frame
            bpy.context.scene.frame_set(cur_frame)

            center = (bones['c_eye.L'].location + bones['c_eye.R'].location) / 2.0

            bones['c_eye.L'].location = bones['c_eye.L'].location - center
            bones['c_eye.R'].location = bones['c_eye.R'].location - center
            bones['c_eye_lookat'].location = center

            eye_ctrls_insert_keyframe(cur_frame)

            ui_utils.progress_update(i, total_frames)

        ui_utils.progress_end()

        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

        props = bpy.context.scene.x_anim_eye_utils

        row = layout.row()

        row.prop(props, "start_frame")
        row.prop(props, "end_frame")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    

##
## eye_ctrl to eye_target
##
   
class x_anim_OT_eye_ctrl_to_eye_target(Operator):
    bl_idname = "x_anim.eye_ctrl_to_eye_target"
    bl_label = "eye_ctrl to eye_target"
    bl_description = "snap eye_target to the result of eye_ctrl"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context: Context):

        props = bpy.context.scene.x_anim_eye_utils
        start_frame = props.start_frame
        end_frame = props.end_frame
        total_frames = int(end_frame - start_frame + 1)

        bones = bpy.context.view_layer.objects.active.pose.bones

        ui_utils.progress_begin()

        # bake the curve to ensure that the evaluated values of subsequent frames 
        # are not affected by inserting new frames
        # add 1 keyframe before start and after end to protect the curve outside the given frame range
        bones_bake(["c_x_eye_target.x", "c_x_eye_target.l", "c_x_eye_target.r"], start_frame - 1, end_frame + 1, ui_utils.progress_update)

        for i in range(total_frames):

            cur_frame = i + start_frame
            bpy.context.scene.frame_set(cur_frame)

            central_location = utils.get_world_position_of_pose_bone(bones["x_actual_eye_target"])
            left_location = utils.get_world_position_of_pose_bone_tail(bones["x_actual_line_of_sight.l"])
            right_location = utils.get_world_position_of_pose_bone_tail(bones["x_actual_line_of_sight.r"])

            utils.set_bone_position(bones["c_x_eye_target.x"], central_location, world_space=True, key=True)
            utils.set_bone_position(bones["c_x_eye_target.l"], left_location, world_space=True, key=True)
            utils.set_bone_position(bones["c_x_eye_target.r"], right_location, world_space=True, key=True)

            ui_utils.progress_update(i, total_frames)

        ui_utils.progress_end()

        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

        props = bpy.context.scene.x_anim_eye_utils

        row = layout.row()

        row.prop(props, "start_frame")
        row.prop(props, "end_frame")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

#
# panel
#


class x_anim_PT_eye_utils(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "x anim"
    bl_label = "Eye Utils"

    def draw(self, context):
        layout = self.layout
        props = bpy.context.scene.x_anim

        row = layout.row()
        ui_utils.default_operator_button(row, x_anim_OT_center_eye_lookat)
        row = layout.row()
        ui_utils.default_operator_button(row, x_anim_OT_eye_ctrl_to_eye_target)

#
# register
#

def register():
    bpy.types.Scene.x_anim_eye_utils = bpy.props.PointerProperty(type=x_anim_eye_utils_properties)

def unregister():
    del bpy.types.Scene.x_anim_eye_utils