import bpy
import os

# Sound List
class XP_SOUND_UL_SOUND_LIST(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "name", text="", emboss=False, icon="SPEAKER")
        
        # Button to duplicate the sound
        button_duplicate = row.operator("object.xp_sound_duplicate", text="", icon="DUPLICATE")
        button_duplicate.index = index        

        # Button to remove the sound
        button_remove = row.operator("object.xp_sound_remove", text="", icon="TRASH")
        button_remove.index = index

# Snapshot List
class XP_SOUND_UL_SNAPSHOT_LIST(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "name", text="", emboss=False, icon="SPEAKER")

        # Button to remove the sound
        button_remove = row.operator("object.xp_snapshot_remove", text="", icon="TRASH")
        button_remove.index = index        

# Panel on Tools
class XP_SOUND_PT_TOOLS_PANEL(bpy.types.Panel):
    bl_label = "Global Settings"
    bl_idname = "VIEW3D_PT_xp_sound_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XPSound"
    
    def draw(self, context):
        layout = self.layout.box()
        scene = context.scene
        
        # Global properties
        col = layout.column()
        col.operator("xpsound.export_snd", text="Export to .snd", icon="EXPORT")
        col.operator("xpsound.import_snd", text="Import from .snd", icon="IMPORT")
        col.label(text="General:")
        col.prop(scene.xp_sound_global, "snd_filename", text="SND Filename")
        
        # Custom drawing for FMOD path
        guids_file_path = bpy.path.abspath(os.path.join("//", context.scene.xp_sound_global.fmod_path, "GUIDS.txt"))
        guids_file_path = os.path.normpath(guids_file_path)
        guid_file_exists = os.path.isfile(guids_file_path)
        
        # Check if GUIDS.txt exists
        row = col.row()
        if not guid_file_exists:
            split = row.split(factor=0.5)
        else:
            split = row
        
        fmod_col = split.column()
        if not guid_file_exists:
            fmod_col.alert = True
        fmod_col.prop(scene.xp_sound_global, "fmod_path", text="FMOD directory")
        
        if not guid_file_exists:
            warning_col = split.column()
            warning_col.label(text="GUIDs.txt not found!", icon='ERROR')
        
        col.prop(scene.xp_sound_global, "ref_point_y")
        col.prop(scene.xp_sound_global, "ref_point_z")
        col.prop(scene.xp_sound_global, "disable_legacy_alerts")
        col.prop(scene.xp_sound_global, "draw_helper")
        
# Empty panel
class XP_SOUND_PT_PANEL(bpy.types.Panel):
    bl_label = "XPSound Settings"
    bl_idname = "OBJECT_PT_xp_sound_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == "EMPTY")
        
    def draw(self, context):
        layout = self.layout
        obj = context.object
        xp_data = obj.xp_sound_data
        
        # Object-specific properties
        layout.prop(xp_data, "event_type")
        
        if xp_data.event_type == 'SOUND':
            self.draw_sound_properties(context, layout, obj)
        elif xp_data.event_type == 'SNAPSHOT':
            self.draw_snapshot_properties(context, layout, obj)
        elif xp_data.event_type == 'SPACE':
            self.draw_space_properties(layout, xp_data)

    def draw_space_properties(self, col, obj):
        col = col.column()
        col.prop(obj, "space_index")
        col.prop(obj, "space_blend_depth")
        
    def draw_sound_properties(self, context, layout, obj):
        # Create a list with each X-Plane sound object
        row = layout.column()
        row.template_list("XP_SOUND_UL_SOUND_LIST", "", obj.xp_sound_data, "xp_sound_list", obj.xp_sound_data, "xp_sound_index")

        # Add/Remove/Duplicate buttons
        row = layout.row().split(factor=0.7)
        row.operator("object.xp_sound_add", text="Add Sound")
        
        # Copy/Paste buttons
        #row = layout.row()
        row = row.split(factor=0.5)
        row.operator("object.xp_sound_copy", text="Copy")
        row.operator("object.xp_sound_paste", text="Paste")

        # Display the event_name property for the selected X-Plane sound object
        if (obj.xp_sound_data.xp_sound_index >= 0 and len(obj.xp_sound_data.xp_sound_list) > 0):
            xp_sound = obj.xp_sound_data.xp_sound_list[obj.xp_sound_data.xp_sound_index]
            layout = layout.box()

            #layout.prop(xp_sound, "guid")
            row = layout.row()
            row.prop_search(xp_sound, "guid", context.scene.xp_sound_global, "parsed_events", text="Event GUID", icon="COLLAPSEMENU")    
            row.operator("object.xp_sound_refresh_parsed_events", text="", icon="FILE_REFRESH")        
            
            col = layout.column()
            col.prop(xp_sound, "event_auto_end_from_start_cond")
            col.prop(xp_sound, "event_polyphonic")
            col.prop(xp_sound, "event_allowed_for_ai")
            col.prop(xp_sound, "event_param_idx")            
            
            # Create tabs for each sound event
            if len(xp_sound.event_list) > 0:
                events = layout.box()
                row = events.row()
                row.label(text="Type") 
                row = row.split(factor=0.5)
                row.label(text="Dataref") 
                row = row.split(factor=0.3)
                row.label(text="Condition") 
                row = row.split(factor=0.8)
                row.label(text="Value") 
            # Draw Events
                for index, event in enumerate(xp_sound.event_list):
                    row = events.row()
                    row.prop(event, "event_type", text="")    
                    row = row.split(factor=0.5)
                    row.prop(event, "dataref_name", text="")      
                    row = row.split(factor=0.3)
                    row.prop(event, "comparison_operator", text="")  
                    row = row.split(factor=0.8)
                    row.prop(event, "comparison_value", text="")
                    remove_button = row.operator("xpsound.remove_sound_event", text="", icon="TRASH")
                    remove_button.index = index
                    
            row = layout.row()
            row.operator("xpsound.add_sound_event", text="Add Event")  
            
    def draw_snapshot_properties(self, context, layout, obj):
        # Create a list with each X-Plane sound object
        row = layout.column()
        row.template_list("XP_SOUND_UL_SNAPSHOT_LIST", "", obj.xp_sound_data, "xp_snapshot_list", obj.xp_sound_data, "xp_snapshot_index")  

        row = layout.row()
        row.operator("object.xp_snapshot_add", text="Add Snapshot")                    

        if (obj.xp_sound_data.xp_snapshot_index >= 0 and len(obj.xp_sound_data.xp_snapshot_list) > 0):
            xp_snapshot = obj.xp_sound_data.xp_snapshot_list[obj.xp_sound_data.xp_snapshot_index]        

            layout = layout.box()
            row = layout.row()
            row.prop_search(xp_snapshot, "guid", context.scene.xp_sound_global, "parsed_snapshots", text="Event GUID", icon="COLLAPSEMENU")    
            row.operator("object.xp_sound_refresh_parsed_events", text="", icon="FILE_REFRESH")              
            
            col = layout.column()
            col.prop(xp_snapshot, "event_auto_end_from_start_cond")
            col.prop(xp_snapshot, "event_param_idx")            
            
            # Create tabs for each sound event
            if len(xp_snapshot.event_list) > 0:
                events = layout.box()
                row = events.row()
                row.label(text="Type") 
                row = row.split(factor=0.5)
                row.label(text="Dataref") 
                row = row.split(factor=0.3)
                row.label(text="Condition") 
                row = row.split(factor=0.8)
                row.label(text="Value") 
                # Draw Events
                for index, event in enumerate(xp_snapshot.event_list):
                    row = events.row()
                    row.prop(event, "event_type", text="")    
                    row = row.split(factor=0.5)
                    row.prop(event, "dataref_name", text="")      
                    row = row.split(factor=0.3)
                    row.prop(event, "comparison_operator", text="")  
                    row = row.split(factor=0.8)
                    row.prop(event, "comparison_value", text="")
                    remove_button = row.operator("xpsound.remove_snapshot_event", text="", icon="TRASH")
                    remove_button.index = index

            row = layout.row()
            row.operator("xpsound.add_snapshot_event", text="Add Event")  

            
def register():
    bpy.utils.register_class(XP_SOUND_PT_TOOLS_PANEL)
    bpy.utils.register_class(XP_SOUND_PT_PANEL)
    bpy.utils.register_class(XP_SOUND_UL_SOUND_LIST)
    bpy.utils.register_class(XP_SOUND_UL_SNAPSHOT_LIST)

def unregister():
    bpy.utils.unregister_class(XP_SOUND_PT_TOOLS_PANEL)
    bpy.utils.unregister_class(XP_SOUND_PT_PANEL)
    bpy.utils.unregister_class(XP_SOUND_UL_SOUND_LIST)    
    bpy.utils.unregister_class(XP_SOUND_UL_SNAPSHOT_LIST)


if __name__ == "__main__":
    register()
