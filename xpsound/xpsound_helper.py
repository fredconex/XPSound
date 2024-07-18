import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import math
import mathutils

def create_arrow_coords(length, head_size):
    shaft_start = (0, 0, 0)
    shaft_end = (0, length, 0)
    head_start = shaft_end
    head_end_1 = (head_size * 0.5, length - head_size, 0)
    head_end_2 = (-head_size * 0.5, length - head_size, 0)
    return [shaft_start, shaft_end, head_start, head_end_1, head_start, head_end_2]

arrow_coords = create_arrow_coords(1, 0.25)

vertex_shader = '''
    uniform mat4 viewProjectionMatrix;
    uniform mat4 modelMatrix;
    
    in vec3 position;
    
    void main()
    {
        gl_Position = viewProjectionMatrix * modelMatrix * vec4(position, 1.0);
    }
'''

fragment_shader = '''
    uniform vec4 color;
    
    out vec4 fragColor;
    
    void main()
    {
        fragColor = color;
    }
'''

shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
batch_arrow = batch_for_shader(shader, 'LINES', {"position": arrow_coords})

def draw_callback_3d():
    if not hasattr(bpy.context.scene, "xp_sound_global") or not bpy.context.scene.xp_sound_global.draw_helper:
        return
    
    active_object = bpy.context.active_object
    if not active_object or active_object.type != 'EMPTY' or not hasattr(active_object, "xp_sound_data") or active_object.xp_sound_data.event_type != "SOUND":
        return

    gpu.state.depth_test_set('LESS_EQUAL')
    gpu.state.line_width_set(2.0)

    shader.bind()
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces[0]
            view_matrix = space.region_3d.view_matrix
            projection_matrix = space.region_3d.window_matrix
            viewProjectionMatrix = projection_matrix @ view_matrix
            shader.uniform_float("viewProjectionMatrix", viewProjectionMatrix)

            # Arrow color (pink for active object)
            color = (1.0, 0.0, 1.0, 1.0)
            shader.uniform_float("color", color)

            obj_matrix = active_object.matrix_world
            arrow_length = active_object.empty_display_size
            scale_matrix = mathutils.Matrix.Scale(arrow_length, 4)
            model_matrix = obj_matrix @ scale_matrix
            shader.uniform_float("modelMatrix", model_matrix)
            batch_arrow.draw(shader)

draw_handle = None

def register():
    global draw_handle
    draw_handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_3d, (), 'WINDOW', 'POST_VIEW')
    bpy.app.handlers.depsgraph_update_post.append(scene_update)

def unregister():
    global draw_handle
    bpy.types.SpaceView3D.draw_handler_remove(draw_handle, 'WINDOW')
    bpy.app.handlers.depsgraph_update_post.remove(scene_update)

def scene_update(dummy):
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()

if __name__ == "__main__":
    register()