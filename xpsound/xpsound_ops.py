import bpy
import os

######################################################################################
# SOUNDS
######################################################################################

# Operator to add a new sound
class XP_SOUND_OT_SOUND_ADD(bpy.types.Operator):
    bl_idname = "object.xp_sound_add"
    bl_label = "Add X-Plane Sound"

    def execute(self, context):
        obj = context.object
        xp_sound = obj.xp_sound_data.xp_sound_list.add()
        obj.xp_sound_data.xp_sound_index = len(obj.xp_sound_data.xp_sound_list) - 1
        return {'FINISHED'}

# Operator to remove a sound
class XP_SOUND_OT_SOUND_REMOVE(bpy.types.Operator):
    bl_idname = "object.xp_sound_remove"
    bl_label = "Remove X-Plane Sound"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        obj = context.object
        xp_sound_list = obj.xp_sound_data.xp_sound_list
        index = self.index
        xp_sound_list.remove(index)
        obj.xp_sound_data.xp_sound_index = min(max(0, index - 1), len(xp_sound_list) - 1)
        return {'FINISHED'}

# Operator to add a new sound event
class XP_SOUND_OT_SOUND_EVENT_ADD(bpy.types.Operator):
    "Defines an Operator to add a new sound event to the selected object's sound events list."
    bl_idname = "xpsound.add_sound_event"
    bl_label = "Add Sound Event"

    def execute(self, context):
        obj = context.active_object
        if obj.xp_sound_data.xp_sound_index >= 0:
            xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
            xp_sound.event_list.add()
            xp_sound.event_index = len(xp_sound.event_list) - 1
        return {"FINISHED"}        

# Operator to remove the selected sound event from the list
class XP_SOUND_OT_SOUND_EVENT_REMOVE(bpy.types.Operator):
    "Remove the selected sound event from the object's sound events list."
    bl_idname = "xpsound.remove_sound_event"
    bl_label = "Remove Sound Event"
    index: bpy.props.IntProperty()
    def execute(self, context):
        obj = context.active_object
        if obj.xp_sound_data.xp_sound_index >= 0:
            xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]        
            xp_sound.event_list.remove(self.index)
            xp_sound.event_index = 0
        return {"FINISHED"}

# Operator to copy the selected sound
class XP_SOUND_OT_SOUND_COPY(bpy.types.Operator):
    bl_idname = "object.xp_sound_copy"
    bl_label = "Copy Sound"
    
    def execute(self, context):
        obj = context.object
        xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
        copied_data = {
            'name': xp_sound.name,
            'guid': xp_sound.guid,
            'event_auto_end_from_start_cond': xp_sound.event_auto_end_from_start_cond,
            'event_polyphonic': xp_sound.event_polyphonic,
            'event_allowed_for_ai': xp_sound.event_allowed_for_ai,
            'event_param_idx': xp_sound.event_param_idx,
            'events': [(event.event_type, event.dataref_name, event.comparison_operator, event.comparison_value) for event in xp_sound.event_list]
        }
        context.window_manager.clipboard = str(copied_data)
        return {'FINISHED'}
    
# Operator to paste the selected sound
class XP_SOUND_OT_SOUND_PASTE(bpy.types.Operator):
    bl_idname = "object.xp_sound_paste"
    bl_label = "Paste Sound"
    
    def execute(self, context):
        obj = context.object
        xp_sound = obj.xp_sound_data.xp_sound_list.add()
        try:
            copied_data = eval(context.window_manager.clipboard)
            xp_sound.name = copied_data['name']
            xp_sound.guid = copied_data['guid']
            xp_sound.event_auto_end_from_start_cond = copied_data['event_auto_end_from_start_cond']
            xp_sound.event_polyphonic = copied_data['event_polyphonic']
            xp_sound.event_allowed_for_ai = copied_data['event_allowed_for_ai']
            xp_sound.event_param_idx = copied_data['event_param_idx']
            # Copy events
            for event_data in copied_data['events']:
                event = xp_sound.event_list.add()
                event.event_type, event.dataref_name, event.comparison_operator, event.comparison_value = event_data
        except Exception as e:
            self.report({'ERROR'}, f"Failed to paste sound: {e}")
        return {'FINISHED'}

# Operator to duplicate the selected sound
class XP_SOUND_OT_SOUND_DUPLICATE(bpy.types.Operator):
    bl_idname = "object.xp_sound_duplicate"
    bl_label = "Duplicate Sound"
    
    index: bpy.props.IntProperty()
     
    def execute(self, context):
        obj = context.object
        if self.index >= 0:
            xp_sound = obj.xp_sound_data.xp_sound_list[self.index]
            
            # Duplicate the sound
            new_xp_sound = obj.xp_sound_data.xp_sound_list.add()
            new_xp_sound.name = xp_sound.name
            new_xp_sound.guid = xp_sound.guid
            new_xp_sound.event_auto_end_from_start_cond = xp_sound.event_auto_end_from_start_cond
            new_xp_sound.event_polyphonic = xp_sound.event_polyphonic
            new_xp_sound.event_allowed_for_ai = xp_sound.event_allowed_for_ai
            new_xp_sound.event_param_idx = xp_sound.event_param_idx
            
            # Duplicate events
            for event in xp_sound.event_list:
                new_event = new_xp_sound.event_list.add()
                new_event.event_type = event.event_type
                new_event.dataref_name = event.dataref_name
                new_event.comparison_Operator = event.comparison_operator
                new_event.comparison_value = event.comparison_value
        return {'FINISHED'}


######################################################################################
# SNAPSHOTS
######################################################################################

# Operator to add a snapshot
class XP_SOUND_OT_SNAPSHOT_ADD(bpy.types.Operator):
    bl_idname = "object.xp_snapshot_add"
    bl_label = "Add X-Plane Snapshot"

    def execute(self, context):
        obj = context.object
        xp_sound = obj.xp_sound_data.xp_snapshot_list.add()
        obj.xp_sound_data.xp_snapshot_index = len(obj.xp_sound_data.xp_snapshot_list) - 1
        return {'FINISHED'}

# Operator to remove a snapshot
class XP_SOUND_OT_SNAPSHOT_REMOVE(bpy.types.Operator):
    bl_idname = "object.xp_snapshot_remove"
    bl_label = "Remove X-Plane Snapshot"
    
    index: bpy.props.IntProperty()
    
    def execute(self, context):
        obj = context.object
        xp_snapshot_list = obj.xp_sound_data.xp_snapshot_list
        index = self.index
        xp_snapshot_list.remove(index)
        obj.xp_sound_data.xp_snapshot_index = min(max(0, index - 1), len(xp_snapshot_list) - 1)
        return {'FINISHED'}    
    
# Operator to add a new snapshot event
class XP_SOUND_OT_SNAPSHOT_EVENT_ADD(bpy.types.Operator):
    "Defines an Operator to add a new snapshot event."
    bl_idname = "xpsound.add_snapshot_event"
    bl_label = "Add Snapshot Event"

    def execute(self, context):
        obj = context.active_object
        if obj.xp_sound_data.xp_snapshot_index >= 0:
            xp_snapshot = obj.xp_sound_data.xp_snapshot_list[obj.xp_sound_data.xp_snapshot_index]
            xp_snapshot.event_list.add()
            xp_snapshot.event_index = len(xp_snapshot.event_list) - 1
        return {"FINISHED"}        

# Operator to remove the selected sound event from the list
class XP_SOUND_OT_SNAPSHOT_EVENT_REMOVE(bpy.types.Operator):
    "Remove the selected snapshot event from the object's sound events list."
    bl_idname = "xpsound.remove_snapshot_event"
    bl_label = "Remove Snapshot Event"
    index: bpy.props.IntProperty()
    def execute(self, context):
        obj = context.active_object
        if obj.xp_sound_data.xp_snapshot_index >= 0:
            xp_snapshot = obj.xp_sound_data.xp_snapshot_list[obj.xp_sound_data.xp_snapshot_index]        
            xp_snapshot.event_list.remove(self.index)
            xp_snapshot.event_index = 0
        return {"FINISHED"}

# Refresh the list of events from GUIDs file    
class XP_SOUND_refresh_parsed_events(bpy.types.Operator):
    "Refreshes the list of parsed events from the GUIDS.txt file."
    bl_idname = "object.xp_sound_refresh_parsed_events"
    bl_label = "Refresh Parsed Events"

    def execute(self, context):
        obj = context.active_object

        # Construct the path to the GUIDS.txt file
        guids_file_path = bpy.path.abspath(os.path.join("//", context.scene.xp_sound_global.fmod_path, "GUIDS.txt"))
        guids_file_path = os.path.normpath(guids_file_path)

        # Clear the existing parsed events
        context.scene.xp_sound_global.parsed_events.clear()
        context.scene.xp_sound_global.parsed_snapshots.clear()

        if os.path.exists(guids_file_path):
            # Parse the GUIDS.txt file and add the events to the collection
            with open(guids_file_path, "r") as file:
                for line in file:
                    line = line.strip()
                    parts = line.split()
                    if len(parts) > 1:
                        guid = parts[0]
                        name = " ".join(parts[1:])
                        if "event:" in name:
                            event_name = name[name.index("event:") + len("event:") :]
                            new_event = context.scene.xp_sound_global.parsed_events.add()
                            new_event.name = event_name
                        if "snapshot:" in name:
                            event_name = name[
                                name.index("snapshot:") + len("snapshot:") :
                            ]
                            new_event = context.scene.xp_sound_global.parsed_snapshots.add()
                            new_event.name = event_name
            self.report({'INFO'}, f"Updated from GUIDS: {guids_file_path}")
            
        else:
            self.report({'WARNING'}, f"GUIDS file is missing at: {guids_file_path}")

        return {"FINISHED"}

# Register all classes and define global properties
classes = (
    XP_SOUND_OT_SOUND_ADD,
    XP_SOUND_OT_SOUND_REMOVE,
    XP_SOUND_OT_SOUND_EVENT_ADD,
    XP_SOUND_OT_SOUND_EVENT_REMOVE,
    XP_SOUND_OT_SOUND_COPY,
    XP_SOUND_OT_SOUND_PASTE,
    XP_SOUND_OT_SOUND_DUPLICATE,

    XP_SOUND_OT_SNAPSHOT_ADD,
    XP_SOUND_OT_SNAPSHOT_REMOVE,
    XP_SOUND_OT_SNAPSHOT_EVENT_ADD,
    XP_SOUND_OT_SNAPSHOT_EVENT_REMOVE,

    XP_SOUND_refresh_parsed_events
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
           
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
