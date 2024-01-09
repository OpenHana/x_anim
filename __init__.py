bl_info = {
    "name": "x_anim",
    "author": "NID",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "View3D > Sidebar",
    "description": "",
    "warning": "",
    "category": "Animation"
}



import importlib

# When bpy is already in local, we know this is not the initial import...
if "bpy" in locals():
    submodules = (properties, utils,
    tools_OT, tools_PT,
    #tools_sub
    child_of_utils,
    )
    # ...so we need to reload our submodule(s) using importlib
    for sub in submodules:
        importlib.reload(sub)


import bpy

from .properties import *
from .utils import *
from .tools_OT import *
from .tools_PT import *



classes = (x_anim_properties, 
           x_anim_PT_utilities,
           x_anim_OT_switch_child_of,
           )


def register():
    for c in classes:
        if not hasattr(bpy.types, c.__name__):
            bpy.utils.register_class(c)
            if hasattr(c, "register_handlers") and callable(c.register_handlers):
                c.register_handlers()

    bpy.types.Scene.x_anim = bpy.props.PointerProperty(type=x_anim_properties)
    print("registered")


def unregister():
    for c in classes:
        if hasattr(bpy.types, c.__name__):
            bpy.utils.unregister_class(c)
            if hasattr(c, "unregister_handlers") and callable(c.unregister_handlers):
                c.unregister_handlers()
            
    if hasattr(bpy.types.Scene, "x_anim"):
        del bpy.types.Scene.x_anim
    print("unregistered")


if __name__ == "__main__":
    register()
