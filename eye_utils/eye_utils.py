import bpy
import mathutils
from bpy.types import Context, Operator, Panel
from .. import ui_utils, utils
from typing import Callable

#
# util functions
#

def eye_ctrls_insert_keyframe(cur_frame):
    bones_insert_keyframe(['c_eye.L', 'c_eye.R', 'c_eye_lookat'], cur_frame)

def eye_ctrls_bake(start_frame, end_frame, progress : ui_utils.ProgressCallback = None):
    bones_bake(['c_eye.L', 'c_eye.R', 'c_eye_lookat'], start_frame, end_frame, progress)

def bones_insert_keyframe(bone_names : list, cur_frame):

    bones = bpy.context.active_object.pose.bones

    for bone_name in bone_names:
        bones[bone_name].keyframe_insert('location', frame=cur_frame, group=bone_name)

def bones_bake(bone_names : list, start_frame, end_frame, progress : ui_utils.ProgressCallback = None):
    
    total_frames = int(end_frame - start_frame + 1)

    for i in range(total_frames):
        cur_frame = i + start_frame
        #bpy.context.scene.frame_set(cur_frame)
        utils.set_frame_fast(cur_frame)
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

class X_ANIM_OT_center_eye_lookat(Operator):
    bl_idname = "x_anim.center_eye_lookat"
    bl_label = "Center c_eye_lookat"
    bl_description = "Put c_eye_lookat at the center of c_eye.L and c_eye.R, when using FaceIt mocap, only c_eye.L/R will move, which is a little inconvinient"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context: Context):
        
        props = bpy.context.scene.x_anim_eye_utils
        start_frame = props.start_frame
        end_frame = props.end_frame
        total_frames = int(end_frame - start_frame + 1)

        bones = bpy.context.view_layer.objects.active.pose.bones

        ui_utils.default_progress_begin()

        # bake the curve to ensure that the evaluated values of subsequent frames 
        # are not affected by inserting new frames
        # add 1 keyframe before start and after end to protect the curve outside the given frame range
        eye_ctrls_bake(start_frame - 1, end_frame + 1, ui_utils.default_progress_update)

        for i in range(total_frames):

            cur_frame = i + start_frame
            #bpy.context.scene.frame_set(cur_frame)
            utils.set_frame_fast(cur_frame)

            center = (bones['c_eye.L'].location + bones['c_eye.R'].location) / 2.0

            bones['c_eye.L'].location = bones['c_eye.L'].location - center
            bones['c_eye.R'].location = bones['c_eye.R'].location - center
            bones['c_eye_lookat'].location = center

            eye_ctrls_insert_keyframe(cur_frame)

            ui_utils.default_progress_update(i, total_frames)

        ui_utils.default_progress_end()

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
   
class X_ANIM_OT_final_line_of_sight_to_eye_target(Operator):
    bl_idname = "x_anim.final_line_of_sight_to_eye_target"
    bl_label = "Final Line Of Sight → Eye Target"
    bl_description = "snap eye_target to the Final Line Of Sight"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context: Context):

        props = bpy.context.scene.x_anim_eye_utils
        start_frame = props.start_frame
        end_frame = props.end_frame
        total_frames = int(end_frame - start_frame + 1)

        bones = bpy.context.view_layer.objects.active.pose.bones

        ui_utils.default_progress_begin()

        # First loop: Collect locations
        frame_data = []
        for i in range(total_frames):
            cur_frame = i + start_frame
            utils.set_frame_fast(cur_frame)

            left_location = utils.get_world_position_of_pose_bone_tail(bones["x_final_line_of_sight.l"])
            right_location = utils.get_world_position_of_pose_bone_tail(bones["x_final_line_of_sight.r"])

            central_location = (left_location + right_location) * 0.5
            # Store data as a tuple
            frame_data.append((cur_frame, left_location, right_location, central_location))

            ui_utils.default_progress_update(i, total_frames)

        # Second loop: Set locations based on collected data
        for i, (cur_frame, left_location, right_location, central_location) in enumerate(frame_data):
            
            utils.set_frame_fast(cur_frame)

            utils.set_bone_position(bones["c_x_eye_target.x"], central_location, world_space=True, key=True)
            utils.set_bone_position(bones["c_x_eye_target.l"], left_location, world_space=True, key=True)
            utils.set_bone_position(bones["c_x_eye_target.r"], right_location, world_space=True, key=True)

            ui_utils.default_progress_update(i, total_frames)

        ui_utils.default_progress_end()

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
## Eye convergence
##
    
class X_ANIM_OT_eye_distance_to_convergence(Operator):
    bl_idname = "x_anim.eye_distance_to_convergence"
    bl_label = "Eye Distance → Convergence"
    bl_description = "Convert distance of c_eye.L/R to convergence value"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context: Context):

        props = bpy.context.scene.x_anim_eye_utils
        start_frame = props.start_frame
        end_frame = props.end_frame
        total_frames = int(end_frame - start_frame + 1)

        bones = bpy.context.view_layer.objects.active.pose.bones

        ui_utils.default_progress_begin()

        # bake the curve to ensure that the evaluated values of subsequent frames 
        # are not affected by inserting new frames
        # add 1 keyframe before start and after end to protect the curve outside the given frame range
        bones_bake(['c_eye.L', 'c_eye.R', 'c_eye_convergence_slider'], start_frame - 1, end_frame + 1, ui_utils.default_progress_update)

        for i in range(total_frames):

            cur_frame = i + start_frame
            #bpy.context.scene.frame_set(cur_frame)
            utils.set_frame_fast(cur_frame)

            convergence = (-bones['c_eye.L'].location.x + bones['c_eye.R'].location.x) / 10.0 # 10 = 5 * 2, 5 is the most each c_eye can move

            bones['c_eye_convergence_slider'].location.y = convergence * 4.0
            bones['c_eye.L'].location.x = 0
            bones['c_eye.R'].location.x = 0

            bones_insert_keyframe(['c_eye.L', 'c_eye.R', 'c_eye_convergence_slider'], cur_frame)

            ui_utils.default_progress_update(i, total_frames)

        ui_utils.default_progress_end()

        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

        props = bpy.context.scene.x_anim_eye_utils

        row = layout.row()

        row.prop(props, "start_frame")
        row.prop(props, "end_frame")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

class X_ANIM_OT_eye_target_distance_to_convergence(Operator):
    bl_idname = "x_anim.eye_target_distance_to_convergence"
    bl_label = "Eye Target Distance → Convergence"
    bl_description = "Convert distance of c_x_eye_target.L/R to convergence value"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context: Context):

        props = bpy.context.scene.x_anim_eye_utils
        start_frame = props.start_frame
        end_frame = props.end_frame
        total_frames = int(end_frame - start_frame + 1)

        bones = bpy.context.view_layer.objects.active.pose.bones

        ui_utils.default_progress_begin()

        # bake the curve to ensure that the evaluated values of subsequent frames 
        # are not affected by inserting new frames
        # add 1 keyframe before start and after end to protect the curve outside the given frame range
        bones_bake(['c_x_eye_target.l', 'c_x_eye_target.r', 'c_eye_target_convergence_slider'], start_frame - 1, end_frame + 1, ui_utils.default_progress_update)

        for i in range(total_frames):

            cur_frame = i + start_frame
            #bpy.context.scene.frame_set(cur_frame)
            utils.set_frame_fast(cur_frame)

            convergence = (-bones['c_x_eye_target.l'].location.x + bones['c_x_eye_target.r'].location.x) / 6.4 # 6.4 = 3.2 * 2, 3.2 is the most each c_x_eye_target can move

            bones['c_eye_target_convergence_slider'].location.y = convergence * 4.0
            bones['c_x_eye_target.l'].location.x = 0
            bones['c_x_eye_target.r'].location.x = 0

            bones_insert_keyframe(['c_x_eye_target.l', 'c_x_eye_target.r', 'c_eye_target_convergence_slider'], cur_frame)

            ui_utils.default_progress_update(i, total_frames)

        ui_utils.default_progress_end()

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

        row.label(text="Faster if only the face rig enabled in scene")

        row = layout.row()
        ui_utils.default_operator_button(row, X_ANIM_OT_center_eye_lookat)
        row = layout.row()
        ui_utils.default_operator_button(row, X_ANIM_OT_final_line_of_sight_to_eye_target)
        row = layout.row()
        ui_utils.default_operator_button(row, X_ANIM_OT_eye_distance_to_convergence)
        row = layout.row()
        ui_utils.default_operator_button(row, X_ANIM_OT_eye_target_distance_to_convergence)

#
# register
#

def register():
    bpy.types.Scene.x_anim_eye_utils = bpy.props.PointerProperty(type=x_anim_eye_utils_properties)

def unregister():
    del bpy.types.Scene.x_anim_eye_utils