import bpy
from bpy.types import Context, Operator, Panel

def default_operator_button(layout, operator_class):
    layout.operator(operator_class.bl_idname, text=operator_class.bl_label)
    return

def progress_begin():
    bpy.context.window_manager.progress_begin(0, 100)

def progress_update(i:int, total:int):
    bpy.context.window_manager.progress_update(float(i) / float(total) * 100)

def progress_end():
    bpy.context.window_manager.progress_end()
