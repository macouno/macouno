# mesh_grow.py Copyright (C) 2012, Dolf Veenvliet
#
# Extrude a selection from a mesh multiple times
#
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
	"name": "Distance from cursor",
	"author": "Dolf Veenvliet",
	"version": 1,
	"blender": (2, 6, 4),
	"api": 31847,
	"location": "View3D > Specials > Distance from cursor",
	"description": "Set selected vertexes to a specific distance from the cursor",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"}
	
	
"""
Usage:

Launch from "W-menu"

Additional links:
	Author Site: http://www.macouno.com
	e-mail: dolf {at} macouno {dot} com
"""

import bpy, mathutils
from bpy.props import FloatProperty

# Grow stuff!
def Set_Distance(context, distance):

	bpy.ops.object.mode_set(mode='OBJECT')
	
	c = context.scene.cursor_location
	m = context.active_object.matrix_world
	for v in context.active_object.data.vertices:
		if v.select:
		
			vRel = mathutils.Vector((v.co*m) - c).normalized()
			
			v.co = c + (vRel * distance)
			
	bpy.ops.object.mode_set(mode='EDIT')
	
	return
	

class Distance_init(bpy.types.Operator):
	'''Grow by extruding and moving/rotating/scaling multiple times'''
	bl_idname = 'mesh.cursor_distance'
	bl_label = 'Distance from cursor'
	bl_options = {'REGISTER', 'UNDO'}
	
	
	# Translation
	distance = FloatProperty(name='Distance', description='Distance in Blender units', default=1.0, min=-1000.0, max=1000.0, soft_min=-1000.0, soft_max=1000.0, step=100, precision=2)


	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return obj and obj.type == 'MESH'

	def execute(self, context):
		SET = Set_Distance(context, self.distance) 
		return {'FINISHED'}

		

def menu_func(self, context):
	self.layout.operator(Distance_init.bl_idname, text="Distance from cursor")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)

if __name__ == "__main__":
	register()