#copy & paste these codes into Blender Text Editor then click run

"""
import bpy
import os
import sys
import importlib


#set the path the project is located in to system path
project_path = "E:\OneDrive\Project\Python"
sys.path.insert(0, project_path)


import x_anim


#unregister the old one before reload
x_anim.unregister()


importlib.reload(x_anim)
print("reloaded")


#register the new one
x_anim.register()
"""