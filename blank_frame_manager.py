# copyright "MIT"
# @jiapeilu 2023

bl_info = {
    "name": "Blank Frame Manager",
    "blender": (4, 0, 0),
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
                context.active_object.data.bones.active = context.active_object.data.bones[bone.name]
                context.view_layer.objects.active = context.active_object

                # Shift keyframes by one frame
                self.move_keyframes(context.active_object,current_frame,offset)
                
        else:
            # Loop through selected objects and shift keyframes for the entire object by one frame
            for obj in context.selected_objects:
                if obj.animation_data is not None and obj.animation_data.action is not None:
                    # Set active object for the view layer
                    context.view_layer.objects.active = obj  
                    # Shift keyframes for all fcurves in the object's action
                    self.move_keyframes(obj,current_frame,offset)
                        
        # Set the current frame to the next frame
        context.scene.frame_set(current_frame + offset)
        return {'FINISHED'}
    
    def move_keyframes(self,obj,current_frame,offset):
        for fcurve in obj.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                if keyframe.co.x >= current_frame:
                    keyframe.co.x += offset
                    keyframe.handle_left.x += offset
                    keyframe.handle_right.x += offset        

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
                self.move_keyframes(context.active_object,current_frame,offset)

        else:
            # Loop through selected objects and shift keyframes back by one frame
            for obj in context.selected_objects:
                if obj.animation_data is not None and obj.animation_data.action is not None:
                    # Set active object for the view layer
                    context.view_layer.objects.active = obj  
                    # Shift keyframes back for all fcurves in the object's action
                    self.move_keyframes(obj,current_frame,offset)

        return {'FINISHED'}
    
    def move_keyframes(self,obj,current_frame,offset):
        for fcurve in obj.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                if keyframe.co.x >= current_frame + offset:
                    keyframe.co.x -= offset
                    keyframe.handle_left.x -= offset
                    keyframe.handle_right.x -= offset 


class WM_OT_KeyingUnlocked(bpy.types.Operator):
    bl_idname = "wm.keying_unlocked"
    bl_label = "Key Unlocked"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Check if we are in Pose Mode
        if bpy.context.mode == 'POSE':
            # Assume 'armature' is the armature object
            armature = bpy.context.active_object
            # Iterate through selected bones
            for bone in bpy.context.selected_pose_bones:
                # Access the pose bone
                pose_bone = armature.pose.bones.get(bone.name)
                # Add non-locked attributes to the keying set
                self.add_non_locked_attributes_to_keying_set(pose_bone)
        else:
            for obj in bpy.context.selected_objects:
                self.add_non_locked_attributes_to_keying_set(obj)
        return {'FINISHED'}
    
    # Function to add non-locked attributes to a keying set
    def add_non_locked_attributes_to_keying_set(self, bone):
        #axis
        X =0
        Y =1
        Z =2
        axis = [X,Y,Z]

        nonLock=[]
        #Location
        for index_axis in axis:
            if not bone.lock_location[index_axis]:
                nonLock.append(['location',index_axis])
                
        #Rotation
        if bone.rotation_mode == "QUATERNION":
            for index_axis in axis:
                if not bone.lock_rotation[index_axis]:
                    nonLock.append(['rotation_quaternion',index_axis+1])
            if not bone.lock_rotation_w:
                    nonLock.append(['rotation_quaternion',0])
                    
        elif bone.rotation_mode == "AXIS_ANGLE":
            for index_axis in axis:
                if not bone.lock_rotation[index_axis]:
                    nonLock.append(['rotation_axis_angle',index_axis+1])
            if not bone.lock_rotation_w:
                    nonLock.append(['rotation_axis_angle',0])
                    
        else:
            for index_axis in axis:
                if not bone.lock_rotation[index_axis]:
                    nonLock.append(['rotation_euler',index_axis])
        #Scale
        for index_axis in axis:
            if not bone.lock_scale[index_axis]:
                nonLock.append(['scale',index_axis])

        if nonLock:
            # Set the current frame
            current_frame = bpy.context.scene.frame_current

            for path in nonLock:
            # Insert a keyframe for 'location.x' at the current frame
                bone.keyframe_insert(data_path=path[0], index=path[1], frame=current_frame)



class WM_PT_BlankFrameManagerPanel(bpy.types.Panel):
    bl_label = "Blank Frame Manager"
    bl_idname = "PT_BlankFrameManagerPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FrameTools'

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.add_blank_frame")
        layout.operator("wm.remove_blank_frame")
        layout.operator("wm.keying_unlocked")

def register():
    bpy.utils.register_class(WM_OT_AddBlankFrame)
    bpy.utils.register_class(WM_OT_RemoveBlankFrame)
    bpy.utils.register_class(WM_OT_KeyingUnlocked)
    bpy.utils.register_class(WM_PT_BlankFrameManagerPanel)


def unregister():
    bpy.utils.unregister_class(WM_OT_AddBlankFrame)
    bpy.utils.unregister_class(WM_OT_RemoveBlankFrame)
    bpy.utils.unregister_class(WM_OT_KeyingUnlocked)
    bpy.utils.unregister_class(WM_PT_BlankFrameManagerPanel)


if __name__ == "__main__":
    register()
