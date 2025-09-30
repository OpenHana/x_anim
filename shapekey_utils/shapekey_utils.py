import bpy

from bpy.types import Operator
import re

# -------------------------------------------------------------------
#   Helper    
# -------------------------------------------------------------------

def reset_shapekey_to_empty(obj, shapekey_name):
    """将指定对象的指定形状键重置为空形状键."""
    if obj.data.shape_keys:
        basis_key = obj.data.shape_keys.reference_key if obj.data.shape_keys.reference_key else obj.data.shape_keys.key_blocks['Basis']
        shapekey = obj.data.shape_keys.key_blocks.get(shapekey_name)
        
        if shapekey and basis_key:
            basis_data = basis_key.data
            shapekey_data = shapekey.data
            for i in range(len(shapekey_data)):
                shapekey_data[i].co = basis_data[i].co
            print(f"Reset shapekey '{shapekey_name}' to empty")
        else:
            print(f"No shapekey named '{shapekey_name}' found or no basis shapekey found")
    else:
        print("Object does not have shape keys")

def reset_active_shapekey_to_empty():
    """将活动对象的活动形状键重置为空形状键."""

    active_obj = bpy.context.view_layer.objects.active

    if active_obj and active_obj.active_shape_key:
        shapekey_name = active_obj.active_shape_key.name
        reset_shapekey_to_empty(active_obj, shapekey_name)
    else:
        print("Active object or active shape key not found")

# -------------------------------------------------------------------
#   Operators    
# -------------------------------------------------------------------

class XCopySelectedShapeKeyOp(Operator):
    bl_idname = "xutil_shapekey_tools.copy_selected"
    bl_label = "Copy Selected"
    bl_description = "new name = name + _Copy"

    def execute(self, context):       
        copy_sk()

        self.report({'INFO'}, "Copied")     
        return {'FINISHED'}
    
class XApplyActiveShapeKeyToBasisOp(Operator):
    bl_idname = "xutil_shapekey_tools.apply_active_to_basis"
    bl_label = "Apply to Basis"
    bl_description = "Apply the current active shape key to Basis using blend_from_shape"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.data.shape_keys or not obj.active_shape_key:
            self.report({'WARNING'}, "No active shape key found")
            return {'CANCELLED'}

        active_sk = obj.active_shape_key
        if active_sk.name == 'Basis':
            self.report({'WARNING'}, "Active shape key is already Basis")
            return {'CANCELLED'}

        # Set Basis as active
        basis_index = obj.data.shape_keys.key_blocks.keys().index('Basis')
        obj.active_shape_key_index = basis_index

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.blend_from_shape(shape=active_sk.name, blend=1.0, add=True)
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, f"Applied '{active_sk.name}' to Basis")
        return {'FINISHED'}
    
def copy_sk() -> bool:

    # 0. get current shape key info

    obj = bpy.context.active_object
    this_sk = obj.active_shape_key
    this_obj_data : bpy.types.Mesh = obj.data
    shape_keys = this_obj_data.shape_keys.key_blocks

    # 1. determine new name

    new_name = this_sk.name + "_Copy"

    # 2. reset other side shape key, and set active

    other_sk = shape_keys.get(new_name)
    if other_sk:
        obj.shape_key_remove(other_sk)
    other_sk = obj.shape_key_add(name=new_name, from_mix=False)

    obj.active_shape_key_index = len(shape_keys) - 1

    # 3. make other side shape key == this shape key

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.blend_from_shape(shape=this_sk.name, blend=1.0, add=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    return True


class XEnableAllShapeKeysOp(Operator):
    bl_idname = "xutil_shapekey_tools.enable_all"
    bl_label = "Enable All"
    bl_description = "Enable all Shape Keys"

    def execute(self, context):       
        for shapekey in context.object.data.shape_keys.key_blocks:
            shapekey.mute = False

        self.report({'INFO'}, "All enabled")     
        return {'FINISHED'}

class XDisableAllShapeKeysOp(Operator):
    bl_idname = "xutil_shapekey_tools.disable_all"
    bl_label = "Disable All"
    bl_description = "Disable all Shape Keys"

    def execute(self, context):       
        for shapekey in context.object.data.shape_keys.key_blocks:
            shapekey.mute = True

        self.report({'INFO'}, "All Shape Keys disabled")        
        return {'FINISHED'}

def mirror_sk_name(shape_key_name: str) -> str:
    """
    Returns the mirrored shape key name by swapping left/right indicators.
    Handles indicators at any position, delimited by common separators.
    """
    # Patterns for left/right indicators and their replacements
    # Avoid variable-width look-behind by matching explicit patterns
    patterns = [
        # Lowercase single-letter with delimiters
        (r'([._-])l([._-]|$)', r'\1r\2'),      # "eye.l" -> "eye.r"
        (r'([._-])r([._-]|$)', r'\1l\2'),      # "eye.r" -> "eye.l"
        # Lowercase full word, no delimiter needed
        (r'left', 'right'),                    # "eyeleft" -> "eyeright", "eye-left" -> "eye-right"
        (r'right', 'left'),                    # "eyeright" -> "eyeleft", "eye-right" -> "eye-left"
        # Uppercase single-letter with delimiters
        (r'([._-])L([._-]|$)', r'\1R\2'),      # "eye.L" -> "eye.R"
        (r'([._-])R([._-]|$)', r'\1L\2'),      # "eye.R" -> "eye.L"
        # Uppercase full word, no delimiter needed
        (r'Left', 'Right'),                    # "eyeLeft" -> "eyeRight", "eye-Left" -> "eye-Right"
        (r'Right', 'Left'),                    # "eyeRight" -> "eyeLeft", "eye-Right" -> "eye-Left"
    ]

    for pattern, replacement in patterns:
        if re.search(pattern, shape_key_name):
            return re.sub(pattern, replacement, shape_key_name, count=1)

    # If no match, append _Mirror
    return shape_key_name + "_Mirror"

def mirror_sk(topo_mirror : bool) -> bool:

    obj = bpy.context.active_object

    # Save the current mode and active shape key index
    prev_mode = obj.mode
    prev_active_sk_index = obj.active_shape_key_index

    # 0. get current shape key info

    this_sk = obj.active_shape_key
    this_obj_data : bpy.types.Mesh = obj.data
    shape_keys = this_obj_data.shape_keys.key_blocks

    # 1. determine other side shape key name

    other_sk_name = mirror_sk_name(this_sk.name)

    if len(other_sk_name) == 0:
        return False

    # 2. reset other side shape key, and set active

    other_sk = shape_keys.get(other_sk_name)
    if other_sk:
        # Set the existing shape key as active
        obj.active_shape_key_index = shape_keys.keys().index(other_sk_name)
    else:
        # Create the shape key if it doesn't exist and set as active
        other_sk = obj.shape_key_add(name=other_sk_name, from_mix=False)
        obj.active_shape_key_index = len(shape_keys) - 1

    # 3. make other side shape key == this shape key

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.blend_from_shape(shape=this_sk.name, blend=1.0, add=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # 4. call mirror

    bpy.ops.object.shape_key_mirror(use_topology=topo_mirror)

    # Restore the previous mode if needed
    if obj.mode != prev_mode:
        bpy.ops.object.mode_set(mode=prev_mode)

    # Restore the original active shape key
    obj.active_shape_key_index = prev_active_sk_index

    return True

class XShapeKeyMirrorLeftRightOp(Operator):
    bl_idname = "xutil_shapekey_tools.mirror_left_right"
    bl_label = "Mirror Left/Right"
    bl_description = "Mirror the current shape key to the other side"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):       
        
        mirror_sk(topo_mirror=False)

        return {'FINISHED'}
    
class XShapeKeyMirrorLeftRightTopoOp(Operator):
    bl_idname = "xutil_shapekey_tools.mirror_left_right_topo"
    bl_label = "Mirror Left/Right (Topology)"
    bl_description = "Mirror the current shape key to the other side"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):       
        
        mirror_sk(topo_mirror=True)

        return {'FINISHED'}

def set_all_weight(weight : float):
    # 获取活跃的对象
    obj = bpy.context.active_object

    # 检查是否有选中的对象，并且该对象是网格对象
    if obj and obj.type == 'MESH':
    # 设置所有形状关键帧的权重
        for shape_key in obj.data.shape_keys.key_blocks:
            # 这里设置为你想要的权重值
            shape_key.value = weight
    else:
        print("请选中一个网格对象！")   

class XAllShapeKeysToZeroOp(Operator):
    bl_idname = "xutil_shapekey_tools.all_to_zero"
    bl_label = "all 0"
    bl_description = "set all weight to 0"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):       
        for shapekey in context.object.data.shape_keys.key_blocks:
            shapekey.value = 0

        return {'FINISHED'}

class XAllShapeKeysToOneOp(Operator):
    bl_idname = "xutil_shapekey_tools.all_to_one"
    bl_label = "all 1"
    bl_description = "set all weight to 1"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):       
        for shapekey in context.object.data.shape_keys.key_blocks:
            shapekey.value = 1

        return {'FINISHED'}

class XResetActiveShapeKeyToEmptyOp(Operator):
    bl_idname = "xutil_shapekey_tools.reset_active_to_empty"
    bl_label = "Reset to Empty"
    bl_description = "Reset the active shape key to empty"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        reset_active_shapekey_to_empty()
        self.report({'INFO'}, "Active shape key reset to empty")
        return {'FINISHED'}


# -------------------------------------------------------------------
#   UI    
# -------------------------------------------------------------------

def draw_ui(self, context):

    scn = context.scene
    layout = self.layout

    layout.separator()
    layout.use_property_decorate = False  # No animation.
    layout.use_property_split = False
    
    layout.separator()

    row = layout.row()
    row.label(text="x_anim shape key tools:")

    row = layout.row(align=True)
    row.operator(XCopySelectedShapeKeyOp.bl_idname)

    row = layout.row(align=True)
    row.operator(XApplyActiveShapeKeyToBasisOp.bl_idname)
    row.operator(XResetActiveShapeKeyToEmptyOp.bl_idname)

    row = layout.row(align=True)
    row.operator(XShapeKeyMirrorLeftRightOp.bl_idname, icon="MOD_MIRROR")
    row.operator(XShapeKeyMirrorLeftRightTopoOp.bl_idname, icon="MOD_MIRROR")

    row = layout.row(align=True)
    row.operator(XEnableAllShapeKeysOp.bl_idname, icon="RESTRICT_VIEW_OFF")
    row.operator(XDisableAllShapeKeysOp.bl_idname, icon="RESTRICT_VIEW_ON")

    row = layout.row(align=True)
    row.operator(XAllShapeKeysToZeroOp.bl_idname)
    row.operator(XAllShapeKeysToOneOp.bl_idname)

# -------------------------------------------------------------------
# register    
# -------------------------------------------------------------------

def register():
    bpy.types.DATA_PT_shape_keys.append(draw_ui)

def unregister():
    bpy.types.DATA_PT_shape_keys.remove(draw_ui)