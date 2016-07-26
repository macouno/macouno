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

import bpy, mathutils, math
from copy import copy
from time import time
from bpy.app.handlers import persistent
from collections import namedtuple
from bpy.props import IntProperty, EnumProperty, FloatVectorProperty, FloatProperty, BoolProperty
from macouno import bmesh_extras, scene_update
from macouno.snet_core import *
from macouno.snet_utils import *

Volume = namedtuple("Volume", "data dimms")
	

	
@persistent
def SNet_Update(context):
	
	#scn = context.scene
	
	for ob in context.objects:
		if ob.SNet_enabled:
			try:
				growing = ob['SNet_growing']
			except:
				growing = False
				
			if growing:
				SNet_GrowStep(ob)
		
			#if ob.location[0] < 10.0:
			#	ob.location[0] += 0.01
			
			
			
def SNet_Set(self, value):
	if self.SNet_enabled:
		print('Enabling Surface Net')
	else:
		print('Disabling Surface Net')
		
		

# Set up the object!
def SNet_Add(context, debug, gridSize, animate, useCoords):

	# Make a new mesh and object for the surface
	me = bpy.data.meshes.new("Surface")
	ob = bpy.data.objects.new('Surface', me)
	
	scn = context.scene
	scn.objects.link(ob)
	
	# Make some variables for the object
	ob.SNet_enabled = True
	
	ob['SNet_debug'] = debug
	ob['SNet_animate'] = animate
	ob['SNet_lastMod'] = time()
	ob['SNet_useCoords'] = useCoords
<<<<<<< .mine
	ob['SNet_growSpeed'] = 0.05
	ob['SNet_growTime'] = 5.0 #Nr of seconds each item takes to grow
	ob['SNet_stateLength'] = 100
	ob['SNet_stateHalf'] = round(ob['SNet_stateLength'] * 0.5)
=======
	ob['SNet_growTime'] = 5.0 # in seconds to completion
	ob['SNet_lastMod'] = time.time()
>>>>>>> .r121
	
	ob['SNet_gridSize'] = mathutils.Vector((gridSize,gridSize,gridSize))
	ob['SNet_gridX'] = gridSize
	ob['SNet_gridY'] = gridSize
	ob['SNet_gridZ'] = gridSize
	ob['SNet_gridLevel'] = ob['SNet_gridX'] * ob['SNet_gridY']
	ob['SNet_gridLen'] = ob['SNet_gridLevel'] * ob['SNet_gridZ']
	ob['SNet_gridCnt'] = ob['SNet_gridLen'] / ob['SNet_gridLevel']
	ob['SNet_gridRes'] = [ob['SNet_gridX'], ob['SNet_gridY'], ob['SNet_gridZ']]
	
	
	# Make target and state values
	ob['SNet_targetList'] = array('f', ones_of(ob['SNet_gridLen']))
<<<<<<< .mine
	ob['SNet_currentList'] = array('f', ones_of(ob['SNet_gridLen']))
	ob['SNet_stateList'] = array('f', minus_of(ob['SNet_gridLen']))
=======
	ob['SNet_currentList'] = [t for t in ob['SNet_targetList']]
	ob['SNet_stateList'] = [False for t in ob['SNet_targetList']]
>>>>>>> .r121
	
	# The max and min values for our grid
	ob['SNet_limitMax'] = 1.0
	ob['SNet_limitMin'] = -1.0
	
	# let's get the location of the 3d cursor
	curLoc = scn.cursor_location
	
	 # Make a list of all coordinates
	if useCoords:
		if debug:
			print('		- Generating list of coordinates')
		ob['SNet_coords'] = SNet_MakeCoords(ob['SNet_gridLen'], ob['SNet_gridRes'])
	elif debug:
		ob['SNet_coords'] = []
		if debug:
			print('		- Calculating coordinates live')

	ob['SNet_targetList'], ob['SNet_stateList'] = SNet_MakeBall(ob['SNet_stateList'], ob['SNet_targetList'], ob['SNet_gridX'], ob['SNet_gridY'], ob['SNet_gridZ'], ob['SNet_gridLevel'], ob['SNet_gridLen'], ob['SNet_limitMax'], ob['SNet_limitMin'], ob['SNet_gridRes'], ob['SNet_coords'], ob['SNet_useCoords'])
	
	ob['SNet_growing'] = True
	
	# Select the object
	ob.select = True
	scn.objects.active = ob
		
		
		

class OpAddSurfaceNet(bpy.types.Operator):
	"""Add a surface net"""
	bl_idname = "mesh.primitive_surface_net"
	bl_label = "Add Surface Net"
	bl_options = {"REGISTER", "UNDO"}
	
	modes=(
		('NON', 'No', 'Instant result in the interface'),
		('RED', 'Redraw', 'Redraw the interface showing the results'),
		('ANI', 'Animate', 'Render an animation using your rendersettings'),
		)
	
<<<<<<< .mine
	showGrowth = EnumProperty(items=modes, name='showGrowth', description='What to do on update', default='RED')
	
=======
	animate = EnumProperty(items=modes, name='Animate', description='What to do on update', default='RED')
	
>>>>>>> .r121
	useCoords = BoolProperty(name='Use Coordinate List', description='Use a list of coordinates in stead of calculating every position', default=True)
	
	gridSize = IntProperty(name='Grid Size', default=10, min=0, max=100, soft_min=0, soft_max=1000)
	
	debug = BoolProperty(name='Debug', description='Get timing info in the console', default=True)

	def execute(self, context):
		SNet_Add(context, self.debug, self.gridSize, self.animate, self.useCoords)
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(OpAddSurfaceNet.bl_idname, text="Surface Net", icon="MESH_CUBE")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_mesh_add.append(menu_func)
	
	# Is this object a net?
	bpy.types.Object.SNet_enabled = bpy.props.BoolProperty(default=False, name="Enable Surface Net", update=SNet_Set)
	
	# Add an app handler
	bpy.app.handlers.scene_update_pre.append(SNet_Update)


def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_mesh_add.remove(menu_func)
	
	del bpy.types.Object.SNet_enabled
	
	bpy.app.handlers.scene_update_pre.remove(SNet_Update)
	

if __name__ == "__main__":
	register()