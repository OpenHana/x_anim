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

from . import auto_load

auto_load.init()

def register():
    auto_load.register()


def unregister():
    auto_load.unregister()

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
