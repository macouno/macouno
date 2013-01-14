import mathutils, math



# A bezier curve (used for falloff based transforms)
class curve():


	# Initialise the class
	def __init__(self, falloff='LIN', mode='inc'):
	
		# The falloff and mode settings
		self.falloff = falloff
		self.mode = mode # mode is inc, mult or val
		
		# Kappa is the position of the handle on a circular curve
		# Not used right now but very handy to keep around
		self.kappa = ((math.sqrt(2)-1)/3)*4
	
		# Get the curve coordinates (depending on falloff and mode)
		self.setShape()
		
		# Current values (between 0.0 and 1.0)
		self.currentY = False
		self.currentX = False
		
		# New values (between 0.0 and 1.0)
		self.newY = False
		self.newX = False
		
		self.startVal = False
		self.currentVal = False
		self.endVal = False
		
		
		
	def update(self, startVal=0.0, currentVal=0.0, endVal=1.0, currentX=0.0, newX=0.0):
	
		self.startVal = startVal
		self.currentVal = currentVal
		self.endVal = endVal
		
		if currentX > 1.0:
			currentX = 1.0
		if newX > 1.0:
			newX = 1.0
		
		self.getCurrentVals(currentX, newX)
	
		if self.mode == 'inc':
			self.getIncrease()
		elif self.mode == 'val':
			self.getValue()
		elif self.mode == 'mult':
			self.getMultiplier()
			
		
		
	# Get a new value based on the current one, end one and the curve position (for colour)
	def getValue(self):
	
		currentGap = self.endVal - self.currentVal
		currentGapFac = 1.0 - self.currentY
		
		dif = currentGap / currentGapFac
		
		newGapFac = 1.0 - self.newY
		newGap = dif * newGapFac
		
		self.currentVal= self.endVal - newGap
	
	
	
	# Get a multiplier (for scaling)
	def getMultiplier(self):
	
		# The ultimate multiplier is the endval (it's relative)!
		dif = self.endVal - self.startVal
		
		if self.currentY < 0.0:
			self.currentY = 1.0 / ((abs(self.currentY) * dif) + 1)
		else:
			self.currentY *= dif
			self.currentY += 1.0
		
		if self.newY < 0.0:
			self.newY = 1.0 / ((abs(self.newY) * dif) + 1)
		else:
			self.newY *= dif
			self.newY += 1.0	
		
		if not self.currentY:
			self.currentVal = self.newY
		else:
			self.currentVal = self.newY / self.currentY
		
		
		'''
		if self.currentY < 0.0:
			self.currentY = 1.0 / ((abs(self.currentY) * dif) + 1)
		else:
			self.currentY *= dif
			self.currentY += 1.0
		
		if self.newY < 0.0:
			self.newY = 1.0 / ((abs(self.newY) * dif) + 1)
		else:
			self.newY *= dif
			self.newY += 1.0
			
		print('1 curY',self.currentY,'newY',self.newY)
		
		# Can not divide by zero!
		if not self.currentY:
			self.currentVal = self.newY
			return
			
		self.currentVal = self.newY / self.currentY
		'''
	
	
	
	# Get a Linear value (for translation/rotation)
	def getIncrease(self):
	
		# We get the difference in scale so we can figure out each step
		dif = self.endVal - self.startVal
		
		self.currentVal =  self.newY - self.currentY
		self.currentVal *= dif
		
		
		
	# Get the x and Y values for the curve (to get relative offset later)
	def getCurrentVals(self, currentX=0.0, newX=0.0):
	
		if self.currentY is False or not self.currentX == currentX:
			self.currentX = currentX
			self.currentY = self.findYPos(currentX)
			
		if self.newY is False or not self.newX == newX:
			self.newX = newX
			self.newY = self.findYPos(newX)
		
		
		
	# Find the offset on a curve
	def findYPos(self, xPos):
	
		roundPos = round(xPos,5)
	
		# GO find the  current value
		for j, node in enumerate(self.curve):
		
			roundNode = round(node['node'][0],5)
			
			# Find the node that ends after or at the new point
			if  j and roundNode >= roundPos:
			
				p0 = self.curve[(j-1)]['node']
				p1 = self.curve[(j-1)]['handle_right']
				
				p2 = node['handle_left']
				p3 = node['node']
				
				# Get the length of the current spline
				splineStart = p0[0]
				splineEnd = p3[0]
				splineLength = splineEnd - splineStart
				
				# Find the points relative to the current spline
				xPos = (xPos - splineStart) / splineLength
				
				# Find the point on the curve for the previous iteration in the loop
				val = self.findPoint(xPos, p0, p1, p2, p3)
				
				# This should tell us what the current Y position is
				yPos = val[1]
				
				return yPos
				
				
				
	# Find a point along a bezier curve
	# r = a point between 0 and 1
	# curve is a dict with four 2d vectors p0,p1,p2,p3
	def findPoint(self, r, p0,p1,p2,p3):
		c = 3 * (p1 - p0)
		b = 3 * (p2 - p1) - c
		a = p3 - p0 - c - b

		r2 = r * r
		r3 = r2 * r

		return a * r3 + b * r2 + c * r + p0
		
		
		
	# Make the default bezier curves
	def setShape(self):
			
		# Linear
		if self.falloff == 'LIN':
			self.curve =  [{'handle_left': mathutils.Vector((-0.33333, -0.33333)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.33333, 0.33333))},{'handle_left': mathutils.Vector((0.66667, 0.66667)), 'node': mathutils.Vector((1.0, 1.0)), 'handle_right': mathutils.Vector((1.33333, 1.33333))}]
			
		# Increasing
		elif self.falloff == 'INC': 
			self.curve =  [{'handle_left': mathutils.Vector((-0.24042, 0.0)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.55228, 0.0))},{'handle_left': mathutils.Vector((1.0, 0.44772)), 'node': mathutils.Vector((1.0, 1.0)), 'handle_right': mathutils.Vector((1.0, 1.34))}]
			
		# Decreasing
		elif self.falloff ==  'DEC':
			self.curve =  [{'handle_left': mathutils.Vector((0.0, -1.0)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.0, 0.55228))},{'handle_left': mathutils.Vector((0.44772, 1.0)), 'node': mathutils.Vector((1.0,1.0)), 'handle_right': mathutils.Vector((1.34, 1.0))}]
			
		# Swoosh
		elif self.falloff == 'SWO':
			self.curve =  [{'handle_left': mathutils.Vector((-1.0, 0.0)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.55228, 0.0))},{'handle_left': mathutils.Vector((0.44772, 1.0)), 'node': mathutils.Vector((1.0,1.0)), 'handle_right': mathutils.Vector((1.34, 1.0))}]
			
		# Spike
		elif self.falloff == 'SPI':
			if self.mode == 'mult':
				self.curve =  [{'handle_left': mathutils.Vector((-0.5, 0.0)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.27614, 0.0))},{'handle_left': mathutils.Vector((0.5, 0.44772)), 'node': mathutils.Vector((0.5, 1.0)), 'handle_right': mathutils.Vector((0.5, 0.44772))},{'handle_left': mathutils.Vector((0.72386, 0.0)), 'node': mathutils.Vector((1.0, 0.0)), 'handle_right': mathutils.Vector((1.25, 0.0))}]
			
			else:
				self.curve =  [{'handle_left': mathutils.Vector((-0.5, 0.0)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.27614, 0.0))},{'handle_left': mathutils.Vector((0.5, 0.22386)), 'node': mathutils.Vector((0.5, 0.5)), 'handle_right': mathutils.Vector((0.5, 0.22386))},{'handle_left': mathutils.Vector((0.72386, 0.0)), 'node': mathutils.Vector((1.0, 0.0)), 'handle_right': mathutils.Vector((1.25, 0.0))}]
			
		# Bump
		elif self.falloff == 'BUM':
			if self.mode == 'mult':
				self.curve =  [{'handle_left': mathutils.Vector((0.0, -0.5)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.0, 0.55228))},{'handle_left': mathutils.Vector((0.22386, 1.0)), 'node': mathutils.Vector((0.5,1.0)), 'handle_right': mathutils.Vector((0.77614, 1.0))},{'handle_left': mathutils.Vector((1.0, 0.55228)), 'node': mathutils.Vector((1.0,0.0)), 'handle_right': mathutils.Vector((1.0, -0.5))}]
				
			else:
				self.curve =  [{'handle_left': mathutils.Vector((0.0, -0.25)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.0, 0.27614))},{'handle_left': mathutils.Vector((0.22386, 0.5)), 'node': mathutils.Vector((0.5,0.5)), 'handle_right': mathutils.Vector((0.77614, 0.5))},{'handle_left': mathutils.Vector((1.0, 0.27614)), 'node': mathutils.Vector((1.0,0.0)), 'handle_right': mathutils.Vector((1.0, -0.25))}]
				
		# Sweep
		elif self.falloff == 'SWE':
			if self.mode == 'mult':
				self.curve =  [{'handle_left': mathutils.Vector((-0.25, 0.0)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.27614, 0.0))},{'handle_left': mathutils.Vector((0.22386, 1.0)), 'node': mathutils.Vector((0.5, 1.0)), 'handle_right': mathutils.Vector((0.77614, 1.0))},{'handle_left': mathutils.Vector((0.72386, 0.0)), 'node': mathutils.Vector((1.0, 0.0)), 'handle_right': mathutils.Vector((1.25, 0.0))}]
				
			else:
				self.curve =  [{'handle_left': mathutils.Vector((-0.25, 0.0)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.27614, 0.0))},{'handle_left': mathutils.Vector((0.22386, 0.5)), 'node': mathutils.Vector((0.5, 0.5)), 'handle_right': mathutils.Vector((0.77614, 0.5))},{'handle_left': mathutils.Vector((0.72386, 0.0)), 'node': mathutils.Vector((1.0, 0.0)), 'handle_right': mathutils.Vector((1.25, 0.0))}]
		
		# None as default, but should never be used
		else:
			self.curve =  [{'handle_left': mathutils.Vector((-0.33333, 0.0)), 'node': mathutils.Vector((0.0, 0.0)), 'handle_right': mathutils.Vector((0.33333, 0.0))},{'handle_left': mathutils.Vector((0.66667, 0.0)), 'node': mathutils.Vector((1.0, 0.0)), 'handle_right': mathutils.Vector((1.33333, 0.0))}]