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
		if ob.SNet_enabled and ob.location[0] < 10.0:
			ob.location[0] += 0.01
			
			
			
def SNet_Set(self, value):
	if self.SNet_enabled:
		print('Enabling Surface Net')
	else:
		print('Disabling Surface Net')
		
		

# Set up the object!
def SNet_Add(context, debug, gridSize, showGrowth, useCoords):

	# Make a new mesh and object for the surface
	me = bpy.data.meshes.new("Surface")
	ob = bpy.data.objects.new('Surface', me)
	
	scn = context.scene
	scn.objects.link(ob)
	
	# Make some variables for the object
	ob.SNet_enabled = True
	
	ob['SNet_debug'] = debug
	ob['SNet_showGrowth'] = showGrowth
	ob['SNet_useCoords'] = useCoords
	ob['SNet_growSpeed'] = 0.05
	ob['SNet_stateLength'] = 100
	
	ob['SNet_gridSize'] = mathutils.Vector((gridSize,gridSize,gridSize))
	ob['SNet_gridX'] = gridSize
	ob['SNet_gridY'] = gridSize
	ob['SNet_gridZ'] = gridSize
	ob['SNet_gridRes'] = [ob['SNet_gridX'], ob['SNet_gridY'], ob['SNet_gridZ']]
	ob['SNet_gridLen'] = ob['SNet_gridX'] * ob['SNet_gridY'] * ob['SNet_gridZ']
	
	# Make target and state values
	ob['SNet_targetList'] = array('f', ones_of(gridSize))
	ob['SNet_currentList'] = array('f', ones_of(gridSize))
	ob['SNet_stateList'] = array('f', zeros_of(gridSize))
	
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

	ob['SNet_targetList'] = SNet_MakeBall(ob['SNet_stateList'], ob['SNet_targetList'], ob['SNet_gridX'], ob['SNet_gridY'], ob['SNet_gridZ'], ob['SNet_gridLen'], ob['SNet_limitMax'], ob['SNet_limitMin'], ob['SNet_coords'], ob['SNet_useCoords'])
		
	# Select the object
	ob.select = True
	scn.objects.active = ob
	
	
		
# OLD CLASS SHOULD NOT BE USED
class SurfaceNet():

	# Initialise the class
	def __init__(self, context, debug, useCoords, showGrowth):
	
		#bpy.ops.object.mode_set(mode='OBJECT')
		self.debug = debug
		
		if self.debug:
			print('\n	--- STARTING ---\n')
			self.startTime = time.time()
			
		# LOTS OF SETTINGS
		bpy.ops.object.select_all(action='DESELECT')
	
		self.useCoords = useCoords
		
		self.growSpeed = 0.05
		self.stateLength = 100
		self.stateHalf = round(self.stateLength * 0.5)
		self.showGrowth = showGrowth
		self.growing = False
		
		# The max and min values for our grid
		self.limitMax = 1.0
		self.limitMin = -1.0
		
		# Make the grid!
		self.gridSize = 10
		self.gridX = self.gridSize
		self.gridY = self.gridSize
		self.gridZ = self.gridSize
		self.gridLevel = self.gridX * self.gridY
		self.gridRes = [self.gridX, self.gridY, self.gridZ]
		self.gridLen = self.gridX * self.gridY * self.gridZ
		self.gridCnt = self.gridLen / self.gridLevel
		
		# Make target and state values
		self.targetList = array('f', ones_of(self.gridLen))
		self.currentList = copy(self.targetList)
		self.stateList = array('f', zeros_of(self.gridLen))
		
		
		# Make a new mesh and object for the surface
		self.shapeMesh = bpy.data.meshes.new("Surface")
		self.shapeObject = bpy.data.objects.new('Surface', self.shapeMesh)
		
		self.mesher = SurfaceNetMesher()
		
		scene = context.scene
		scene.objects.link(self.shapeObject)


		# let's get the location of the 3d cursor
		curLoc = bpy.context.scene.cursor_location
		
		 # Make a list of all coordinates
		if useCoords:
			if self.debug:
				print('		- Generating list of coordinates')
			self.coords = SNet_MakeCoords(self.gridLen, self.gridRes)
		elif self.debug:
			print('		- Calculating coordinates live')
		
		
		self.MakeBall()
		#self.MakeStick()
				
		self.GrowShape()
		
		# Testing a function to get points near eacht other
		#self.GetNear(250)

		# Select the new object
		self.shapeObject.select = True
		scene.objects.active = self.shapeObject

		if self.debug:
			now = time.time()
			print('		- Time spent =', str(round((now - self.startTime), 3))+'s')
			print('\n	--- FINISHED SURFACE NET ---\n')
			
		return
	
	
		

	
	
	

	
		
		

		
		
		
		
	# Let's show the growth of our shape!
	def GrowShape(self):
	
		# Do not grow but apply the new shape immediately
		if not self.showGrowth:
			self.currentList = copy(self.targetList)
			self.ApplyShape()
			
		else:
		
			self.growing = True
			
			if self.debug:
				print('		- Starting growthspurt')
				step = 1
		
			# Keep updating the mesh as long as we're growing
			while self.growing:
					
				self.growing = False
				
				for i, target in enumerate(self.targetList):
				
					state = self.stateList[i]
					
					# If this location is growing... we know what to do!
					if state > 0:
						
						# Keep growing!
						if not self.growing:
							self.growing = True
						
						# If we haven't reached the end of the growth cycle...
						if state < self.stateLength:
							
							# Start my neighbours
							if state == self.stateHalf:
								
								near = self.GetGridNear(i, 1)
								
								for n in near:
								
									if self.stateList[n] == 0 and not self.IsGridEnd(n):
										if self.targetList[n] != self.currentList[n]:
											self.stateList[n] = 1
										
								
							dif = self.targetList[i] - self.currentList[i]
							
							dif /= (self.stateLength - state)
							
							self.currentList[i] += dif
							
							self.stateList[i] = state + 1
							
						# If the state has reached its maximum we are done growing
						else:
							
							self.currentList[i] = self.targetList[i]
							self.stateList[i] = 0

					
				if self.debug:
					print('			- Growing step '+str(step))
					step += 1
					
				self.ApplyShape()

		
		
		
	def ApplyShape(self):
	
			# Create the meshed volume
			meshed_volume = self.mesher.mesh_volume(*Volume(dimms = self.gridRes, data = self.currentList))
			
			# Apply the volume data to the mesh
			self.shapeObject.data = mesh_from_data(*meshed_volume)
			
			time.sleep(0.01)
			bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
			#scene_update.go()

		
		

class OpAddSurfaceNet(bpy.types.Operator):
	"""Add a surface net"""
	bl_idname = "mesh.primitive_surface_net"
	bl_label = "Add Surface Net"
	bl_options = {"REGISTER", "UNDO"}
	
	showGrowth = BoolProperty(name='Show Growth', description='Update the scene to show the growth of the form (takes more time and memory)', default=True)
	
	useCoords = BoolProperty(name='Use Coordinate List', description='Use a list of coordinates in stead of calculating every position', default=True)
	
	gridSize = IntProperty(name='Grid Size', default=10, min=0, max=100, soft_min=0, soft_max=1000)
	
	debug = BoolProperty(name='Debug', description='Get timing info in the console', default=True)

	def execute(self, context):
		SNet_Add(context, self.debug, self.gridSize, self.showGrowth, self.useCoords)
		#Net = SurfaceNet(context, self.debug, self.useCoords, self.showGrowth);
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