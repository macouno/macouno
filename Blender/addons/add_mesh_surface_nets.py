# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Surface Nets",
    "author": "macouno",
    "version": (0, 1),
    "blender": (2, 70, 0),
    "location": "View3D > Add > Mesh > Surface Nets",
    "description": "Create a mesh from a surface net",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
	"support": 'TESTING',
    "category": "Add Mesh"}

import bpy, mathutils, math
from macouno import bmesh_extras, scene_update
from macouno.surface_nets import *
from mathutils import Matrix



##------------------------------------------------------------
# calculates the matrix for the new object
# depending on user pref
def align_matrix(context):
    loc = Matrix.Translation(context.scene.cursor_location)
    obj_align = context.user_preferences.edit.object_align
    if (context.space_data.type == 'VIEW_3D'
        and obj_align == 'VIEW'):
        rot = context.space_data.region_3d.view_matrix.to_3x3().inverted().to_4x4()
    else:
        rot = Matrix()
    align_matrix = loc * rot
    return align_matrix
	
	
def get_override(area_type, region_type):
    for area in bpy.context.screen.areas: 
        if area.type == area_type:             
            for region in area.regions:                 
                if region.type == region_type:                    
                    override = {'area': area, 'region': region} 
                    return override
    #error message if the area or region wasn't found
    raise RuntimeError("Wasn't able to find", region_type," in area ", area_type,
                        "\n Make sure it's open while executing script.")

						
						
def scale(val):
	
	#we need to override the context of our operator    
	override = get_override( 'VIEW_3D', 'WINDOW' )
	
	bpy.ops.transform.resize(override, value=val, constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional=bpy.context.tool_settings.proportional_edit, proportional_edit_falloff=bpy.context.tool_settings.proportional_edit_falloff, proportional_size=1, snap=bpy.context.tool_settings.use_snap, snap_target=bpy.context.tool_settings.snap_target, snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)
	
	

def AddSurfaceNets():

	bpy.ops.object.mode_set(mode='OBJECT')

	# let's get the location of the 3d cursor
	curLoc = bpy.context.scene.cursor_location
	
	mesher = SurfaceNetMesher()

	volumes = [create_sphere(), create_torus()]
	for volume in volumes:
		meshed_volume = mesher.mesh_volume(*volume)
		mesh_data = mesh_from_data(*meshed_volume)
		cube_object = bpy.data.objects.new("Cube_Object", mesh_data)

		scene = bpy.context.scene
		scene.objects.link(cube_object)
	
	
	#bpy.context.active_object.location = curLoc
	
	
	
	
	
	#ob = bpy.context.active_object
	
	

	
	#bpy.ops.object.mode_set(mode='OBJECT')

	return


class AddStreetLight(bpy.types.Operator):
    """Add a street light mesh"""
    bl_idname = "mesh.primitive_light_surface_nets"
    bl_label = "Add Surface Nets"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        AddSurfaceNets();
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddStreetLight.bl_idname, text="Surface Nets", icon="MESH_CUBE")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()