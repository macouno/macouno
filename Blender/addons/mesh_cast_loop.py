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
	"description": "Extrude and translate/rotate/scale multiple times",
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
from bpy.props import EnumProperty, BoolProperty, FloatProperty
from macouno import select_polygons, mesh_extras, misc

# Bump stuff!
class Cast_Loop():

	# Initialise the class
	def __init__(self, context, shape):
	
		self.ob = context.active_object
		self.me = self.ob.data
		
		# Go to vertex select mode
		mode = bpy.context.tool_settings.mesh_select_mode
		oldMode = [mode[0],mode[1],mode[2]]
		bpy.context.tool_settings.mesh_select_mode = [True, False, False]
		
		bpy.ops.object.mode_set(mode='OBJECT')
		
		# Lets keep a list of all selected verts
		#selVerts = mesh_extras.get_selected_vertices()
				
		# Now only the outer loop
		self.outVerts = []
		self.inVerts = []
		for p in self.me.polygons:
			if not p.select:
				for v in p.vertices:
					vert = self.me.vertices[v]
					if vert.select and not vert in self.outVerts:
						self.outVerts.append(vert)
		vCount = len(self.outVerts)
		
		for v in self.me.vertices:
			if not v in self.outVerts:
				self.inVerts.append(v)
		
		# Cast to a circle
		if shape == 'CIR':
			
			# Find the midpoint
			self.cent = mathutils.Vector()
			normal = mathutils.Vector()
			for v in self.outVerts:
				self.cent += v.co
				normal += v.normal
			self.cent /= vCount
			normal = normal.normalized()
			
			# make a quaternion and a matrix representing this "plane"
			quat = normal.to_track_quat('-Z', 'Y')
			mat = quat.to_matrix()
			
			# Put all the verts in the plane...
			# Lets find out for each vert how far it is along the normal
			midDist = 0.0
			for v in self.outVerts:
				relPos = v.co - self.cent
				relDot = normal.dot(relPos)
				
				v.co += (normal * -relDot)
				midDist += relPos.length
				
			# The medium distance from the center point
			midDist /= vCount 
				
			# now lets put them all the right distance from the center
			for v in self.outVerts:
				relPos = v.co - self.cent
				relPos = relPos.normalized() * midDist
				v.co = relPos + self.cent
				
			# As a final step... we want them to be rotated neatly around the center...
			step = math.radians(360) / (vCount)
			
			# The first one we don't move... So lets find the second!
			v1in = self.outVerts[0].index
			v1co = self.outVerts[0].co - self.cent
			self.doneVerts = [v1in]
			
			self.stepRound(v1in,v1co,(step))
			
			

		'''
		for v in self.me.vertices:
			if v in selVerts:
				v.select = True
			else:
				v.select = False
		'''
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.context.tool_settings.mesh_select_mode = oldMode
		
		
		
	# Rotate each vert around the center to create a neat circle
	def stepRound(self,v1in,v1co, step):
	
		for e in self.me.edges:
			
			if v1in in e.vertices:
				if v1in == e.vertices[0]:
					v2in = e.vertices[1]
				elif v1in == e.vertices[1]:
					v2in = e.vertices[0]
				
				v2 = self.me.vertices[v2in]
					
				# make really sure this vert is the next in the loop
				if v2 in self.outVerts and not v2in in self.doneVerts:
					
					v2 = self.me.vertices[v2in]
					v2co = v2.co - self.cent
					
					v2co =  misc.rotate_vector_to_vector(v2co, v1co, step)
					
					v2.co = v2co + self.cent
					
					self.doneVerts.append(v2in)
					
					self.stepRound(v2in,v2co,step)
					return
				

		
	
		


class Cast_Loop_init(bpy.types.Operator):
	'''Reshape an edge loop'''
	bl_idname = 'mesh.cast_loop'
	bl_label = 'Cast Loop'
	bl_options = {'REGISTER', 'UNDO'}

	# The methods we use
	shapes=(
		('CIR', 'Circle', ''),
		('INF', 'Infinity', ''),
		)
		
	shape = EnumProperty(items=shapes, name='Method', description='The shape to apply', default='CIR')
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		Cast = Cast_Loop(context, self.shape) 
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