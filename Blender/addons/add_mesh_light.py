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
    "name": "Street Light",
    "author": "macouno",
    "version": (0, 1),
    "blender": (2, 70, 0),
    "location": "View3D > Add > Mesh > Light",
    "description": "Grow a street light",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
	"support": 'TESTING',
    "category": "Add Mesh"}

import bpy, mathutils, math
from macouno import bmesh_extras, cast_loop
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
	
	

def AddLight():

	# let's get the location of the 3d cursor
	curLoc = bpy.context.scene.cursor_location

	bpy.ops.mesh.primitive_circle_add(vertices=24, radius=1, fill_type='TRIFAN', view_align=False, enter_editmode=False, location=(0, 0, 0))
	bpy.context.active_object.location = curLoc
	
	bpy.ops.object.mode_set(mode='EDIT')
	
	# Change Selection mode to face selection
	lastSelectioMode = bpy.context.tool_settings.mesh_select_mode[:]
	bpy.context.tool_settings.mesh_select_mode = (False, False, True)
		
	bpy.ops.mesh.select_all(action='SELECT')
	
	crn = 3
	fScale = 1.5
	# 		('STR', 'Straight',''),		('SPI', 'Spike',''),		('BUM', 'Bump',''),		('SWE', 'Sweep',''),
	fShape = 'BUM'

	cast_loop.cast(corners=crn, falloff_scale=fScale, falloff_shape=fShape)
	
	# Falloffs in LIN, INC, DEC, SWO, SPI, BUM, SWE
	bpy.ops.mesh.grow(
		translation=15,
		rotation=(0.0,math.radians(10),0.0),
		rotation_falloff='LIN',
		scale=0.5,
		scale_falloff='LIN',
		retain=True,
		steps=True,
		debug=False,
		animate=True,
		)
	
	bpy.ops.mesh.extrude_region()
	

	scale((2.0,2.0,2.0))
	
	
	crn = 4
	fScale = 1.0
	# 		('STR', 'Straight',''),		('SPI', 'Spike',''),		('BUM', 'Bump',''),		('SWE', 'Sweep',''),
	fShape = 'STR'

	cast_loop.cast(corners=crn, falloff_scale=fScale, falloff_shape=fShape)
	
	bpy.ops.mesh.grow(
		translation=2,
		rotation=(0.0,0.0,0.0),
		rotation_falloff='LIN',
		scale=0.5,
		scale_falloff='LIN',
		retain=True,
		steps=True,
		debug=False,
		animate=True,
		)
	
	# Put the cursor at the selected faces
	#bpy.ops.view3d.snap_cursor_to_selected()

	# Reset selection mode
	bpy.context.tool_settings.mesh_select_mode[:] = lastSelectioMode
	
	bpy.ops.object.mode_set(mode='OBJECT')
	
	#bpy.context.scene.cursor_location = mathutils.Vector((0.0,1.0,0.0))

	return


class AddStreetLight(bpy.types.Operator):
    """Add a street light mesh"""
    bl_idname = "mesh.primitive_light_add"
    bl_label = "Add Street Light"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        AddLight();
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddStreetLight.bl_idname, text="Street  Light", icon="MESH_CUBE")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()