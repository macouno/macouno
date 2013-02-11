# mesh_self_shadow.py Copyright (C) 2011, Dolf Veenvliet
#
# Relaxes selected vertices while retaining the shape as much as possible
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
	"name": "Self shadow",
	"author": "Dolf Veenvliet",
	"version": (0,4),
	"blender": (2, 6, 5),
	"api": 35851,
	"location": "View3D > Paint > Self shadow",
	"description": "Create vertex colours based on the mesh's angles",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"}

"""
Usage:

Launch from "Paint -> Self shadow"


Additional links:
	Author Site: http://www.macouno.com
	e-mail: dolf {at} macouno {dot} com
"""

import bpy, colorsys, math, mathutils
from bpy.props import EnumProperty, BoolProperty, FloatProperty

# Grow stuff!
class Self_shadow():

	# Initialise the class
	def __init__(self, context, contrast, method, normalize):
	
		bpy.ops.object.mode_set(mode='OBJECT')
	
		self.ob = context.active_object
		self.me = self.ob.data
		
		self.normalize = normalize
		self.contrast = contrast
		
		# Find the biggest and smallest value
		self.minimum = 0.0
		self.range = math.pi
		
		# Containers for the angles and nr of angles
		leng = len(self.me.vertices)
		self.angles= [0.0] * leng
		self.totAngles= [0] * leng
		
		# Get the vertex colours
		if not self.me.vertex_colors.active:
			self.me.vertex_colors.new('selfshadow')
			for f in self.me.vertex_colors.active.data:
				try:
					f.color1 = f.color2 = f.color3 = f.color4 = (0.0,0.0,0.0)
				except:
					f.color1 = f.color2 = f.color3 = (0.0,0.0,0.0)
					
		self.vCols = self.me.vertex_colors.active.data
		
		# Get the angles
		if method == 'POL':
			self.usePolygons()
		else:
			self.useEdges()
			
		if self.normalize:
			self.getMinMax()
		
		# Apply the colours
		self.applyColours()
		
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')
		
		
		
	# Use the mabaker method (uses face normals, for slower but smoother result)
	def usePolygons(self):
	
		for p in self.me.polygons:
		
			cent = mathutils.Vector()
			vList = []
			
			# Get the center point for each polygon
			for loop_index in range(p.loop_start, p.loop_start + p.loop_total):
				vIndex = self.me.loops[loop_index].vertex_index
				v = self.me.vertices[vIndex]
				vList.append([vIndex,v])
				cent += v.co
		
			cent /= p.loop_total
		
			# Now get the angle between the vert normal and the center
			# Get the center point for each polygon
			for vIndex, v in vList:
				vecOne = v.co - cent
		
				try:
					self.angles[vIndex] += vecOne.angle(v.normal)
					self.totAngles[vIndex] += 1
				except:
					continue
	
	
	
	# Use the old ma-Self script code to get a quick result
	# Uses connected edges and vert normals
	def useEdges(self):
		
		# Loop through all edges and find out for each vert what the angle to the connected edge is
		for e in self.me.edges:

			iOne = e.vertices[0]
			iTwo = e.vertices[1]
			
			vOne = self.me.vertices[iOne]
			vTwo = self.me.vertices[iTwo]

			vecOne = vOne.co - vTwo.co
			vecTwo = vTwo.co - vOne.co

			try:
				self.angles[iOne] += vecOne.angle(vOne.normal)
				self.angles[iTwo] += vecTwo.angle(vTwo.normal)
				
				self.totAngles[iOne] += 1
				self.totAngles[iTwo] += 1
			except:
				continue
				
				
				
	# Get the minimum and maximum for normalizing
	def getMinMax(self):
	
		min = 0
		max = 0
		set = False
		
		for i, a in enumerate(self.angles):
		
			angCnt = self.totAngles[i]
		
			if angCnt:
			
				angle = a / angCnt
				self.angles[i] = angle
				
				if not set:
					min = angle
					max = angle
					set = True
				else:
					if angle < min:
						min = angle
					elif angle > max:
						max = angle
				
		self.minimum = min
		self.range = max - min
		
		#print('range',math.degrees(self.range), math.degrees(min), math.degrees(max))
			
			
			
	def applyColours(self):

		# Make sure there are vertex colours
		try:
			vertex_colors = self.me.vertex_colors.active
		except:
			vertex_colors =self.me.vertex_colors.new(name="Self Shadow")

		self.me.vertex_colors.active = vertex_colors

		for p in self.me.polygons:
		
			for loop in p.loop_indices:
				v = self.me.loops[loop].vertex_index
				col_out = vertex_colors.data[loop].color
				
				# Get the actual angle (we might have added multiple up)
				if (not self.normalize) and self.totAngles[v] > 1:
					angle = self.angles[v] / self.totAngles[v]
				else:
					angle = self.angles[v]
					
				# The value is relative to pi (180 degrees)
				if not self.range: self.range = 1.0
				val =1.0 - ((angle-self.minimum)/self.range)
				
				# So lets make the val between -1 and + 1
				if self.contrast:
					
					val = val ** self.contrast
					val = 1.0 - val
				
					val = val ** self.contrast
					val = 1.0 - val
				
				ori = vertex_colors.data[loop].color
				v_col = colorsys.rgb_to_hsv(ori[0],ori[1],ori[2])
				if val > v_col[2]: val = v_col[2]
				v_col = colorsys.hsv_to_rgb(v_col[0],v_col[1],val)
				vertex_colors.data[loop].color = v_col
		
				

class Self_shadow_init(bpy.types.Operator):
	'''Generate vertex colours based on the mesh's angles'''
	bl_idname = 'paint.self_shadow'
	bl_label = 'Self shadow'
	bl_options = {'REGISTER', 'UNDO'}
	
	contrast = FloatProperty(name='Contrast', default=1.0, min=1.0, max=10.0, soft_min=1.0, soft_max=10.0, step=10, precision=2)
	
	# The methods we use
	methods=(
		('POL', 'Polygons', ''),
		('EDG', 'Edges', ''),
		)
		
	method = EnumProperty(items=methods, name='Method', description='The calculation method for colouring', default='EDG')
	
	normalize = BoolProperty(name='Normalize', description='Normalize/maximise the result', default=True)

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		SHADOW = Self_shadow(context, self.contrast, self.method, self.normalize)
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(Self_shadow_init.bl_idname, text="Self shadow")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_paint_vertex.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_paint_vertex.remove(menu_func)

if __name__ == "__main__":
	register()
