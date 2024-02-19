import bpy
from bpy.types import Panel


class x_anim_PT_switch_child_of(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "x anim"
    bl_label = "Switch Child Of"


    def draw(self, context):
        layout = self.layout
        props = bpy.context.scene.x_anim

        row = layout.row()
        row.label(text="Child Of Utils",icon="CON_CHILDOF")
        
        row = layout.row()
        row.operator("x_anim.switch_child_of", text="Switch Child Of")