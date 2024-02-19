import bpy
from bpy.types import Context, Operator, Panel

class x_anim_OT_synced_mocap(Operator):
    bl_idname = "x_anim.synced_mocap"
    bl_label = "Synced Mocap"
    bl_description = "Activate multiple mocap systems at once, (FaceIt, VMC4B)"

    def execute(self, context: Context):
        
        bpy.ops.faceit.receiver_start()

        bpy.ops.vmc4b.connect()
        bpy.ops.vmc4b.startrecording()

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
        row.operator(x_anim_OT_synced_mocap.bl_idname, text=x_anim_OT_synced_mocap.bl_label)