import bpy
import gpu
import bmesh
import mathutils
from mathutils import *
from bpy.types import Panel, PropertyGroup, AddonPreferences
from bpy.props import FloatVectorProperty, PointerProperty, BoolProperty
from gpu_extras.batch import batch_for_shader
from bpy_extras.view3d_utils import location_3d_to_region_2d

bl_info = {
    "name": "Vertex Project",
    "author": "Kuklach",
    "version": (0, 4, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Kuklach Tools",
    "description": "Simple addon to fast project edges or vertices on a plane defined by cursor location and normal.",
    "category": "Tools"
}


class VertexProjectionProperties(PropertyGroup):
    """Properties for vertex projection tool"""

    plane_normal: FloatVectorProperty(
        name="Plane Normal",
        description="Normal vector of the projection plane",
        default=(0.0, 1.0, 0.0),
        min=-1.0,
        max=1.0,
        subtype='XYZ'
    )

    vertex_normal: FloatVectorProperty(
        name="Vertex Normal",
        description="Alternative normal vector for vertex projection",
        default=(0.0, 1.0, 0.0),
        min=-1.0,
        max=1.0,
        subtype='XYZ'
    )

    auto_set_cursor: BoolProperty(
        name="Auto Set Cursor",
        description="Automatically set the cursor position on the projection plane",
        default=True
    )

    use_vertices_only: BoolProperty(
        name="Use Vertices Only",
        description="Project vertices instead of edges",
        default=False
    )

    use_vertex_normal: BoolProperty(
        name="Use Vertex Normal",
        description="Use the alternative normal for vertex projection",
        default=False
    )
    use_outside_edges: BoolProperty(
        name="Use Outside Edges",
        description="Use edges outside of projection plane",
        default=True
    )

class BASE_PANEL:
    bl_category = "Kuklach Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    #bl_options = {"DEFAULT_CLOSED"}


class VertexProjectionPanel(BASE_PANEL, Panel):
    bl_idname = "ProjectPanel"
    bl_label = "Vertex Projection"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        tool_props = bpy.context.scene.vertex_projection_props

        box = layout.box()
        
        box.label(text="Set Plane Normal", icon='OUTLINER_OB_EMPTY')
        row = box.row(align=True)# Add icon for the header
        row.operator("wm.set_normal", text="X", icon='AXIS_SIDE').normal = 'X'  # Add icon for the button
        row.operator("wm.set_normal", text="Y", icon='AXIS_FRONT').normal = 'Y'
        row.operator("wm.set_normal", text="Z", icon='AXIS_TOP').normal = 'Z'
        row = box.row()
        row.prop(tool_props, "plane_normal", text="")
        #box.label(text="Set Normal from Selection", icon='OUTLINER_OB_EMPTY')
        row = box.row(align=True)
        row.operator("wm.set_normal_sel", text="Left", icon='AXIS_SIDE').normal = 'X'
        row.operator("wm.set_normal_sel", text="Front", icon='AXIS_FRONT').normal = 'Y'
        row.operator("wm.set_normal_sel", text="Up", icon='AXIS_TOP').normal = 'Z'

        box = layout.box()
        box.label(text="Project Vertices")
        row = box.row(align=True)
        row.operator("wm.execute_projection", text='Positive', icon='ADD').is_positive = True
        row.operator("wm.execute_projection", text='Negative', icon='REMOVE').is_positive = False       
        row = box.row(align=True)
        row.operator("wm.execute_projection", text='Closest', icon='FULLSCREEN_EXIT').is_closest = True         
        
        box = layout.box()
        box.prop(tool_props, "auto_set_cursor", text="Auto Set Cursor", icon='CURSOR')  # Add icon for the property
        box.prop(tool_props, "use_outside_edges", text="Use Outside Edges", icon='EDGESEL')
        box.prop(tool_props, "use_vertices_only", text="Use Vertices Only", icon='VERTEXSEL')
        #box = layout.box()
        #box.label(text="Project Closest Vertices")

        box = layout.box()
        box.label(text="Toggle Visual Helpers")
        box.operator("wm.show_debug", text='Show Helpers', icon='HIDE_OFF')


class VertexProjectionOptionsPanel(BASE_PANEL, Panel):
    bl_parent_id = "ProjectPanel"
    bl_label = "Vertex Projection Options"
    bl_order = 1
    bl_options = {'DEFAULT_CLOSED'}
    # def draw_header(self, _):
    #      layout = self.layout
    #      layout.label(text="", icon='NORMALS_FACE')  # Add icon for the header
    def draw(self, context):
        layout = self.layout
        tool_props = bpy.context.scene.vertex_projection_props

        layout.prop(tool_props, "use_vertex_normal", text="Use Vertex Normal", icon='NORMALS_VERTEX')
        layout.label(text="Vertex Normal")
        layout.prop(tool_props, "vertex_normal", text="")
        #layout.label(text="You can find settings for this addon in preferences")


class VisualDebugOptionsPanel(AddonPreferences):
    bl_idname = __name__

    icon_thickness: bpy.props.FloatProperty(
        name="Icon Thickness",
        description="Thickness of the '+' and '-' icons",
        default=2.5,
        min=0.1,
        max=10.0
    )

    plane_color: bpy.props.FloatVectorProperty(
        name="Plane Color",
        description="Color of the projection plane",
        subtype='COLOR',
        default=(0.25, 0.25, 0.25, 0.15),
        min=0.0,
        max=1.0,
        size=4
    )

    plane_scale: bpy.props.FloatProperty(
        name="Plane Scale",
        description="Scale of the projection plane",
        default=7,
        min=0.0,
        max=1000.0,
    )

    icon_scale: bpy.props.FloatProperty(
        name="Icon Scale",
        description="Scale of the '+' and '-' icons",
        default=0.45,
        min=0.0,
        max=100.0,
    )

    icon_distance: bpy.props.FloatProperty(
        name="Icon Distance",
        description="Distance of the icons from the projection plane",
        default=0.9,
        min=0.0,
        max=100.0
    )

    icon_alpha: bpy.props.FloatProperty(
        name="Icon Alpha",
        description="Transparency of the '+' and '-' icons",
        default=0.9,
        min=0.0,
        max=1.0
    )
    
    line_thickness: bpy.props.FloatProperty(
        name="Icon Thickness",
        description="Thickness of the vertex lines",
        default=1.5,
        min=0.1,
        max=10.0
    )

    line_color: bpy.props.FloatVectorProperty(
        name="Plane Color",
        description="Color of the vertex lines",
        subtype='COLOR',
        default=(1, 0, 0, 1),
        min=0.0,
        max=1.0,
        size=4
    )

    blend: bpy.props.EnumProperty(
        name="Shader Blend",
        description="Alpha Blend Channels",
        items=[
            ('ALPHA_PREMULT', "ALPHA_PREMULT", "The original color channels are interpolated according to the alpha value with the new colors pre-multiplied by this value"),
            ('ADDITIVE_PREMULT', "ADDITIVE_PREMULT ", "(Can give cool effect with black color, low alpha and big plane scale) The original color channels are added by the corresponding ones that are pre-multiplied by the alpha value"),
            ('MULTIPLY', "MULTIPLY", "The original color channels are multiplied by the corresponding ones"),
            ('SUBTRACT', "SUBTRACT", "The original color channels are subtracted by the corresponding ones"),
            ('INVERT', "INVERT", "The original color channels are replaced by its complementary color"),
        ],
        default='ALPHA_PREMULT'
    )

    def draw(self, context):
        layout = self.layout
        tool_props = context.preferences.addons[__name__].preferences
        
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Plane Alpha Blend:")
        row.prop(tool_props, "blend", text="")
        row = box.row(align=True)
        row.prop(tool_props, "plane_color", text="Plane Color")
        row = box.row(align=True) 
        row.label(text="Plane Scale")
        row.prop(tool_props, "plane_scale", text="")
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Icon Scale")
        row.prop(tool_props, "icon_scale", text="")
        row = box.row(align=True)
        row.label(text="Icon Thickness")
        row.prop(tool_props, "icon_thickness", text="")
        row = box.row(align=True)
        row.label(text="Icon Distance")
        row.prop(tool_props, "icon_distance", text="")
        row = box.row(align=True)
        row.label(text="Icon Alpha")
        row.prop(tool_props, "icon_alpha", text="")
        box = layout.box()
        row = box.row(align=True)
        row.label(text="Vertex Lines Thickness")
        row.prop(tool_props, "line_thickness", text="")
        row = box.row(align=True)
        row.label(text="Vertex Lines Color")
        row.prop(tool_props, "line_color", text="")


class SetNormal(bpy.types.Operator):
    """Set the plane normal to a specific axis"""
    bl_idname = "wm.set_normal"
    bl_label = "Set Normal"
    #bl_options = {'REGISTER', 'UNDO'}

    normal: bpy.props.EnumProperty(
        name="Axis",
        description="Axis to set the normal to",
        items=[
            ('X', "X", "Set the normal to the X-axis"),
            ('Y', "Y", "Set the normal to the Y-axis"),
            ('Z', "Z", "Set the normal to the Z-axis"),
        ],
        default='Z'
    )

    #@classmethod
    #def poll(cls, context):
    #    return context.active_object is not None and bpy.context.active_object.type == 'MESH'

    def execute(self, context):
        if self.normal == 'X':
            bpy.context.scene.vertex_projection_props.plane_normal = (1, 0, 0)
        elif self.normal == 'Y':
            bpy.context.scene.vertex_projection_props.plane_normal = (0, 1, 0)
        else:
            bpy.context.scene.vertex_projection_props.plane_normal = (0, 0, 1)
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}


class SetNormalSel(bpy.types.Operator):
    """Calculate normal matrix from selected vertices"""
    bl_idname = "wm.set_normal_sel"
    bl_label = "Set Normal from Selection"
    bl_options = {'REGISTER', 'UNDO'}

    normal: bpy.props.EnumProperty(
        name="Axis",
        description="Axis to set the normal from selected vertices",
        items=[
            ('X', "Left", "Set the plane normal from selected vertices to the left"),
            ('Y', "Front", "Set the plane normal from selected vertices to the front"),
            ('Z', "Up", "Set the plane normal from selected vertices to the up"),
        ],
        default='Z'
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object is not None and bpy.context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = bpy.context.active_object
        mesh = obj.data
        selected_verts = [v for v in mesh.vertices if v.select]

        if len(selected_verts) < 2:
            self.report({'WARNING'}, "Please select at least 2 vertices")
            return {'CANCELLED'}

        v1 = selected_verts[0].co
        v2 = selected_verts[1].co
        a = v2 - v1

        if len(selected_verts) > 2:
            v3 = selected_verts[2].co
            v = (v1 + v2 + v3) / 3
        else:
            plane_no = bpy.context.scene.vertex_projection_props.plane_normal
            r3d = bpy.context.area.spaces.active.region_3d
            view_matrix = r3d.view_matrix
            x, y, z = view_matrix.to_3x3()
            point = r3d.view_matrix.inverted().translation
            v = (v1 + v2) / 2
            v3 = mathutils.geometry.intersect_line_plane(
                point, point + -z * 2, a, z, False)

        b = v3 - v1
        c = a.cross(b)

        if c.magnitude > 0:
            c = c.normalized()
        else:
            self.report({'WARNING'}, "Selected vertices are colinear")
            return {'CANCELLED'}

        b2 = c.cross(a).normalized()
        a2 = a.normalized()
        m = Matrix([a2, b2, c]).transposed().inverted()

        if bpy.context.scene.vertex_projection_props.auto_set_cursor:
            context.scene.cursor.location = obj.matrix_world @ v

        if self.normal == 'X':
            bpy.context.scene.vertex_projection_props.plane_normal = m[0].xyz.normalized()
        elif self.normal == 'Y':
            bpy.context.scene.vertex_projection_props.plane_normal = m[1].xyz.normalized()
        else:
            bpy.context.scene.vertex_projection_props.plane_normal = m[2].xyz.normalized()
        bpy.ops.object.mode_set(mode='EDIT')
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        return {'FINISHED'}


class ExecuteProjection(bpy.types.Operator):
    """Project vertices from the positive/negative side of the plane or closest vertices to it"""
    bl_idname = "wm.execute_projection"
    bl_label = "Project Vertices"
    bl_options = {'REGISTER', 'UNDO'}

    is_positive: bpy.props.BoolProperty(
        name="Positive Side",
        description="Project vertices on the positive side of the plane",
        default=True
    )
    
    is_closest: bpy.props.BoolProperty(
        name="Is Closest",
        description="Project closest vertices to the plane",
        default=False
    )

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object is not None and bpy.context.active_object.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.normal_update()

        mat = obj.matrix_world
        plane_no = bpy.context.scene.vertex_projection_props.plane_normal
        plane_co = context.scene.cursor.location
        bm.verts.ensure_lookup_table()

        if context.scene.vertex_projection_props.use_vertices_only:
            selected_verts = [v for v in bm.verts if v.select]
            plane_normal = plane_no

            if context.scene.vertex_projection_props.use_vertex_normal:
                plane_normal = context.scene.vertex_projection_props.vertex_normal

            for vert in selected_verts:
                try:
                    vert.co = mat.inverted() @ mathutils.geometry.intersect_line_plane(
                        mat @ vert.co, mat @ vert.co + plane_normal * 2, plane_co, plane_no, self.is_positive)
                except:
                    self.report({'WARNING'}, f"Vertex {vert.index} does not intersect with this plane")
        else:
            selected_edges = [e for e in bm.edges if e.select]

            for edge in selected_edges:
                v1 = mat @ edge.verts[0].co
                v2 = mat @ edge.verts[1].co
                dir1 = mathutils.Vector((plane_co - v2).normalized())
                dir2 = mathutils.Vector((plane_co - v1).normalized())
                dot_product = dir1.dot(plane_no)                    
                dist1 = abs(mathutils.geometry.distance_point_to_plane(v1, plane_co, plane_no))
                dist2 = abs(mathutils.geometry.distance_point_to_plane(v2, plane_co, plane_no))
                # if self.is_closest:
                #     self.is_closest = False
                #     if (dist1 > dist2):
                #         try:
                #             edge.verts[1].co = mat.inverted() @ mathutils.geometry.intersect_line_plane(v1, v2, plane_co, plane_no, self.is_positive)
                #         except:
                #             self.report({'WARNING'}, f"Edge № {edge.index} does not intersect with this plane")
                #     else:
                #         try:
                #             edge.verts[0].co = mat.inverted() @ mathutils.geometry.intersect_line_plane(v2, v1, plane_co, plane_no, self.is_positive)
                #         except:
                #             self.report({'WARNING'}, f"Edge № {edge.index} does not intersect with this plane")
                    # else:
                    #     if (dist1 < dist2):
                    #         try:
                    #             edge.verts[0].co = mat.inverted() @ mathutils.geometry.intersect_line_plane(v1, v2, plane_co, plane_no, self.is_positive)
                    #         except:
                    #             self.report({'WARNING'}, f"Edge № {edge.index} does not intersect with this plane")
                    #     else:
                    #         try:
                    #             edge.verts[1].co = mat.inverted() @ mathutils.geometry.intersect_line_plane(v2, v1, plane_co, plane_no, self.is_positive)
                    #         except:
                    #             self.report({'WARNING'}, f"Edge № {edge.index} does not intersect with this plane")
                #else:
                if ((dot_product < 0 and dir2.dot(plane_no) < 0) or (dir2.dot(plane_no) > 0 and dot_product > 0)) or self.is_closest :
                    if not bpy.context.scene.vertex_projection_props.use_outside_edges and not self.is_closest:
                        continue
                    if dist1 > dist2:
                        try:
                            edge.verts[1].co = mat.inverted() @ mathutils.geometry.intersect_line_plane(v1, v2, plane_co, plane_no, self.is_positive)
                        except: 
                            self.report({'WARNING'}, f"Edge № {edge.index} does not intersect with this plane")
                    else:
                        try:
                            edge.verts[0].co = mat.inverted() @ mathutils.geometry.intersect_line_plane(v2, v1, plane_co, plane_no, self.is_positive)
                        except: 
                            self.report({'WARNING'}, f"Edge № {edge.index} does not intersect with this plane")
                elif not self.is_closest:
                    if self.is_positive and dot_product < 0 or not self.is_positive and dot_product > 0:
                        try:
                            edge.verts[1].co = mat.inverted() @ mathutils.geometry.intersect_line_plane(v1, v2, plane_co, plane_no, self.is_positive)
                        except: 
                            self.report({'WARNING'}, f"Edge № {edge.index} does not intersect with this plane")
                    else:
                        try:
                            edge.verts[0].co = mat.inverted() @ mathutils.geometry.intersect_line_plane(v2, v1, plane_co, plane_no, self.is_positive)
                        except: 
                            self.report({'WARNING'}, f"Edge № {edge.index} does not intersect with this plane")

        if self.is_closest:
            self.is_closest = False
        bmesh.update_edit_mesh(mesh, loop_triangles=False)
        return {'FINISHED'}


class ShowDebugHelper(bpy.types.Operator):
    """Show or hide visual helpers for the projection plane and icons"""
    bl_idname = "wm.show_debug"
    bl_label = "Show Debug"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and bpy.context.active_object.type == 'MESH'

    def execute(self, context):
        global draw_handler_handle, rect_batch, plus_batch, minus_batch
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
        if draw_handler_handle is None:
            args = (self, context)
            draw_handler_handle = bpy.types.SpaceView3D.draw_handler_add(draw, args, 'WINDOW', 'POST_VIEW')        
            return {'FINISHED'}
        else:
            bpy.types.SpaceView3D.draw_handler_remove(draw_handler_handle, 'WINDOW')
            draw_handler_handle = None
            rect_batch = None
            plus_batch = None
            minus_batch = None
            return {'FINISHED'}


draw_handler_handle = None
rect_batch = None
plus_batch = None
minus_batch = None

def get_geometry_batches(self, context):
    global rect_batch, plus_batch, minus_batch
    rect_size = context.preferences.addons[__name__].preferences.plane_scale
    icon_size = context.preferences.addons[__name__].preferences.icon_scale
    
    obj = bpy.context.active_object
    if obj and obj.type == 'MESH':
        cursor_loc = bpy.context.scene.cursor.location
        cursor_normal = bpy.context.scene.vertex_projection_props.plane_normal

        # Define the vertices for the rectangle
        local_rect_verts = [
            mathutils.Vector((-rect_size, rect_size, 0)),
            mathutils.Vector((-rect_size, -rect_size, 0)),
            mathutils.Vector((rect_size, -rect_size, 0)),
            mathutils.Vector((rect_size, rect_size, 0))
        ]

        # Define the vertices for the "+" icon
        local_plus_verts = [
            mathutils.Vector((icon_size, 0, 0)),
            mathutils.Vector((-icon_size, 0, 0)),
            mathutils.Vector((0, icon_size, 0)),
            mathutils.Vector((0, -icon_size, 0))
        ]

        # Define the vertices for the "-" icon
        local_minus_verts = [
            mathutils.Vector((icon_size, 0, 0)),
            mathutils.Vector((-icon_size, 0, 0))
        ]

        # Rotate the vertices by the cursor normal
        rotation_matrix = cursor_normal.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        rect_verts = [cursor_loc + rotation_matrix @ vert for vert in local_rect_verts]

        # Create batches
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        rect_indices = ((0, 1, 2), (2, 3, 0))
        rect_batch = batch_for_shader(shader, 'TRIS', {"pos": rect_verts}, indices=rect_indices)

        # Calculate the view matrix and its inverse
        view_matrix = context.region_data.view_matrix.copy()
        view_matrix.translation = mathutils.Vector((0, 0, 0))
        inv_view_matrix = view_matrix.inverted()

        # Apply the inverse view matrix to the icons' vertices
        plus_verts = [(cursor_loc + cursor_normal * (icon_size + context.preferences.addons[__name__].preferences.icon_distance) + inv_view_matrix @ vert) for vert in local_plus_verts]
        minus_verts = [(cursor_loc - cursor_normal * (icon_size + context.preferences.addons[__name__].preferences.icon_distance) + inv_view_matrix @ vert) for vert in local_minus_verts]

        plus_indices = ((0, 1), (2, 3))
        plus_batch = batch_for_shader(shader, 'LINES', {"pos": plus_verts}, indices=plus_indices)

        minus_indices = ((0, 1),)
        minus_batch = batch_for_shader(shader, 'LINES', {"pos": minus_verts}, indices=minus_indices)

    return rect_batch, plus_batch, minus_batch
    
def update_mode(self, context):
    if context.active_object and context.active_object.type == 'MESH' and context.active_object.mode == 'EDIT':
        draw(self, context)

# Draw handler function
def draw(self, context):
    global rect_batch, plus_batch, minus_batch
    obj = context.active_object
    if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
        rect_batch, plus_batch, minus_batch = get_geometry_batches(self, context)

        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
        vertex_batches = []

        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)
        bm.normal_update()

        mat = obj.matrix_world
        plane_no = bpy.context.scene.vertex_projection_props.plane_normal
        plane_co = context.scene.cursor.location
        
        shader.uniform_float("color", (context.preferences.addons[__name__].preferences.line_color))
        gpu.state.line_width_set(context.preferences.addons[__name__].preferences.line_thickness)
        if bpy.context.scene.vertex_projection_props.use_vertices_only:
            selected_verts = [v for v in bm.verts if v.select]
            for vert in selected_verts:
                try:
                    plane_normal = plane_no
                    if (bpy.context.scene.vertex_projection_props.use_vertex_normal):
                        plane_normal = bpy.context.scene.vertex_projection_props.vertex_normal
                    v2 = mat.inverted() @ mathutils.geometry.intersect_line_plane(mat @ vert.co, mat @ vert.co + plane_normal * 2, plane_co, plane_no, False)
                    line_start = mat @ vert.co
                    line_end = mat @ v2
                    line_batch = batch_for_shader(shader, 'LINES', {"pos": [line_start, line_end]})
                    vertex_batches.append(line_batch)
                except:
                    continue
            for batch in vertex_batches:
                batch.draw(shader)
        gpu.state.blend_set('ALPHA_PREMULT')
        gpu.state.line_width_set(context.preferences.addons[__name__].preferences.icon_thickness)
        shader.uniform_float("color", (0.0, 1.0 * context.preferences.addons[__name__].preferences.icon_alpha, 0.0, 1 * context.preferences.addons[__name__].preferences.icon_alpha))
        plus_batch.draw(shader)
        shader.uniform_float("color", (1.0 * context.preferences.addons[__name__].preferences.icon_alpha, 0.0, 0.0, 1 * context.preferences.addons[__name__].preferences.icon_alpha))
        minus_batch.draw(shader)
        gpu.state.blend_set(context.preferences.addons[__name__].preferences.blend)
        shader.uniform_float("color", (context.preferences.addons[__name__].preferences.plane_color))
        gpu.state.depth_test_set('LESS')
        gpu.state.depth_mask_set(True)
        rect_batch.draw(shader)
        gpu.state.depth_mask_set(False)
        


classes = (
    VertexProjectionProperties,
    VertexProjectionPanel,
    VertexProjectionOptionsPanel,
    VisualDebugOptionsPanel,
    SetNormal,
    SetNormalSel,
    ExecuteProjection,
    ShowDebugHelper
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.vertex_projection_props = PointerProperty(type=VertexProjectionProperties)
    #bpy.app.handlers.depsgraph_update_post.append(update_mesh_data)
    bpy.app.handlers.load_post.append(update_mode)


def unregister():
    global draw_handler_handle, rect_batch, plus_batch, minus_batch

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.vertex_projection_props

    # Check if update_mode is in the list before removing
    if update_mode in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(update_mode)

    # Cleanup draw handler and batches
    if draw_handler_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(draw_handler_handle, 'WINDOW')
        draw_handler_handle = None
        rect_batch = None
        plus_batch = None
        minus_batch = None


if __name__ == "__main__":
    register()