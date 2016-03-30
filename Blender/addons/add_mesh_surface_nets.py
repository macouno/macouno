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
    "name": "Surface Nets",
    "author": "macouno",
    "version": (0, 1),
    "blender": (2, 7, 0),
    "location": "View3D > Add > Mesh > Surface Nets",
    "description": "Create a mesh from a surface net",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
	"support": 'TESTING',
    "category": "Add Mesh"}

import bpy, mathutils, math
from macouno import bmesh_extras, scene_update
from macouno.surface_nets import *
from mathutils import Matrix

Volume = namedtuple("Volume", "data dimms")



# Get the location at a specific position in the grid
def GetLocation(res, position):

	# The total nr of positions per layer
	layer = res[0] * res[1]
	
	# The relative position on the final z layer
	xyRes = position % layer
	
	# The z position
	z = (position - xyRes) / layer
	
	yRes = xyRes % res[1]
	
	y = (xyRes - yRes) / res[1]

	x = yRes 	
	
	return mathutils.Vector((x,y,z))
	
	



def AddSurfaceNets():

	bpy.ops.object.select_all(action='DESELECT')

	# let's get the location of the 3d cursor
	curLoc = bpy.context.scene.cursor_location
	
	mesher = SurfaceNetMesher()
	cub = 10
	
	res = [cub,cub,cub]
	len = res[0] * res[1] * res[2]
	
	data = array('f', zeros_of(len))
	'''
	# Make coordinates for every point in the volume (not needed if you use GetLocation
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
	
	print(coords)
	'''
	
	middle = mathutils.Vector((res[0]*0.5,res[1]*0.5,res[2]*0.5))
	
	for i in range(len):
	
		distV = middle - GetLocation(res, i) #coords[i]
		dist = distV.length
		
		data[i] = round(dist - 2.5, 2)
	
	dot = Volume(dimms = res, data = data)
	
	#print(dot)

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

	return


class AddStreetLight(bpy.types.Operator):
    """Add a street light mesh"""
    bl_idname = "mesh.primitive_light_surface_nets"
    bl_label = "Add Surface Nets"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):
        AddSurfaceNets();
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(AddStreetLight.bl_idname, text="Surface Nets", icon="MESH_CUBE")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()