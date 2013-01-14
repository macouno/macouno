# mesh_normalsmooth.py Copyright (C) 2011, Dolf Veenvliet
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
	"name": "Normal smooth",
	"author": "Dolf Veenvliet",
	"version": 8,
	"blender": (2, 5, 6),
	"api": 31847,
	"location": "View3D > Specials > Normalsmooth",
	"description": "Nicer smoothing of your mesh",
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

import bpy, math, mathutils
	
def NormalSmooth(context):

	bpy.ops.object.mode_set(mode='OBJECT')
	
	ob = context.active_object
	me = ob.data
	selVerts = []
	nuCos = []

	# Lets see if there's any selected vertices
	for v in me.vertices:
		if v.select:
			nuCos.append(True)
			selVerts.append(v.index)
		else:
			nuCos.append(False)
			
	# Only run if there are selected vertices
	if len(selVerts):
		
		print(' - Found',len(selVerts),'selected vert')
		
		# Loop through the vertices to move
		for v1Index in selVerts:
			
			vCheck = []
			v1 = me.vertices[v1Index]
			
			# Find the verts that share a polygon with this one
			for p in me.polygons:
				if v1Index in p.vertices:
					for v2Index in p.vertices:
						if not v2Index in vCheck and not v2Index == v1Index:
							vCheck.append(v2Index)
				
			# Nothing to do if there's no connected verts            
			if len(vCheck):
				
				# Start a new vector
				vNew = mathutils.Vector()
				
				for v2Index in vCheck:
					
					v2 = me.vertices[v2Index]
					
					# Get a vector from v1 to v2
					VVVector = (v1.co - v2.co)
					
					# Find out how far they are apart
					VVLength = VVVector.length
					
					# Get the normal of v2 (normalized!)
					v2Nor = (v2.normal).normalized()
					
					# Get the cross vector of the two
					vCross = v2Nor.cross(VVVector)
					
					# get the normal rotated 90 degrees towards v1
					mat = mathutils.Matrix.Rotation(math.radians(-90), 3, vCross)
					
					nVec = (mat * VVVector.normalized())
					
					# now make the resulting vector half the length of the distance
					nVec = nVec.normalized() * (VVLength * 0.514)
					
					# Add it to v2's position
					nVec += v2.co
					
					vNew += nVec
					
				# Divide the new vector by the number of added vectors
				vNew *= (1.0/len(vCheck))
				
				nuCos[v1Index] = vNew
		
	# Apply all the new coordinates
	for i, co in enumerate(nuCos):
		if co:
			me.vertices[i].co = co
			
	print(' FINISHED\n')
	bpy.ops.object.mode_set(mode='EDIT')

	

class NormalSmooth_init(bpy.types.Operator):
	bl_idname = 'mesh.normalsmooth'
	bl_label = 'Normal Smooth'
	bl_options = {'REGISTER', 'UNDO'}
	

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		NormalSmooth(context) 
		return {'FINISHED'}

		

def menu_func(self, context):
	self.layout.operator(NormalSmooth_init.bl_idname, text="Normal Smooth")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)

if __name__ == "__main__":
	register()