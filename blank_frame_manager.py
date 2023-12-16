bl_info = {
    "name": "Blank Frame Manager",
    "blender": (2, 93, 0),
    "category": "Animation",
}

import bpy

class WM_OT_AddBlankFrame(bpy.types.Operator):
    bl_idname = "wm.add_blank_frame"
    bl_label = "Add Blank Frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the current frame
        current_frame = context.scene.frame_current

        # Calculate the offset for shifting keyframes
        offset = 1

        # Check if in Pose Mode
        if context.mode == 'POSE':
            # Loop through selected bones and shift keyframes by one frame
            for bone in context.selected_pose_bones:
                context.view_layer.objects.active = context.active_object
                context.active_object.data.bones.active = context.active_object.data.bones[bone.name]

                # Shift keyframes by one frame
                for fcurve in context.active_object.animation_data.action.fcurves:
                    for keyframe in fcurve.keyframe_points:
                        if keyframe.co.x >= current_frame:
                            keyframe.co.x += offset
        else:
            # Loop through selected objects and shift keyframes for the entire object by one frame
            for obj in context.selected_objects:
                if obj.animation_data is not None and obj.animation_data.action is not None:
                    context.view_layer.objects.active = obj
                    bpy.context.view_layer.objects.active = obj  # Set active object for the view layer
                    # Shift keyframes for all fcurves in the object's action
                    for fcurve in obj.animation_data.action.fcurves:
                        for keyframe in fcurve.keyframe_points:
                            if keyframe.co.x >= current_frame:
                                keyframe.co.x += offset

        # Set the current frame to the next frame
        context.scene.frame_set(current_frame + offset)
        return {'FINISHED'}

class WM_OT_RemoveBlankFrame(bpy.types.Operator):
    bl_idname = "wm.remove_blank_frame"
    bl_label = "Remove Blank Frame"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the current frame
        current_frame = context.scene.frame_current

        # Calculate the offset for shifting keyframes
        offset = 1

        # Check if in Pose Mode
        if context.mode == 'POSE':
            # Loop through selected bones and shift keyframes back by one frame
            for bone in context.selected_pose_bones:
                context.view_layer.objects.active = context.active_object
                context.active_object.data.bones.active = context.active_object.data.bones[bone.name]

                # Shift keyframes back by one frame
                for fcurve in context.active_object.animation_data.action.fcurves:
                    for keyframe in fcurve.keyframe_points:
                        if keyframe.co.x >= current_frame + offset:
                            keyframe.co.x -= offset
        else:
            # Loop through selected objects and shift keyframes back by one frame
            for obj in context.selected_objects:
                if obj.animation_data is not None and obj.animation_data.action is not None:
                    context.view_layer.objects.active = obj
                    bpy.context.view_layer.objects.active = obj  # Set active object for the view layer
                    # Shift keyframes back for all fcurves in the object's action
                    for fcurve in obj.animation_data.action.fcurves:
                        for keyframe in fcurve.keyframe_points:
                            if keyframe.co.x >= current_frame + offset:
                                keyframe.co.x -= offset

        # Remove the current frame (excluding the first frame)
        if current_frame > 1:
            context.scene.frame_set(current_frame - offset)
        return {'FINISHED'}

class WM_PT_BlankFrameManagerPanel(bpy.types.Panel):
    bl_label = "Blank Frame Manager"
    bl_idname = "PT_BlankFrameManagerPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.add_blank_frame")
        layout.operator("wm.remove_blank_frame")

addon_keymaps = []

def register():
    bpy.utils.register_class(WM_OT_AddBlankFrame)
    bpy.utils.register_class(WM_OT_RemoveBlankFrame)
    bpy.utils.register_class(WM_PT_BlankFrameManagerPanel)

    # Add hotkey
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='Object', space_type='EMPTY')
    kmi = km.keymap_items.new('wm.add_blank_frame', 'I', 'PRESS', shift=True)
    addon_keymaps.append((km, kmi))
    
    kmi = km.keymap_items.new('wm.remove_blank_frame', 'I', 'PRESS', shift=True, alt=True)
    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(WM_OT_AddBlankFrame)
    bpy.utils.unregister_class(WM_OT_RemoveBlankFrame)
    bpy.utils.unregister_class(WM_PT_BlankFrameManagerPanel)

    # Remove hotkey
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
