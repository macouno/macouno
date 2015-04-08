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
    "version": (2, 0),
    "blender": (2, 59, 0),
    "location": "View3D > Add > Mesh > Light",
    "description": "Grow a street light",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"}

import bpy
from macouno import bmesh_extras


def AddLight():

	bpy.ops.mesh.primitive_circle_add(vertices=12, radius=1, fill_type='TRIFAN', view_align=False, enter_editmode=False, location=(0, 0, 0))

	bpy.ops.object.mode_set(mode='EDIT')
		
	bpy.ops.mesh.select_all(action='SELECT')
	
	bpy.ops.mesh.cast_loop()
	
	corners = 3
	falloff_scale = 1.0
	# 		('STR', 'Straight',''),		('SPI', 'Spike',''),		('BUM', 'Bump',''),		('SWE', 'Sweep',''),
	scale_falloff = 'STR'

	bmesh_extras.cast_loop(corners=corners, falloff_scale=falloff_scale, falloff_shape=scale_falloff)
	
	
	
	bpy.ops.object.mode_set(mode='OBJECT')

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