'''
UTILITIES

For use in combination with the snet_core
'''
import mathutils



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
	
	
	
# Check to see if n is on the border of 
def SNet_IsGridEnd(n, gridX, gridY, gridLevel, gridLen):

	# At the bottom level
	if n < (gridLevel-1):
		return True
		
	# At the top level
	elif n > ((gridLen - gridLevel)-1):
		return True
		
	# Find the position at this level
	lvlPos = n % gridLevel
	
	# Now find the position in the gridY
	xPos = lvlPos % gridY
	
	if xPos <= 0 or xPos >= (gridX-1):
		return True
	
	yPos = lvlPos - xPos
	if yPos > 0:
		yPos = gridLevel / yPos
	
	if yPos <= 0 or yPos >= (gridY-1):
		return True
	
	return False
	
	
	
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
	
	

# Make coordinates for every point in the volume (not needed if you use GetLocation
def SNet_MakeCoords(len, res):
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
	
	
	
# Limit a value to a global max and minimum
def SNet_LimitValue(n, limitMax, limitMin):
	if n > limitMax:
		return limitMax
	elif n < limitMin:
		return limitMin
	return n
	
	
	
# Make a sphere in the middle of the grid
def SNet_MakeBall(stateList, targetList, gridX, gridY, gridZ, gridLen, limitMax, limitMin, gridRes, coords, useCoords):

	# Let's make a ball within a certain distance from the middle
	middle = mathutils.Vector((gridX*0.5,gridY*0.5,gridZ*0.5))
	
	for i in range(gridLen):
	
		distV = middle - SNet_GetCoord(i, gridRes, useCoords, coords)
		dist = distV.length
		
		val = SNet_LimitValue(round(dist - 5, 2), limitMax, limitMin)
		
		if dist < 0.1:
			
			# SET A STATE!
			print("STARTING POINT")
			stateList[i] = 1
		
		if val != limitMax:
		
			#self.stateList[i] = 1.0
			targetList[i] = val
			
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
	
	
	
# Get the location at a specific position in the grid
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
