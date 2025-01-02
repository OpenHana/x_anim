import bpy
from bpy.types import Context, Operator, Panel
from typing import Callable

def default_operator_button(layout, operator_class):
    layout.operator(operator_class.bl_idname, text=operator_class.bl_label)
    return


ProgressCallback = Callable[[int, int], None]
'''
A callback function for progress updates.
The first parameter is the current task index.
The second parameter is the total number of tasks.

pass in progress_update when you see param of this type
'''

def default_progress_begin():
    bpy.context.window_manager.progress_begin(0, 100)

def default_progress_update(i:int, total:int):
    bpy.context.window_manager.progress_update(float(i) / float(total) * 100)

def default_progress_end():
    bpy.context.window_manager.progress_end()
