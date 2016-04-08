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
from bpy.props import IntProperty, EnumProperty, FloatVectorProperty, FloatProperty, BoolProperty
from macouno import bmesh_extras, scene_update
from macouno.surface_nets import *
from mathutils import Matrix

Volume = namedtuple("Volume", "data dimms")





	

class SurfaceNet():

	# Initialise the class
	def __init__(self, context, debug, useCoords):
	
		self.debug = debug
		self.useCoords = useCoords

		if self.debug:
			print('\n	--- STARTING ---\n')
			self.startTime = time.time()
			
		bpy.ops.object.select_all(action='DESELECT')

		# let's get the location of the 3d cursor
		curLoc = bpy.context.scene.cursor_location
		
		mesher = SurfaceNetMesher()
		cub = 10
		
		res = [cub,cub,cub]
		len = res[0] * res[1] * res[2]
		
		data = array('f', zeros_of(len))
		
		 # Make a list of all coordinates
		if useCoords:
			self.coords = MakeCoords(len, res)
		
		middle = mathutils.Vector((res[0]*0.5,res[1]*0.5,res[2]*0.5))
		
		for i in range(len):
		
			if self.useCoords:
				distV = middle - self.coords[i]
			else:
				distV = middle - GetLocation(res, i) #coords[i]
			dist = distV.length
			
			data[i] = round(dist - 2.5, 2)
		
		dot = Volume(dimms = res, data = data)
		
		volumes = [dot]
		#volumes = [create_sphere()] #, create_torus()]
		for volume in volumes:
		
			#print(volume)
			meshed_volume = mesher.mesh_volume(*volume)
			mesh_data = mesh_from_data(*meshed_volume)
			cube_object = bpy.data.objects.new("Cube_Object", mesh_data)

			scene = bpy.context.scene
			scene.objects.link(cube_object)
			
			# Select the new object
			cube_object.select = True
			scene.objects.active = cube_object

		if self.debug:
			now = time.time()
			print('		- Time spent =', str(round((now - self.startTime), 3))+'s')
			print('\n	--- FINISHED SURFACE NET ---\n')
			
		return

		
	# Get the location at a specific position in the grid
	def GetLocation(res, position):

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
	def MakeCoords(len, res):

		coords = []
		
		# Make a coordinate for every point in the volume
		x = y = z = 0
		for i in range(len):
			
			coords.append(mathutils.Vector((x, y, z)))

			x = x + 1
			if x == res[0]:
				x = 0
				y = y + 1
			if y == res[1]:
				y = 0
				z = z + 1

		return coords


class OpAddSurfaceNet(bpy.types.Operator):
	"""Add a surface net"""
	bl_idname = "mesh.primitive_surface_net"
	bl_label = "Add Surface Net"
	bl_options = {"REGISTER", "UNDO"}
	
	useCoords = BoolProperty(name='Use Coordinates', description='Use a list of coordinates in stead of calculating every position', default=False)

	debug = BoolProperty(name='Debug', description='Get timing info in the console', default=True)

	def execute(self, context):
		Net = SurfaceNet(context, self.debug, self.useCoords);
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