import bpy
from bpy.types import Context, Operator, Panel
from .. import ui_utils

class x_anim_OT_synced_mocap_connect(Operator):
    bl_idname = "x_anim.synced_mocap_connect"
    bl_label = "Synced Mocap Connect"
    bl_description = "Activate multiple mocap systems at once, (FaceIt, VMC4B)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.ops.vmc4b.connect.poll()

    def execute(self, context: Context):

        bpy.ops.vmc4b.connect()

        return {'FINISHED'}
    
class x_anim_OT_synced_mocap_disconnect(Operator):
    bl_idname = "x_anim.synced_mocap_disconnect"
    bl_label = "Synced Mocap Disconnect"
    bl_description = "disconnect multiple mocap systems at once, (FaceIt, VMC4B)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.ops.vmc4b.disconnect.poll()

    def execute(self, context: Context):
        
        bpy.ops.vmc4b.disconnect()

        return {'FINISHED'}

class x_anim_OT_synced_mocap_start(Operator):
    bl_idname = "x_anim.synced_mocap_start"
    bl_label = "Synced Mocap Start"
    bl_description = "Activate multiple mocap systems at once, (FaceIt, VMC4B)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.ops.vmc4b.startrecording.poll()

    def execute(self, context: Context):
        
        bpy.ops.faceit.receiver_start()

        bpy.ops.vmc4b.startrecording()

        return {'FINISHED'}
    
class x_anim_OT_synced_mocap_stop(Operator):
    bl_idname = "x_anim.synced_mocap_stop"
    bl_label = "Synced Mocap Stop"
    bl_description = "Stop multiple mocap systems at once, (FaceIt, VMC4B)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.ops.vmc4b.stoprecording.poll()

    def execute(self, context: Context):
        
        bpy.ops.faceit.receiver_stop()

        bpy.ops.vmc4b.stoprecording()

        return {'FINISHED'}

class x_anim_PT_mocap_utils(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "x anim"
    bl_label = "Mocap Utils"

    def draw(self, context):
        layout = self.layout
        props = bpy.context.scene.x_anim

        row = layout.row()
        ui_utils.default_operator_button(row, x_anim_OT_synced_mocap_connect)
        ui_utils.default_operator_button(row, x_anim_OT_synced_mocap_disconnect)
        
        row = layout.row()
        ui_utils.default_operator_button(row, x_anim_OT_synced_mocap_start)
        ui_utils.default_operator_button(row, x_anim_OT_synced_mocap_stop)