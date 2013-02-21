# object_check_angle.py Copyright (C) 2011, Dolf Veenvliet
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
	"name": "Check Angles",
	"author": "Dolf Veenvliet",
	"version": 1,
	"blender": (2, 6, 3),
	"api": 31847,
	"location": "Object > Check Angles",
	"description": "Check to see if an object has any faces too steep for extrusion printing",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Object"}

"""
Usage:

Launch from Object - Check Angle
"""

import bpy, mathutils, math
from bpy.props import FloatProperty

def Angle_Check(context, limit):

	checkLimit = limit
	checkFactor = 1.0 / (checkLimit * 0.25)

	down = mathutils.Vector((0.0,0.0,1.0))
	ob = context.active_object
	me = ob.data
		
	# Get the vertex colours
	if not me.vertex_colors.active:
		me.vertex_colors.new('steepness')
		for f in me.vertex_colors.active.data:
			try:
				f.color = (0.0,0.0,0.0)
			except:
				f.color = (0.0,0.0,0.0)
	
	
	for p in me.polygons:
		
		n = p.normal
		n = n.normalized()
		a = round(math.degrees(n.angle(down)))
		
		if a < checkLimit:
			
			a -= (checkLimit * 0.75)
			if a < 0.0:
				a = 0.0

			r = (checkLimit*0.25) - a
			r = r * checkFactor
			dif = (1.0 - r) * 0.5
			r = 1.0 - dif
			g = 1.0 - r
			b = 0.0
			#print('found',r,g)
			

		else:
			r = 0.0
			g = 0.0
			b = 1.0
			
		# range is used here to show how the polygons reference loops,
		# for convenience 'poly.loop_indices' can be used instead.
		for loop_index in range(p.loop_start, p.loop_start + p.loop_total):
		#for v in p.vertices:

			p_col = me.vertex_colors.active.data[loop_index]
			p_col.color[0] = r
			p_col.color[1] = g
			p_col.color[2] = b



class Angle_Check_init(bpy.types.Operator):
	'''Check to see if there are any hard to print angles int he object'''
	bl_idname = 'object.angle_check'
	bl_label = 'Check Angles'
	bl_options = {'REGISTER', 'UNDO'}
	
	# Scale
	limit = FloatProperty(name='Limit', description='Limit in degrees', default=40.0, min=0.0, max=180.0, soft_min=0.0, soft_max=360.0, step=10, precision=1)

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		Angle_Check(context, self.limit) 
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(Angle_Check_init.bl_idname, text="Check Angles")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
	register()