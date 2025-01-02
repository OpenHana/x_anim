import bpy

from bpy.types import Operator

# -------------------------------------------------------------------
#   Helper    
# -------------------------------------------------------------------

def mirror_active_vertex_group(use_topology_mirror : bool):

    # get active object & data

    obj = bpy.context.active_object

    vertex_groups = bpy.data.objects[obj.name].vertex_groups;

    active_vg_name = vertex_groups.active.name;

    # gen mirrored vg name

    mirrored_vg_name = active_vg_name + "_mirrored"

    if active_vg_name.endswith(".l"):
        mirrored_vg_name = active_vg_name[0: len(active_vg_name) - 1] + 'r'
    elif active_vg_name.endswith(".r"):
        mirrored_vg_name = active_vg_name[0: len(active_vg_name) - 1] + 'l'
    elif active_vg_name.endswith("_mirrored"):
        mirrored_vg_name = active_vg_name[0: len(active_vg_name) - len("_mirrored")]

    # special cases used internally by xuxing
    # "1" was added to quickly "disable" that vertex group if bound to a bone
    # so we still mirror them, and 
    if active_vg_name.endswith(".l1"): 
        mirrored_vg_name = active_vg_name[0: len(active_vg_name) - 2] + 'r1'
    elif active_vg_name.endswith(".r1"):
        mirrored_vg_name = active_vg_name[0: len(active_vg_name) - 2] + 'l1'

    # remove mirrored vg if present
    mirrored_vg_index = vertex_groups.find(mirrored_vg_name)
    if mirrored_vg_index > 0:
        vertex_groups.remove(vertex_groups[mirrored_vg_index])

    # copy active vg & mirror & rename

    bpy.ops.object.vertex_group_copy()
    bpy.ops.object.vertex_group_mirror(use_topology=use_topology_mirror)
        
    vertex_groups.active.name = mirrored_vg_name

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

# -------------------------------------------------------------------
# register    
# -------------------------------------------------------------------

def register():
    bpy.types.DATA_PT_vertex_groups.append(draw_ui)

def unregister():
    bpy.types.DATA_PT_vertex_groups.remove(draw_ui)