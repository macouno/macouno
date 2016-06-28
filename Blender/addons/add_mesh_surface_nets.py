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

def SNet_Add(context, debug):

	# Make a new mesh and object for the surface
	me = bpy.data.meshes.new("Surface")
	ob = bpy.data.objects.new('Surface', me)
	
	scn = context.scene
	scn.objects.link(ob)
	
	ob.select = True
	scn.objects.active = ob
	
	# Make some variables for the object
	ob.SNet_enabled = True
	ob['SNet_debug'] = debug
	ob['SNet_growSpeed'] = 0.05
	ob['SNet_stateLength'] = 100
	
	ob['SNet_gridSize'] = mathutils.Vector((10.0,10.0,10.0))
	

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
			self.coords = self.MakeCoords(self.gridLen, self.gridRes)
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

		
		
	# Make a sphere in the middle of the grid
	def MakeBall(self):
	
		# Let's make a ball within a certain distance from the middle
		middle = mathutils.Vector((self.gridX*0.5,self.gridY*0.5,self.gridZ*0.5))
		
		for i in range(self.gridLen):
		
			distV = middle - self.GetCoord(i)
			dist = distV.length
			
			val = self.LimitValue(round(dist - 5, 2))
			
			if dist < 0.1:
				
				# SET A STATE!
				print("STARTING POINT")
				self.stateList[i] = 1
			
			if val != self.limitMax:
			
				#self.stateList[i] = 1.0
				self.targetList[i] = val
				
				
		
	def MakeStick(self):
	
		# Let's make a ball within a certain distance from the middle
		middle = mathutils.Vector((self.gridX*0.5,self.gridY*0.5,self.gridZ*0.5))
		
		m = self.GetGridMiddle()
		self.stateList[m] = 1
		self.targetList[m] = -1
		
		near = []
		near = self.GetGridX(m, near, 10)
		
		for n in near:
			self.targetList[n] = -1
	
	
		
	# Get the midpoint of the grid
	def GetGridMiddle(self):
	
		xLoc = round(self.gridX*0.5)
		yLoc = math.floor(self.gridY*0.5)
		zLoc = math.floor(self.gridZ*0.5)
		
		zDist = self.gridLevel * zLoc
		yDist = self.gridX * yLoc
		
		return xLoc + zDist + yDist
	
	
	
	# Check to see if n is on the border of 
	def IsGridEnd(self, n):
	
		# At the bottom level
		if n < (self.gridLevel-1):
			return True
			
		# At the top level
		elif n > ((self.gridLen-self.gridLevel)-1):
			return True
			
		# Find the position at this level
		lvlPos = n % self.gridLevel
		
		# Now find the position in the gridY
		xPos = lvlPos % self.gridY
		
		if xPos <= 0 or xPos >= (self.gridX-1):
			return True
		
		yPos = lvlPos - xPos
		if yPos > 0:
			yPos = self.gridLevel / yPos
		
		if yPos <= 0 or yPos >= (self.gridY-1):
			return True
		
		return False
	
		
		
	# Get the next and previous items on one axis
	def GetGridX(self, n, near, steps):

		if steps < 0:
			for i in range(-(steps)):
				s = i+1
				ns = n-s
				# Haal de volgende op als deze niet aan het begin zit
				if ns > 1 and (ns % self.gridX) > 1:
					near.append(ns)
				else:
					return near
					
		else:
			
			for i in range(steps):
				ns = (n+1)+i
				# Get the next point if we're not at the end
				if ns % self.gridX:
					near.append(ns)
				else:
					return near

		return near

		
		
	# Find the points on the next level
	def GetGridY(self, n, near, steps):
	
		if steps < 0:
		
			for i in range(-(steps)):
				s = (i+1) * self.gridX
				ns = n - s
				# We want to know the placing on the current level!
				thisLvl = ns % self.gridLevel
				if thisLvl >= self.gridX:
					near.append(ns)
				else:
					return near
					
		else:
		
			for i in range(steps):
				s = (i+1) * self.gridX
				ns = n + s
				thisLvl = ns % self.gridLevel
				if thisLvl < (self.gridLevel - self.gridX):
					near.append(ns)
				else:
					return near
			

		'''
		# Add the previous row
		Np = n - self.gridX
		if Np > 0 :
			near.append(Np)
			near = self.GetGridX(Np, near, -steps)
			near = self.GetGridX(Np, near, steps)
		
		# Add the next row
		Np = n + self.gridX
		if Np < (self.gridLen-1):
			near.append(Np)

			near = self.GetGridX(Np, near, -steps)
			near = self.GetGridX(Np, near, steps)
		'''
		return near
		
	
	
	def GetGridZ(self, n, near, steps):
	
		if steps < 0:
		
			for i in range(-(steps)):
				s = (i+1) * self.gridLevel
				ns = n - s
				thisLvl = math.floor(ns / self.gridLevel)
				if thisLvl > 1.0:
					near.append(ns)
				else:
					return near
					
		else:
		
			for i in range(steps):
				s = (i+1) * self.gridLevel
				ns = n + s
				thisLvl = math.floor(ns / self.gridLevel)
				if thisLvl < (self.gridCnt):
					near.append(ns)
				else:
					return near
		'''
		nearUp = False
		nearDown = False
				
		# Get the items a level up from current
		if n > 0 and n < ((self.gridLen - (self.gridLevel*2))-1) :
		
			nearUp = copy(near)	
			for i,m in enumerate(nearUp) :
				nearUp[i] += self.gridLevel
				
			nearUp.append(n + self.gridLevel)
			
			
		# Get the items a down from current
		if False and n > (self.gridLevel*2)-1: 
			
			nearDown = copy(near)
			for i,m in enumerate(nearDown):
				nearDown[i] -= self.gridLevel
			nearDown.append(n - self.gridLevel)
			
		if nearUp:
			near += nearUp
		if nearDown:
			near += nearDown
		'''
		return near
	
	
		
	# Get all adjacent points
	def GetGridNear(self, n, steps):
		
		near = []

		# Get the next items on this level
		near = self.GetGridX(n, near, -steps)
		near = self.GetGridX(n, near, steps)
		near = self.GetGridY(n, near, -steps)
		near = self.GetGridY(n, near, steps)
		near = self.GetGridZ(n,near, -steps)
		near = self.GetGridZ(n,near, steps)
		
		return near
		
		
		
	# Get the coord for this point
	def GetCoord(self, n):

		if self.useCoords:
			return self.coords[n]
		
		return self.GetLocation(n)
		
		
		
	# Limit a value to a global max and minimum
	def LimitValue(self, n):
		if n > self.limitMax:
			return self.limitMax
		elif n < self.limitMin:
			return self.limitMin
		return n
		
		
		
		
	# Get the location at a specific position in the grid
	def GetLocation(self, position):

		res = self.gridRes
		
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
		SNet_Add(context, self.debug)
		#Net = SurfaceNet(context, self.debug, self.useCoords, self.showGrowth);
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