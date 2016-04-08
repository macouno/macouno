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
	"name": "Add Surface Net",
	"author": "macouno",
	"version": (0, 1),
	"blender": (2, 7, 0),
	"location": "View3D > Add > Mesh > Surface Net",
	"description": "Create a mesh from a surface net",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"support": 'TESTING',
	"category": "Add Mesh"}

import bpy, mathutils, math, time
from copy import copy
from bpy.props import IntProperty, EnumProperty, FloatVectorProperty, FloatProperty, BoolProperty
from macouno import bmesh_extras, scene_update
from macouno.surface_nets import *

Volume = namedtuple("Volume", "data dimms")



class SurfaceNet():

	# Initialise the class
	def __init__(self, context, debug, useCoords, showGrowth):
	
		#bpy.ops.object.mode_set(mode='OBJECT')
			
		bpy.ops.object.select_all(action='DESELECT')
	
		self.debug = debug
		self.useCoords = useCoords
		self.showGrowth = showGrowth
		self.growing = False
		self.currentList = []
		self.targetList = []
		
		# Make the grid!
		self.gridSize = 10
		self.gridRes = [self.gridSize, self.gridSize, self.gridSize]
		self.gridLen = self.gridRes[0] * self.gridRes[1] * self.gridRes[2]
		
		# Make a new mesh and object for the surface
		self.shapeMesh = bpy.data.meshes.new("Surface")
		self.shapeObject = bpy.data.objects.new('Surface', self.shapeMesh)
		
		scene = context.scene
		scene.objects.link(self.shapeObject)

		if self.debug:
			print('\n	--- STARTING ---\n')
			self.startTime = time.time()


		# let's get the location of the 3d cursor
		curLoc = bpy.context.scene.cursor_location
		
		self.mesher = SurfaceNetMesher()
		
		self.targetList = array('f', zeros_of(self.gridLen))
		self.currentList = copy(self.targetList)
		
		 # Make a list of all coordinates
		if useCoords:
			if self.debug:
				print('		- Generating list of coordinates')
			self.coords = MakeCoords(self.gridLen, self.gridRes)
		elif self.debug:
			print('		- Calculating coordinates live')
		
		middle = mathutils.Vector((self.gridRes[0]*0.5,self.gridRes[1]*0.5,self.gridRes[2]*0.5))
		
		for i in range(self.gridLen):
		
			if self.useCoords:
				distV = middle - self.coords[i]
			else:
				distV = middle - GetLocation(self.gridRes, i) #coords[i]
				
			dist = distV.length
			
			self.targetList[i] = round(dist - 2.5, 2)

		self.GrowShape()

		# Select the new object
		self.shapeObject.select = True
		scene.objects.active = self.shapeObject
		

		if self.debug:
			now = time.time()
			print('		- Time spent =', str(round((now - self.startTime), 3))+'s')
			print('\n	--- FINISHED SURFACE NET ---\n')
			
		return

		
		
	def GrowShape(self):
	
		if self.showGrowth:
			# Create the meshed volume
			meshed_volume = self.mesher.mesh_volume(*Volume(dimms = self.gridRes, data = self.targetList))
			
			# Apply the volume data to the mesh
			self.shapeObject.data = mesh_from_data(*meshed_volume)
			
			scene_update.go()
			
		else:
			# Create the meshed volume
			meshed_volume = self.mesher.mesh_volume(*Volume(dimms = self.gridRes, data = self.targetList))
			
			# Apply the volume data to the mesh
			self.shapeObject.data = mesh_from_data(*meshed_volume)
			
			scene_update.go()
		
		
		
	# Get the location at a specific position in the grid
	def GetLocation(self, res, position):

		xRes = res[1]

		# The total nr of positions per layer
		layer = res[0] * xRes
		
		# The relative position on the final z layer
		xyRes = position % layer
		
		# The z position
		z = (position - xyRes) / layer
		
		x = xyRes % xRes
		
		y = (xyRes - x) / xRes
		
		return mathutils.Vector((x,y,z))
		

		
	# Make coordinates for every point in the volume (not needed if you use GetLocation
	def MakeCoords(self, len, res):

		coords = []
		
		# Make a coordinate for every point in the volume
		x = y = z = 0
		for i in range(len):
			
			coords.append(mathutils.Vector((x, y, z)))

			# Go up a level if you move beyond the x or y resolution
			x += 1
			if x == res[0]:
				x = 0
				y += 1
			if y == res[1]:
				y = 0
				z += 1

		return coords

		

class OpAddSurfaceNet(bpy.types.Operator):
	"""Add a surface net"""
	bl_idname = "mesh.primitive_surface_net"
	bl_label = "Add Surface Net"
	bl_options = {"REGISTER", "UNDO"}
	
	showGrowth = BoolProperty(name='Show Growth', description='Update the scene to show the growth of the form (takes more time and memory)', default=True)
	
	useCoords = BoolProperty(name='Use Coordinate List', description='Use a list of coordinates in stead of calculating every position', default=False)
	
	debug = BoolProperty(name='Debug', description='Get timing info in the console', default=True)

	def execute(self, context):
		Net = SurfaceNet(context, self.debug, self.useCoords, self.showGrowth);
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(OpAddSurfaceNet.bl_idname, text="Surface Net", icon="MESH_CUBE")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
	register()