import bpy
from bpy.types import Context, Operator, Panel
from .. import ui_utils

class x_anim_eye_utils_properties(bpy.types.PropertyGroup):
    start_frame : bpy.props.IntProperty(name="start frame")
    end_frame : bpy.props.IntProperty(name="end frame")

class x_anim_OT_center_eye_lookat(Operator):
    bl_idname = "x_anim.center_eye_lookat"
    bl_label = "Center c_eye_lookat"
    bl_description = "Put c_eye_lookat at the center of c_eye.L and c_eye.R"

    #start_frame = bpy.props.IntProperty(name="start frame")
    #end_frame = bpy.props.IntProperty(name="end frame")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context: Context):

        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout

        props = bpy.context.scene.x_anim_eye_utils

        layout.prop(props, "start_frame")
        layout.prop(props, "end_frame")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
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

def register():
    bpy.types.Scene.x_anim_eye_utils = bpy.props.PointerProperty(type=x_anim_eye_utils_properties)

def unregister():
    del bpy.types.Scene.x_anim_eye_utils