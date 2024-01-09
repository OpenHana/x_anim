import bpy

#type polls
def armature_poll(self, object):
    return object.type == 'ARMATURE'
    
def text_poll(self, object):
    return object.type == 'FONT'

#properties
class x_anim_properties(bpy.types.PropertyGroup):

    ...