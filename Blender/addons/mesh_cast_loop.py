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
from bpy.props import EnumProperty, BoolProperty, FloatProperty
from macouno import select_polygons, mesh_extras, misc, falloff_curve

# Bump stuff!
class Cast_Loop():

	# Initialise the class
	def __init__(self, context, shape,scale,scale_falloff):
	
		self.ob = context.active_object
		self.me = self.ob.data
		self.scale = scale
		self.scale_falloff = scale_falloff
		
		bpy.ops.object.mode_set(mode='OBJECT')
				
		# Now only the outer loop
		self.selVerts = mesh_extras.get_selected_vertices()
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
			if v.select and not v in self.outVerts:
				self.inVerts.append(v)
		

		
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
		top = False
		topVert = False
		for i,v in enumerate(self.outVerts):
			relPos = v.co - self.cent
			relPos = relPos.normalized() * midDist
			v.co = relPos + self.cent
			
			# Find the top vert for nice alignment of the shape (start the steploop here)
			if top is False or v.co[2] > top:
				top = v.co[2]
				topVert = i
			
		# As a final step... we want them to be rotated neatly around the center...
		step = math.radians(360) / (vCount)
		
		# The first one we don't move... So lets find the second!
		v1 = self.outVerts[topVert]
		v1in = v1.index
		v1co = v1.co - self.cent
		self.doneVerts = [v1in]
		
		# Place the verts equidistantly around the midpoint
		self.oVerts = [v1]
		self.stepRound(v1in,v1co,(step))
		
		if shape != 'CIR':
			
			# lets try putting them in a triangle
			if shape == 'TRI':
				cornerCount = 3.0
			elif shape == 'SQA':
				cornerCount = 4.0
			c = 360.0 / cornerCount
			a = (180.0 - c) * 0.5
			
			stepLen = math.ceil(len(self.outVerts) / cornerCount)
			
			aLine = False
			
			
			self.currentX = 0.0
			self.vec = self.scale
			self.factor = 1.0
			curve = falloff_curve.curve(self.scale_falloff, 'mult')
			
			for i, v in enumerate(self.oVerts):
			
				stepPos = i % stepLen

				
				# Get a normalized version of the current relative position
				line = mathutils.Vector(v.co - self.cent).normalized()
				
				# Get the starting line as a reference
				if not aLine:
					aLine = line
					self.currentX = 0.0
					self.factor = 1.0
					
				else:
				
					# Find the angle from the current starting line
					cAng = aLine.angle(line)
					
					# If the angle is bigger than a step, we make this the new start
					if cAng > math.radians(c):
						
						# Make sure the angle is correct!
						line =  misc.rotate_vector_to_vector(line, aLine, math.radians(c))
						v.co = (line * midDist) + self.cent
						aLine = line
						
						self.currentX = 0.0
						self.factor = 1.0
					
					# These should all be midpoints along the line!
					else:
					
						# Find out how far we are from the start as a factor (fraction of one?)
						angFac = cAng / math.radians(c)
						self.newX = angFac
						
						# Create a nice curve object to represent the falloff
						
						curve.update(1.0, 0.0, self.vec, self.currentX, self.newX)
						
						fac = abs(curve.currentVal)
						
						self.factor *= fac
						
						self.currentX = self.newX
						
						# Find the corner of the new triangle
						b = 180 - (a+math.degrees(cAng))
						
						# find the distance from the midpoint
						A = math.sin(math.radians(a)) / (math.sin(math.radians(b))/midDist)
						
						bLine = line * A
						
						bLine *= self.factor
						
						v.co = bLine + self.cent
				
			
			# Smooth the inner verts please (twice)
			for x in range(0,5):
				# First create a list with neat average positions
				newCo = []
				for v1 in self.inVerts:
					
					v1co = mathutils.Vector(v1.co)
					v1in = v1.index
					v1cn = 1
					
					for p in self.me.polygons:
						if v1in in p.vertices:
							for v2in in p.vertices:
								v1co += self.me.vertices[v2in].co
								v1cn += 1
								
					v1co /= v1cn
					newCo.append(v1co)
					
				# Apply the list of neat average positions
				for i, v in enumerate(self.inVerts):
					v.co = newCo[i]
		
		
		bpy.ops.object.mode_set(mode='EDIT')
		
		
		
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
					
					# Add to the list of ordered verts!
					self.oVerts.append(v2)
					
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
		('TRI', 'Triangle', ''),
		('SQA', 'Square', ''),
		)
		
	shape = EnumProperty(items=shapes, name='Method', description='The shape to apply', default='TRI')
	
	# Scale
	scale = FloatProperty(name='Scale', description='Translation in Blender units', default=1.0, min=0.01, max=10.0, soft_min=0.01, soft_max=100.0, step=10, precision=2)
	
	# The falloffs we use
	falloffs=(
		('SPI', 'Spike',''),
		('BUM', 'Bump',''),
		('SWE', 'Sweep',''),
		)
		
	scale_falloff = EnumProperty(items=falloffs, name='Falloff', description='The falloff of the scale', default='SPI')
	
	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		Cast = Cast_Loop(context, self.shape,self.scale,self.scale_falloff) 
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