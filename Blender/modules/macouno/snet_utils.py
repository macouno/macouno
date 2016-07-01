'''
UTILITIES

For use in combination with the snet_core
'''
import mathutils


def SNet_GetCoord(n, coords, useCoords):

	if useCoords:
		return coords[n]
	
	return SNet_GetLocation(n)
	
	
	
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
	
	
	
# Make a sphere in the middle of the grid
def SNet_MakeBall(gridX, gridY, gridZ, gridLen):

	# Let's make a ball within a certain distance from the middle
	middle = mathutils.Vector((gridX*0.5,gridY*0.5,gridZ*0.5))
	
	for i in range(gridLen):
	
		distV = middle - SNet_GetCoord(i)
		dist = distV.length
		
		val = self.LimitValue(round(dist - 5, 2))
		
		if dist < 0.1:
			
			# SET A STATE!
			print("STARTING POINT")
			self.stateList[i] = 1
		
		if val != self.limitMax:
		
			#self.stateList[i] = 1.0
			self.targetList[i] = val