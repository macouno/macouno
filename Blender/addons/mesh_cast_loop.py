# mesh_cast_loop.py Copyright (C) 2011, Dolf Veenvliet
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
	"name": "Cast Loop",
	"author": "Dolf Veenvliet",
	"version": 1,
	"blender": (2, 5, 6),
	"api": 31847,
	"location": "View3D > Specials > Cast Loop",
	"description": "Cast the outside of your selection to a specific shape",
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

import bpy, mathutils, math
from bpy.props import EnumProperty, BoolProperty, FloatProperty, StringProperty
from macouno import select_polygons, mesh_extras, misc, falloff_curve, bmesh_extras

# Bump stuff!
class Cast_Loop():

	# Initialise the class
	def __init__(self, context, shape,scale,scale_falloff, corner_group):
	
	
		if shape == 'TRI':
			corners = 3;
		elif shape == 'SQA':
			corners = 4
		else:
			corners = 0;
		
		bmesh_extras.cast_loop(corners=corners, falloff_scale=scale,falloff_shape=scale_falloff,corner_group=corner_group)
		return

		


class Cast_Loop_init(bpy.types.Operator):
	'''Reshape an edge loop'''
	bl_idname = 'mesh.cast_loop'
	bl_label = 'Cast Loop'
	bl_options = {'REGISTER', 'UNDO'}

	# The methods we use
	shapes=(
		('CIR', 'Circle', ''),
		('TRI', 'Triangle', ''),
		('SQA', 'Square', ''),
		)
		
	shape = EnumProperty(items=shapes, name='Method', description='The shape to apply', default='CIR')
	
	# Scale
	scale = FloatProperty(name='Scale', description='Translation in Blender units', default=1.0, min=0.01, max=10.0, soft_min=0.01, soft_max=100.0, step=10, precision=2)
	
	# The falloffs we use
	falloffs=(
		('STR', 'Straight',''),
		('SPI', 'Spike',''),
		('BUM', 'Bump',''),
		('SWE', 'Sweep',''),
		)
		
	scale_falloff = EnumProperty(items=falloffs, name='Falloff', description='The falloff of the scale', default='STR')
	
	corner_group = StringProperty(name="Corner Group", description="Name of the group to add corners to if there are any", default='', maxlen=100)
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		Cast = Cast_Loop(context, self.shape,self.scale,self.scale_falloff, self.corner_group) 
		return {'FINISHED'}

		

def menu_func(self, context):
	self.layout.operator(Cast_Loop_init.bl_idname, text="Cast Loop")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)

if __name__ == "__main__":
	register()