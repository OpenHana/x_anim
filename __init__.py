bl_info = {
    "name": "x_anim",
    "author": "NID",
    "blender": (4, 0, 0),
    "version": (0, 0, 1),
    "location": "View3D > Sidebar",
    "description": "animation utils",
    "warning": "",
    "category": "Animation"
}

import bpy
from . import auto_load
from . import properties

auto_load.init()

def register():
    auto_load.register()

    bpy.types.Scene.x_anim = bpy.props.PointerProperty(type=properties.x_anim_properties)

def unregister():
    auto_load.unregister()

    del bpy.types.Scene.x_anim

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
