import bpy, bmesh, mathutils, math
from macouno import misc, falloff_curve, bmesh_extras, scene_update



# Find the next vert and place it the correct nr of degrees clockwise around the midpoint
def loop_step(v1,loopVerts, step,outEdges, center, dVec):

	#Check both edges connected to this one
	for e in v1.link_edges:
		
		# We only go for the edge on the outside....
		if e in outEdges:
		
			if v1 == e.verts[0]:
				v2 = e.verts[1]
			else:
				v2 = e.verts[0]
				
			v1co = v1.co - center
			v2co = v2.co - center
		
			if dVec is False:
				dVec = v2co - v1co
				
			relVec = v2co - v1co
				
			# If the dot is negative... we're moving back along the circle and we invert the step (move the vert toward the previous one in stead of away from it)
			dot = relVec.dot(dVec)
			
			#print(len(outEdges),'dot',dot)
			
			if dot < 0.0:
				v2co =  misc.rotate_vector_to_vector(v1co, v2co, step)
			else:
				v2co =  misc.rotate_vector_to_vector(v2co, v1co, step)
				
			# Put the vert in the right position
			v2.co = v2co + center
			
			# Remove the edge from the list of outer edges.... no lnoger needed
			outEdges.remove(e)
			loopVerts.append(v2)
			
			dVec = v2co - v1co
			outEdges, loopVerts = loop_step(v2, loopVerts, step, outEdges, center, dVec)
			
			break
			
	return outEdges, loopVerts

	

# Casting loops is cool... hopefully it works well in bmesh! Yaya
# Scale can be a nr between 0.01 and 100.0
# Scale falloff should be a curve shape. ('STR', 'Straight',''),('SPI', 'Spike',''),('BUM', 'Bump',''),('SWE', 'Sweep',''),
# corner_group = Name of a group you want all corners to be added to
def cast(bme=None, corners=0, falloff_scale=1.0, falloff_shape='STR',corner_group=None,redraw=False):

	if not bme:
		bm = bmesh_extras.get_bmesh()
	else:
		bm = bme
		
	print(corners, falloff_scale, falloff_shape)
		
	# Get a heap of lists to work with later!
	selFaces = bmesh_extras.get_selected_faces(bm)
	selVerts = bmesh_extras.get_selected_verts(bm)
	outVerts = bmesh_extras.get_outer_verts(selFaces)
	outEdges = bmesh_extras.get_outer_edges(selFaces)
	cent = bmesh_extras.get_vert_center(selVerts )
	normal = bmesh_extras.get_normal(selFaces)
	inVerts = []
	
	if len(outVerts):
	
		# Let's quickly make a list of inner verts
		for v in selVerts:
			if not v in outVerts:
				inVerts.append(v)
				
		# make a quaternion and a matrix representing this "plane"
		quat = normal.to_track_quat('-Z', 'Y')
		mat = quat.to_matrix()

		# Put all the verts in the plane...
		# And.. find out for each vert how far it is along the normal
		# Ang get the average distance from the center point
		midDist = 0.0
		for v in selVerts:
			relPos = (v.co - cent)
			relDot = normal.dot(relPos)
			
			v.co += (normal * (-relDot))
			# If this is an outerVert... then we keep track of it's distance from the center
			if v in outVerts:
				midDist += relPos.length
		
		
		# The medium distance from the center point
		midDist /= len(outVerts) 
		
		# now lets put them all the right distance from the center
		top = False
		topVert = False
		for i,v in enumerate(outVerts):
			relPos = v.co - cent
			relPos = relPos.normalized() * midDist
			v.co = relPos + cent
			
			# Find the top vert for nice alignment of the shape (start the steploop here)
			if top is False or v.co[2] > top:
				top = v.co[2]
				topVert = i

		
		# As a final step... we want them to be rotated neatly around the center...
		step = math.radians(360) / (len(outEdges))
		

		# Now that we found the top vert we can start looping through to put them in the right position
		loopVerts = [outVerts[topVert]]
		outEdges, loopVerts = loop_step(outVerts[topVert],loopVerts,step,outEdges,cent,False)
		
		# Set corner group weight to 0.0 because the shape is a circle (will be reset to 1.0 later for the actual corners)
		if corner_group:
			bm, group_index = add_to_group(bme=bm,verts=outVerts, newGroup=False, groupName=corner_group, weight=0.0)
		
		
		if corners:
		
			# Initiate a list of all corner verts so we can set the weight accordingly later (best done in one move)
			cornerVerts = []
			
			c = round((360.0 / corners),2)
			a = (180.0 - c) * 0.5
			
			stepLen = math.ceil(len(outVerts) / corners)
			
			#print('stepLen', stepLen)
			
			aLine = False
			
			currentX = 0.0
			vec = falloff_scale
			factor = 1.0
			curve = falloff_curve.curve(falloff_shape, 'mult')
			
			loopCnt = len(loopVerts)
			cornerCnt = math.floor(loopCnt / corners)
			
			#print('\n',loopCnt,cornerCnt)
			
			
			for i, v in enumerate(loopVerts):
			
				
				#if(i>9):
				#	return
					
				stepPos = i % stepLen
				
				#print(i,'stepPos',stepPos)
				
				# Get a normalized version of the current relative position
				line = mathutils.Vector(v.co - cent).normalized()
				
				# Get the starting line as a reference (is also a corner
				if not aLine:
					aLine = line
					currentX = 0.0
					factor = 1.0
					
					#if corner_group: corner_group.add([v.index], 1.0, 'REPLACE')
					if corner_group:
						cornerVerts.append(v)
					
				else:
				
					# Find the angle from the current starting line
					cAng = round(math.degrees(aLine.angle(line)),2)
					#print('ang',cAng,c,(cAng >= c))
					
					# If the angle is bigger than a step, we make this the new start
					if cAng >= c:
					
						#print('found corner')
					
						#if corner_group: corner_group.add([v.index], 1.0, 'REPLACE')
						if corner_group:
							cornerVerts.append(v)
						
						# Make sure the angle is correct!
						line =  misc.rotate_vector_to_vector(line, aLine, math.radians(c))
						v.co = (line * midDist) + cent
						aLine = line
						
						currentX = 0.0
						factor = 1.0
						
					# These should all be midpoints along the line!
					# make sure we don't do the last one... because it's the first one!
					else:
					
						# Remove non corner items from the corner group
						#if corner_group: corner_group.remove([v.index])
						
						# Only if we have to scale and the line isn't straight!
						if falloff_scale != 1.0 and falloff_shape != 'STR':
						
							# Find out how far we are from the start as a factor (fraction of one?)
							angFac = cAng / c
							newX = angFac
							
							# Create a nice curve object to represent the falloff
							
							curve.update(1.0, 0.0, vec, currentX, newX)
							
							fac = abs(curve.currentVal)
							
							factor *= fac
							
							currentX = newX
							
						# Find the corner of the new triangle
						b = 180 - (a+cAng)
						
						# find the distance from the midpoint
						A = math.sin(math.radians(a)) / (math.sin(math.radians(b))/midDist)
						
						bLine = line * A
						
						bLine *= factor
						
						v.co = bLine + cent
				
				if redraw:
					scene_update.go(False, 'RED')
				
			if len(cornerVerts):
				bm, group_index = add_to_group(bme=bm,verts=cornerVerts, newGroup=False, groupName=corner_group, weight=1.0)
				
		# I want to make sure these verts are inside the loop!
		# So we move all verts halfway towards the center before smoothing (neat results in entoforms)
		for v in inVerts:
			relPos = cent - v.co
			v.co += (relPos * 0.5)

		#for i in range(100):
		# SMOOTH THE VERTS MAN!!!
		bmesh_extras.smooth_verts(verts=inVerts,loops=10)
		#bmesh.ops.smooth_vert(bm, verts=inVerts,use_axis_x=True, use_axis_y=True, use_axis_z=True)

				
	if not bme:
		bmesh_extras.put_bmesh(bm)
	else:
		return bm