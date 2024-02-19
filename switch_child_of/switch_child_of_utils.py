from ..utils import *


def switch_child_of(self):

    for pb in bpy.context.selected_pose_bones:

        for c in pb.constraints: 
            if c.type != 'CHILD_OF':
                continue
            if c.name != self.target_child_of:            
                disable_child_of(pb, c)  

        for c in pb.constraints:
            if c.type != 'CHILD_OF':
                continue
            if c.name == self.target_child_of:
                enable_child_of(pb, c)


def disable_child_of(pb, c):
    mat_prev = pb.matrix.copy()

    if c.influence != 0.0:
        
        parent_type = 'bone' if c.subtarget else 'object'
        parent_name = c.subtarget if parent_type == 'bone' else c.target.name
        
        # set influence
        c.influence = 0.0
        
        # snap
        if parent_type == 'bone':         
            pb.matrix = mat_prev                
            
        elif parent_type == 'object':
            obj_par = get_object(parent_name)
            pb.matrix = c.inverse_matrix.inverted() @ obj_par.matrix_world.inverted() @ pb.matrix
            

        keyframe_pb_transforms(pb)
        c.keyframe_insert(data_path='influence')
            
        

def enable_child_of(pb, c):
    mat_prev = pb.matrix.copy()
    
    if c.influence != 1.0:

        parent_type = 'bone' if c.subtarget else 'object'
        parent_name = c.subtarget if parent_type == 'bone' else c.target.name            

        # set influence
        c.influence = 1.0
        
        # update_transform() 
        
        # snap
        if parent_type == 'bone':
            bone_parent = get_pose_bone(bpy.context.active_object, parent_name)
            pb.matrix = c.inverse_matrix.inverted() @ bone_parent.matrix.inverted() @ mat_prev
            
            # update_transform()
            
        elif parent_type == 'object':
            obj_par = get_object(parent_name)
            pb.matrix = c.inverse_matrix.inverted() @ obj_par.matrix_world.inverted() @ mat_prev
            
        
        keyframe_pb_transforms(pb)
        c.keyframe_insert(data_path='influence')



def keyframe_selected_pose_bones():
    for pb in bpy.context.selected_pose_bones:
        keyframe_pb_transforms(pb)
        for c in pb.constraints:
            if c.type == "CHILD_OF":
                c.keyframe_insert(data_path="influence")
    


def bake_switch_child_of(self):
    
    if self.only_at_keyframe:

        #prepass
        # frame_start & frame_start - 1
        bpy.context.scene.frame_set(self.frame_start)
        keyframe_selected_pose_bones()
        bpy.context.scene.frame_set(self.frame_start - 1)
        keyframe_selected_pose_bones()

        # frames in between
        prev_frame = self.frame_start - 1
        while bpy.context.scene.frame_current < self.frame_end:
            bpy.ops.screen.keyframe_jump(next=True)

            if prev_frame == bpy.context.scene.frame_current or bpy.context.scene.frame_current > self.frame_end:
                break
            prev_frame = bpy.context.scene.frame_current
            keyframe_selected_pose_bones()


        # frame_end & frame_end + 1
        bpy.context.scene.frame_set(self.frame_end)
        keyframe_selected_pose_bones()
        bpy.context.scene.frame_set(self.frame_end + 1)
        keyframe_selected_pose_bones()



        #switch pass
        bpy.context.scene.frame_set(self.frame_start - 1)
        prev_frame = self.frame_start - 1
        while bpy.context.scene.frame_current < self.frame_end:
            bpy.ops.screen.keyframe_jump(next=True)

            if prev_frame == bpy.context.scene.frame_current or bpy.context.scene.frame_current > self.frame_end:
                break

            prev_frame = bpy.context.scene.frame_current
            switch_child_of(self) 


    else:
        #prepass
        for i in range(self.frame_start - 1, self.frame_end + 2):
            bpy.context.scene.frame_set(i)

            keyframe_selected_pose_bones()

        #switch pass
        for i in range(self.frame_start, self.frame_end + 1):
            bpy.context.scene.frame_set(i)

            switch_child_of(self)