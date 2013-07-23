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
from macouno import select_polygons, mesh_extras, misc, falloff_curve

# Bump stuff!
class Cast_Loop():

	# Initialise the class
	def __init__(self, context, shape,scale,scale_falloff, corner_group):
	
		self.ob = context.active_object
		self.me = self.ob.data
		self.scale = scale
		self.scale_falloff = scale_falloff
		self.mod = self.ob.mode
		
		# Get/make a corner group vertex group
		if corner_group:
			try:
				corner_group = self.ob.vertex_groups[corner_group]
			except:
				corner_group = self.ob.vertex_groups.new(corner_group)
				
		if self.mod == 'EDIT':
			bpy.ops.object.mode_set(mode='OBJECT')
				
		# Now only the outer loop
		self.selVerts = mesh_extras.get_selected_vertices()
		
		if len(self.selVerts) == len(self.me.vertices):
			print('>> NO CASTING SINCE EVERYTHING IS SELECTED <<')
			return
		
		self.outVerts = []
		self.inVerts = []
		self.cent = mathutils.Vector()
		normal = mathutils.Vector()
		
		for p in self.me.polygons:
			if not p.select:
				for v in p.vertices:
					vert = self.me.vertices[v]
					if vert.select and not vert in self.outVerts:
						self.outVerts.append(vert)
						self.cent += vert.co
			else:
				normal += p.normal
				
				#for v in p.vertices:
				#	normal += self.me.vertices[v].normal
				
				
		# Hey we need outer edges too!
		self.outEdges = []
		
		for e in self.me.edges:
			
			foundIn = False
			foundOut = False
			
			v1 = e.vertices[0]
			v2 = e.vertices[1]
			
			for p in self.me.polygons:
				
				if foundIn is False and p.select is True and v1 in p.vertices and v2 in p.vertices:
					foundIn = True				
				if foundOut is False and p.select is False and v1 in p.vertices and v2 in p.vertices:
					foundOut = True
		
		
			if foundIn and foundOut:
				self.outEdges.append(e)
					
		#print('found',len(self.outEdges),'edges')
		
		normal = normal.normalized()
		vCount = len(self.outVerts)
		self.cent /= vCount
		
		# Find all verts inside of the selection
		for v in self.selVerts:
			if v.select and not v in self.outVerts:
				self.inVerts.append(v)
		

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
		#return
		
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
		#return
		
		# As a final step... we want them to be rotated neatly around the center...
		step = math.radians(360) / (vCount)
		
		# The first one we don't move... So lets find the second!
		v1 = self.outVerts[topVert]
		v1in = v1.index
		v1co = v1.co - self.cent
		self.doneVerts = [v1in]
		
		# Place the verts equidistantly around the midpoint
		self.oVerts = [v1]
		self.oRig = v1co
		self.dVec = False
		self.doneEdges = []
		self.stepRound(v1in,v1co,(step))
		
		# If we make a circle, we don't want any of the verts in the corner group
		if shape == 'CIR':
			for v in self.oVerts:
				if corner_group: corner_group.remove([v.index])
						
		
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
				
				# Get the starting line as a reference (is also a corner
				if not aLine:
					aLine = line
					self.currentX = 0.0
					self.factor = 1.0
					
					if corner_group: corner_group.add([v.index], 1.0, 'REPLACE')
					
				else:
				
					# Find the angle from the current starting line
					cAng = aLine.angle(line)
					
					# If the angle is bigger than a step, we make this the new start
					if cAng > math.radians(c):
					
						if corner_group: corner_group.add([v.index], 1.0, 'REPLACE')
						
						# Make sure the angle is correct!
						line =  misc.rotate_vector_to_vector(line, aLine, math.radians(c))
						v.co = (line * midDist) + self.cent
						aLine = line
						
						self.currentX = 0.0
						self.factor = 1.0
					
					# These should all be midpoints along the line!
					# make sure we don't do the last one... because it's the first one!
					else:
					
						# Remove non corner items from the corner group
						if corner_group: corner_group.remove([v.index])
						
						# Only if we have to scale and the line isn't straight!
						if self.scale != 1.0 and self.scale_falloff != 'STR':
						
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
				
			mesh_extras.smooth_selection(self.inVerts, 2)
		
		if self.mod == 'EDIT':
			bpy.ops.object.mode_set(mode='EDIT')
		
		
		
	# Rotate each vert around the center to create a neat circle
	def stepRound(self,v1in,v1co, step):
	
		for e in self.outEdges:
			
			eIn = e.index
			
			if not eIn in self.doneEdges and v1in in e.vertices:
			
				if v1in == e.vertices[0]:
					v2in = e.vertices[1]
				elif v1in == e.vertices[1]:
					v2in = e.vertices[0]

				v2 = self.me.vertices[v2in]
				
				# Add to the list of ordered verts!
				if not v2 in self.oVerts:
					self.oVerts.append(v2)
				
				v2co = v2.co - self.cent
				
				if self.dVec is False:
					self.dVec = v2co - v1co
					
				# If the dot is negative... we're moving back along the circle and we invert the step (move the vert toward the previous one in stead of away from it)
				dot = v2co.dot(self.dVec)
				
				#pre = v2co.angle(self.oRig)
				if dot < 0.0:
					v2co =  misc.rotate_vector_to_vector(v2co, v1co, -step)
				else:
					v2co =  misc.rotate_vector_to_vector(v2co, v1co, step)
				
				#post = v2co.angle(self.oRig)
				#print('  dot',round(dot,2),'pre',round(math.degrees(pre)),'post',round(math.degrees(post)),'step',round(math.degrees(step)))
				v2.co = v2co + self.cent
				
				self.doneVerts.append(v2in)
				self.doneEdges.append(eIn)
				self.dVec = v2co - v1co
				
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