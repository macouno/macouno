# mesh_multiform.py Copyright (C) 2011, Dolf Veenvliet
#
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
	"name": "Scale to",
	"author": "Dolf Veenvliet",
	"version": 1,
	"blender": (2, 6, 3),
	"api": 31847,
	"location": "Object > Scale to",
	"description": "Scale an object to a specific dimension",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Object"}

"""
Usage:

Launch from Object - Scale to
"""

import bpy
from bpy.props import FloatProperty, EnumProperty

# Make it as a class
def Scale_to(context, sc, xs):

	bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

	if xs == 'X':
		a = 0
	elif xs == 'Y':
		a = 1
	else:
		a = 2

	ob = context.active_object

	ob.scale *= (sc / ob.dimensions[a])

	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		
		
class Scale_to_init(bpy.types.Operator):
	'''Scale an object to a specific target dimension'''
	bl_idname = 'object.scale_to'
	bl_label = 'Scale to'
	bl_options = {'REGISTER', 'UNDO'}
	
	# The falloffs we use
	axiss=[
		('X', 'X', ''),
		('Y', 'Y', ''),
		('Z', 'Z', ''),
		]
	
	# Scale
	scale = FloatProperty(name='Scale', description='Dimension in Blender units', default=1.0, min=0.01, max=1000.0, soft_min=0.01, soft_max=1000.0, step=10, precision=2)
	
	xs = EnumProperty(items=axiss, name='Axis', description='The axis to scale in', default='X')

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		Scale_to(context, self.scale, self.xs) 
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(Scale_to_init.bl_idname, text="Scale to")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
	register()