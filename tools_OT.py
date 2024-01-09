from .utils import *
from .tools_sub import *
from bpy.types import Operator


class x_anim_OT_switch_child_of(Operator):
    bl_idname = "x_anim.switch_child_of"
    bl_label = "Switch Child Of"
    bl_description = "Switch Child Of"
    bl_options = {'UNDO'}

    constraint_items = []
    def get_constraint_items(self, context):
        return x_anim_OT_switch_child_of.constraint_items    

    target_child_of: bpy.props.EnumProperty(items=get_constraint_items, default=None)
    bake_type: bpy.props.EnumProperty(items=(('STATIC', 'Static', 'Switch and snap only for the current frame'), ('ANIM', 'Anim', 'Switch and snap over a specified frame range')), default='STATIC')
    frame_start: bpy.props.IntProperty(default=0)
    frame_end: bpy.props.IntProperty(default=10)
    only_at_keyframe: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return (context.active_object != None and context.mode == 'POSE')    

    def invoke(self, context, event):
        x_anim_OT_switch_child_of.constraint_items = []       
        active_bone = None
        try:
            active_bone = bpy.context.active_pose_bone
        except:
            pass
            
        if active_bone == None:
            self.report({'ERROR'}, "A bone must be selected")
            return {'FINISHED'}            
        
        active_constraint = None
        
        # collect current ChildOf constraints
        if len(active_bone.constraints):
            # get active one first
            for c in active_bone.constraints:
                if c.type == 'CHILD_OF':
                    if c.influence > 0:
                        active_constraint = c
                        separator = ''
                        if c.subtarget != '':
                            separator = ': '
                        #show not common alert
                        not_common_string = '  [not common]'
                        in_all_pb = True
                        for pb in bpy.context.selected_pose_bones:
                            in_this_pb = False
                            for c0 in pb.constraints:
                                if c0.type == 'CHILD_OF' and c0.target == c.target and c0.subtarget == c.subtarget:
                                    in_this_pb = True
                            in_all_pb = in_all_pb and in_this_pb
                        if in_all_pb: 
                            not_common_string = ''
                        x_anim_OT_switch_child_of.constraint_items.append((c.name, c.target.name + separator + c.subtarget + not_common_string, ''))
        
            # others
            for c in active_bone.constraints:
                if c.type == 'CHILD_OF':
                    if c != active_constraint or active_constraint == None:
                        separator = ''
                        if c.subtarget != '':
                            separator = ': '
                        #show not common alert
                        not_common_string = '  [not common]'
                        in_all_pb = True
                        for pb in bpy.context.selected_pose_bones:
                            in_this_pb = False
                            for c0 in pb.constraints:
                                if c0.type == 'CHILD_OF' and c0.target == c.target and c0.subtarget == c.subtarget:
                                    in_this_pb = True
                            in_all_pb = in_all_pb and in_this_pb
                        if in_all_pb: 
                            not_common_string = ''
                        x_anim_OT_switch_child_of.constraint_items.append((c.name, c.target.name + separator + c.subtarget + not_common_string, ''))
                  
        x_anim_OT_switch_child_of.constraint_items.append(('NONE', 'None', 'None'))
        
        if active_constraint != None:
            self.target_child_of = active_constraint.name
    
        if len(x_anim_OT_switch_child_of.constraint_items) == 1:
            self.report({'ERROR'}, "No ChildOf constraint found on active bone")
            return {'FINISHED'}
        
        # set frame start and end
        if context.active_object.animation_data.action:
            action = context.active_object.animation_data.action
            self.frame_start, self.frame_end = int(action.frame_range[0]), int(action.frame_range[1])   

        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)


    def draw(self, context):
        layout = self.layout
        layout.label(text='Active Parent:           '+self.constraint_items[0][1])
        layout.prop(self, 'target_child_of', text='Snap To')
        
        layout.prop(self, 'bake_type', expand=True)
        
        if self.bake_type == 'ANIM':
            row = layout.row(align=True)
            row.prop(self, 'frame_start', text='Frame Start')
            row.prop(self, 'frame_end', text='Frame End')
            row = layout.row()    
            row.prop(self, 'only_at_keyframe', text='Only at Keyframe')



    def execute(self, context):
        if self.bake_type == 'STATIC':
            child_of_utils.switch_child_of(self)
        elif self.bake_type == 'ANIM':
            child_of_utils.bake_switch_child_of(self)
        return {'FINISHED'}