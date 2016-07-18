'''
UTILITIES

For use in combination with the snet_core
'''
import mathutils, bpy
from copy import copy
from macouno.snet_core import *


# Make coordinates for every point in the volume (not needed if you use GetLocation
def SNet_MakeCoords(len, res):

	coords = []
	
	# Make a coordinate for every point in the volume
	x = y = z = 0
	for i in range(len):
		
		# Should not be a vector yet... we'll do that when retrieving
		coords.append((x, y, z))

		# Go up a level if you move beyond the x or y resolution
		x += 1
		if x == res[0]:
			x = 0
			y += 1
		if y == res[1]:
			y = 0
			z += 1

	return coords
	
	
	
def SNet_GetLocation(position, gridRes):

	res = gridRes
	
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
	
	
	
# Check to see if n is on the border of 
def SNet_IsGridEnd(n, gridX, gridY, gridLevel, gridLen, gridRes):

	# At the bottom level
	if n < gridLevel * 2:
		return True
		
	# At the top level
	elif n >= (gridLen - (gridLevel*2)):
		return True
		
	# Find the position at this level
	lvlPos = (n % gridLevel)
	
	# Now find the position in the gridX
	xPos = lvlPos % gridY
	
	if xPos <= 1 or xPos >= (gridX-2):
		return True
	
	# Clean way to find the y position
	# First discard the x location
	lvlPos -= xPos
	
	# Now divide by the y length
	yPos = lvlPos / gridY
	
	if yPos <= 1 or yPos >= (gridY-2):
		return True

	return False
	
	
	
	
# Limit a value to a global max and minimum
def SNet_LimitValue(n, limitMax, limitMin):
	if n > limitMax:
		return limitMax
	elif n < limitMin:
		return limitMin
	return n
	
	
	
# Make a sphere in the middle of the grid
def SNet_MakeBall(stateList, targetList, gridX, gridY, gridZ, gridLevel, gridLen, limitMax, limitMin, gridRes, coords, useCoords):

	# Let's make a ball within a certain distance from the middle
	middle = mathutils.Vector(((gridX-1)*0.5,(gridY-1)*0.5,(gridZ-1)*0.5))
	'''
	# Option to put an empty at the middle
	bpy.ops.object.empty_add(type='PLAIN_AXES', radius=10.0, view_align=False, location=middle)
	ob = bpy.context.active_object
	ob.name = 'True'
	ob.show_name = False
	'''
	
	for i in range(gridLen):
	
		if not SNet_IsGridEnd(i, gridX, gridY, gridLevel, gridLen, gridRes):
	
			distV = middle - SNet_GetCoord(i, gridRes, useCoords, coords)
			dist = distV.length
			
			val = round((dist -3.0), 2)
			
			if dist < 0.1:
				#val = -1.0
				# SET A STATE!
				print("STARTING POINT",i)
				stateList[i] = 1
			
			targetList[i] = SNet_LimitValue(val, limitMax, limitMin)
				
		# Extra bit that adds empties ont he outer edges
		elif False:
			bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.01, view_align=False, location=SNet_GetCoord(i, gridRes, useCoords, coords))
			ob = bpy.context.active_object
			ob.name = 'True'
			ob.show_name = False
			
	return targetList
	
	

# Grow a stick like shape from the middle out
def SNet_MakeStick(stateList, targetList, gridX, gridY, gridZ, gridLevel):

	# Let's make a ball within a certain distance from the middle
	middle = mathutils.Vector((gridX*0.5, gridY*0.5, gridZ*0.5))
	
	m = SNet_GetGridMiddle(gridX, gridY, gridZ, gridLevel)
	stateList[m] = 1
	targetList[m] = -1
	
	near = []
	near = SNet_GetGridX(m, near, 10, gridX)
	
	for n in near:
		targetList[n] = -1
		
	return targetList


	
# Get the midpoint of the grid
def SNet_GetGridMiddle(gridX, gridY, gridZ, gridLevel):

	xLoc = round(gridX*0.5)
	yLoc = math.floor(gridY*0.5)
	zLoc = math.floor(gridZ*0.5)
	
	zDist = gridLevel * zLoc
	yDist = gridX * yLoc
	
	return xLoc + zDist + yDist



# Get the coord for this point
def SNet_GetCoord(n, gridRes, useCoords, coords):

	if useCoords:
		return mathutils.Vector(coords[n])
	
	return SNet_GetLocation(n, gridRes)



# Get the next and previous items on one axis
def SNet_GetGridX(n, near, steps, gridX):

	if steps < 0:
		for i in range(-(steps)):
			s = i+1
			ns = n-s
			# Haal de volgende op als deze niet aan het begin zit
			if ns > 1 and (ns % gridX) > 1:
				near.append(ns)
			else:
				return near
				
	else:
		
		for i in range(steps):
			ns = (n+1)+i
			# Get the next point if we're not at the end
			if ns % gridX:
				near.append(ns)
			else:
				return near

	return near



# Find the points on the next level
def SNet_GetGridY(n, near, steps, gridX, gridLevel):

	if steps < 0:
	
		for i in range(-(steps)):
			s = (i+1) * gridX
			ns = n - s
			# We want to know the placing on the current level!
			thisLvl = ns % gridLevel
			if thisLvl >= gridX:
				near.append(ns)
			else:
				return near
				
	else:
	
		for i in range(steps):
			s = (i+1) * gridX
			ns = n + s
			thisLvl = ns % gridLevel
			if thisLvl < (gridLevel - gridX):
				near.append(ns)
			else:
				return near
		
	return near



def SNet_GetGridZ(n, near, steps, gridLevel, gridCnt):

	if steps < 0:
	
		for i in range(-(steps)):
			s = (i+1) * gridLevel
			ns = n - s
			thisLvl = math.floor(ns / gridLevel)
			if thisLvl > 1.0:
				near.append(ns)
			else:
				return near
				
	else:
	
		for i in range(steps):
			s = (i+1) * self.gridLevel
			ns = n + s
			thisLvl = math.floor(ns / gridLevel)
			if thisLvl < (gridCnt):
				near.append(ns)
			else:
				return near

	return near



# Get all adjacent points
def SNet_GetGridNear(n, steps, gridX, gridLevel, gridCnt):
	
	near = []

	# Get the next items on this level
	near = SNet_GetGridX(n, near, -steps, gridX)
	near = SNet_GetGridX(n, near, steps, gridX)
	near = SNet_GetGridY(n, near, -steps, gridX, gridLevel)
	near = SNet_GetGridY(n, near, steps, gridX, gridLevel)
	near = SNet_GetGridZ(n,near, -steps, gridLevel, gridCnt)
	near = SNet_GetGridZ(n,near, steps, gridLevel, gridCnt)
	
	return near
	


def SNet_GrowStep(ob):

	# Retrieve the variables we need
	currentList = ob['SNet_currentList']
	targetList = ob['SNet_targetList']
	stateList = ob['SNet_stateList']
	stateLength = ob['SNet_stateLength']
	stateHalf = ob['SNet_stateHalf']
	gridX = ob['SNet_gridX']
	gridY = ob['SNet_gridY']
	gridLevel = ob['SNet_gridLevel']
	gridLen = ob['SNet_gridLen']
	gridRes = ob['SNet_gridRes']
	gridCnt = ob['SNet_gridCnt']
	
	# Stop growing if nothing can be found!
	growing = False
	
	if not ob['SNet_showGrowth']:
		SNet_ApplyShape(ob, gridRes, targetList)
		currentList = [t for t in targetList]
		stateList = [0 for t in targetList]
		
	else:
	
		for i, target in enumerate(targetList):
		
			state = stateList[i]
			
			# If this location is growing... we know what to do!
			if state > 0:
				
				# Keep growing!
				if not growing:
					growing = True
				
				# If we haven't reached the end of the growth cycle...
				if state < stateLength:
					
					# Start my neighbours
					if state == stateHalf:
						
						near = SNet_GetGridNear(i, 1, gridX, gridLevel, gridCnt)
						
						for n in near:
						
							if stateList[n] == 0:
								if targetList[n] != currentList[n]:
									stateList[n] = 1
								
						
					dif = targetList[i] - currentList[i]
					
					dif /= (stateLength - state)
					
					currentList[i] += dif
					
					stateList[i] = state + 1
					
				# If the state has reached its maximum we are done growing
				else:
					
					currentList[i] = targetList[i]
					stateList[i] = 0
		
		if growing:
			SNet_ApplyShape(ob, gridRes, currentList)
	
	ob['SNet_growing'] = growing
	ob['SNet_currentList'] = currentList
	ob['SNet_stateList'] = stateList



def SNet_ApplyShape(shapeObject, gridRes, currentList):

	mesher = SurfaceNetMesher()
	
	dot = Volume(data=array('f', [
	
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0,
	
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0,
	
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, -1.0, 1.0,
	1.0, 1.0, 1.0, 1.0,
	
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0
	
	]), dimms=[4, 4, 4])
	
	dot = create_torus()
	dot = create_sphere()
	
	print(dot)
	
	# Create the meshed volume
	meshed_volume = mesher.mesh_volume(*Volume(dimms = gridRes, data = currentList))
	#meshed_volume = mesher.mesh_volume(*dot)
	
	# Apply the volume data to the mesh
	shapeObject.data = mesh_from_data(*meshed_volume)
	
	#time.sleep(0.01)
	#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=2)
	#scene_update.go()