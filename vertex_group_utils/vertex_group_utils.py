import bpy
from ..ui_utils import *
from bpy.types import Operator


# -------------------------------------------------------------------
#   Helper    
# -------------------------------------------------------------------
def mirror_vertex_group(obj, vertex_group_name : str, use_topology_mirror: bool):

    # Set active vertex group to vertex_group_name
    vertex_group_index = obj.vertex_groups.find(vertex_group_name)

    if vertex_group_index == -1:
        print(f"Error: Vertex group '{vertex_group_name}' not found in object '{obj.name}'")
        return
    
    obj.vertex_groups.active_index = vertex_group_index

    # gen mirrored vg name
    mirrored_vg_name = vertex_group_name + "_mirrored"

    if vertex_group_name.endswith(".l"):
        mirrored_vg_name = vertex_group_name[0: len(vertex_group_name) - 1] + 'r'
    elif vertex_group_name.endswith(".r"):
        mirrored_vg_name = vertex_group_name[0: len(vertex_group_name) - 1] + 'l'
    elif vertex_group_name.endswith("_mirrored"):
        mirrored_vg_name = vertex_group_name[0: len(vertex_group_name) - len("_mirrored")]

    # special cases used internally by xuxing
    if vertex_group_name.endswith(".l1"): 
        mirrored_vg_name = vertex_group_name[0: len(vertex_group_name) - 2] + 'r1'
    elif vertex_group_name.endswith(".r1"):
        mirrored_vg_name = vertex_group_name[0: len(vertex_group_name) - 2] + 'l1'

    # remove mirrored vg if present
    mirrored_vg_index = obj.vertex_groups.find(mirrored_vg_name)
    if mirrored_vg_index > 0:
        obj.vertex_groups.remove(obj.vertex_groups[mirrored_vg_index])

    # copy active vg & mirror & rename
    bpy.ops.object.vertex_group_copy()
    bpy.ops.object.vertex_group_mirror(use_topology=use_topology_mirror)
        
    obj.vertex_groups.active.name = mirrored_vg_name

def mirror_active_vertex_group(use_topology_mirror: bool):
    obj = bpy.context.active_object
    vertex_groups = bpy.data.objects[obj.name].vertex_groups
    active_vg_name = vertex_groups.active.name
    mirror_vertex_group(obj, active_vg_name, use_topology_mirror)

def mirror_all_vertex_groups(use_topology_mirror: bool, left_to_right: bool, progess_callback : ProgressCallback = None):
    obj = bpy.context.active_object
    vertex_groups = bpy.data.objects[obj.name].vertex_groups
    vg_names = [vg.name for vg in vertex_groups]

    total_vgs = len(vg_names)
    for i, vg_name in enumerate(vg_names):
        if left_to_right:
            if vg_name.endswith(".l") or vg_name.endswith(".l1"):
                mirror_vertex_group(obj, vg_name, use_topology_mirror)
        else:
            if vg_name.endswith(".r") or vg_name.endswith(".r1"):
                mirror_vertex_group(obj, vg_name, use_topology_mirror)

        if progess_callback:
            progess_callback(i, total_vgs)

def sort_vertex_groups_alphabetically():
    obj = bpy.context.active_object
    vertex_groups = obj.vertex_groups
    sorted_vgs = sorted(vertex_groups, key=lambda vg: vg.name)

    for target_index, vg in enumerate(sorted_vgs):
        current_index = vertex_groups.find(vg.name)
        while current_index > target_index:
            bpy.ops.object.vertex_group_move(direction='UP')
            current_index -= 1
        while current_index < target_index:
            bpy.ops.object.vertex_group_move(direction='DOWN')
            current_index += 1

# -------------------------------------------------------------------
#   Operators    
# -------------------------------------------------------------------

class XMirrorActiveVertexGroupOp(Operator):
    bl_idname = "object.x_mirror_active_vertex_group"
    bl_label = "Mirror Active Vertex Group"
    bl_options = {'REGISTER', 'UNDO'}

    use_topology_mirror: bpy.props.BoolProperty(
        name="Use Topology Mirror",
        description="Use topology based mirroring",
        default=True
    )

    def execute(self, context):
        mirror_active_vertex_group(self.use_topology_mirror)
        return {'FINISHED'}

class XMirrorAllVertexGroupsOp(Operator):
    bl_idname = "object.x_mirror_all_vertex_groups"
    bl_label = "Mirror All Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}

    use_topology_mirror: bpy.props.BoolProperty(
        name="Use Topology Mirror",
        description="Use topology based mirroring",
        default=True
    )

    left_to_right: bpy.props.BoolProperty(
        name="Left to Right",
        description="Mirror from left to right",
        default=True
    )

    def execute(self, context):

        default_progress_begin()

        mirror_all_vertex_groups(self.use_topology_mirror, self.left_to_right, default_progress_update)

        default_progress_end()

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "use_topology_mirror")
        layout.prop(self, "left_to_right")

class XSortVertexGroupsAlphabeticallyOp(Operator):
    bl_idname = "object.x_sort_vertex_groups_alphabetically"
    bl_label = "Sort Vertex Groups Alphabetically"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sort_vertex_groups_alphabetically()
        return {'FINISHED'}

# -------------------------------------------------------------------
#   UI    
# -------------------------------------------------------------------

def draw_ui(self, context):

    layout = self.layout
    
    layout.separator()

    row = layout.row()
    row.label(text="x_anim vertex group tools:")

    row = layout.row(align=True)
    row.operator(XMirrorActiveVertexGroupOp.bl_idname, text="Mirror", icon="MOD_MIRROR").use_topology_mirror = False
    row.operator(XMirrorActiveVertexGroupOp.bl_idname, text="Mirror(Topology)", icon="MOD_MIRROR").use_topology_mirror = True

    row = layout.row(align=True)

    op = row.operator(XMirrorAllVertexGroupsOp.bl_idname, text="Mirror All L → R", icon="MOD_MIRROR")
    op.use_topology_mirror = False
    op.left_to_right = True

    op = row.operator(XMirrorAllVertexGroupsOp.bl_idname, text="Mirror All L → R(Topology)", icon="MOD_MIRROR")
    op.use_topology_mirror = True
    op.left_to_right = True

    row = layout.row(align=True)

    op = row.operator(XMirrorAllVertexGroupsOp.bl_idname, text="Mirror All R → L", icon="MOD_MIRROR")
    op.use_topology_mirror = False
    op.left_to_right = False

    op = row.operator(XMirrorAllVertexGroupsOp.bl_idname, text="Mirror All R → L(Topology)", icon="MOD_MIRROR")
    op.use_topology_mirror = True
    op.left_to_right = False

    layout.separator()

    row = layout.row()
    row.operator(XSortVertexGroupsAlphabeticallyOp.bl_idname, text="Sort Alphabetically (SLOW!)", icon="SORTALPHA")

# -------------------------------------------------------------------
# register    
# -------------------------------------------------------------------

def register():
    bpy.types.DATA_PT_vertex_groups.append(draw_ui)

def unregister():
    bpy.types.DATA_PT_vertex_groups.remove(draw_ui)