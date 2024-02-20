def default_operator_button(layout, operator_class):
    layout.operator(operator_class.bl_idname, text=operator_class.bl_label)
    return