import bpy, bmesh, mathutils, math
from macouno import misc, falloff_curve


# Get the bmesh data from the current mesh object
def get_bmesh():
	
	# Get the active mesh
	ob = bpy.context.active_object
	me = ob.data

	# Get a BMesh representation
	if ob.mode == 'OBJECT':
		bm = bmesh.new()
		bm.from_mesh(me)   # fill it in from a Mesh
	else:
		bm = bmesh.from_edit_mesh(me) # Fill it from edit mode mesh
	
	return bm
	
	
	
# Put the bmesh data back into the current mesh object
def put_bmesh(bm):
	
	# Get the active mesh
	ob = bpy.context.active_object
	me = ob.data
	
	# Flush selection
	bm.select_flush_mode() 
	
	# Finish up, write the bmesh back to the mesh
	if ob.mode == 'OBJECT':
		bm.to_mesh(me)
		bm.free()
	else:
		bmesh.update_edit_mesh(me, True)
		
		
		
		
# Get a list of all selected faces
def get_selected_faces(bm):
		
	return [f for f in bm.faces if f.select]
		
		
		
# Get a list of all selected faces
def get_selected_verts(bm):
		
	return [v for v in bm.verts if v.select]

	

# See if a  bmesh has any selected faces at all (make sure you return as soon as you find one)
def has_selected(bm):
	for f in bm.faces:
		if f.select:
			return True
	return False
	
	
	
# Crease all edges sharper than 60 degrees (1 radians-ish)
def crease_edges(sharpness='', limit=1.0, group=None):
	
	bm = get_bmesh()
	
	# Get the crease custom data layer or make one if it doesn't exist
	crease_lay = bm.edges.layers.crease.active
	if crease_lay is None: crease_lay = bm.edges.layers.crease.new()
	
	# Create edge creases based on a group
	if group:
		try:
			gi = bpy.context.active_object.vertex_groups[group].index
		except:
			gi = False
			
	if gi:
	
		# Get the customdata layer with vertex group information
		group_lay = bm.verts.layers.deform.active
		if group_lay is None: group_lay = bm.verts.layers.deform.new()
		
		# Go through all edges
		for e in bm.edges:
		
			# See if both verts on this edge are in the corner group
			fnd = 0
			for v in e.verts:
				if gi in v[group_lay]:
					fnd += 1
					
			if fnd ==  2:
				e[crease_lay] = sharpness
			else:
				e[crease_lay] = 0.0				
				
	# If there's no group we use edge angle
	else:
		for e in bm.edges:
			if e.select:
				if e.calc_face_angle() > limit:
					e[crease_lay] = sharpness
				else:
					e[crease_lay] = 0.0
	
	put_bmesh(bm)
	
	
	
# See if a face is on the outside of your selection
def is_outer_face(face, faces):
	for v in face.verts:
		# Check all connected faces
		for f in v.link_faces:
			if not f == face and f in faces:
				return True
	return False
	
	
	
# See if a specific vert is on the outside of a list of faces (connected to a face not in the list)
def is_outer_vert(vert, faces):
	for f in vert.link_faces:
		if not f in faces:
			return True
	return False
	
	
	
# Find all faces on the outside of the current selection (connected to a non-selected face)
def get_outer_faces(faces):
	
	outFaces = []
	for f1 in faces:
		found = False
		for v in f1.verts:
			if found: break
			
			# Check all connected faces
			for f2 in v.link_faces:
				if not f2 == f1 and not f2 in faces:
					outFaces.append(f1)
					found =True
					break
					
	return outFaces
	
	
	
# Get the verts on the outside of your selection
def get_outer_verts(faces):
	
	outVerts = []
	for f1 in faces:
	
		for v in f1.verts:
			if not v in outVerts:
			
				# Check all connected faces
				for f2 in v.link_faces:
					if not f2 in faces:
						outVerts.append(v)
						break
					
	return outVerts	
	
	
	
# Get the verts on the outside of your selection
def get_outer_edges(faces):
	
	outEdges = []
	for f1 in faces:
		for e in f1.edges:
			if not e in outEdges:
			
				 # Both the edge's verts should be connected to a non selected face
				outFound = False
				for v in e.verts:
					if outFound is False:
						for f2 in v.link_faces:
							if not f2 in faces:
								if outFound is False:
									outFound = []
								outFound.append(f2)
					else:
						for f2 in v.link_faces:
							if f2 in outFound:
								outFound = True
								break
					
				if outFound is True:
					outEdges.append(e)
					
	return outEdges
	
	
	
# Get the center point of a list of faces
def get_center(faces):
	
	c = mathutils.Vector()
	cnt = 0
	
	for f in faces:
		c += f.calc_center_bounds()
		cnt += 1
			
	return c / cnt	
	
	
	
# Get the normal of a list of faces
def get_normal(faces):
	
	c = mathutils.Vector()
	
	for f in faces:
		c += f.normal
			
	return c.normalized()
			
	
	
# Find a corner in a list of faces
def get_corners(faces=None,preferred=None):
	
	if faces:
	
		vertList = [v.index for f in faces for v in f.verts]
		corners = []
								
		# Find all faces with a vert that isn't shared with any others
		for f1 in faces:

			for v1 in f1.verts:
					
				# If this vert is only in the selected verts once... it must be an outer corner
				if vertList.count(v1.index) == 1:
					
					# Now see if the vert is connected to a preferred face
					pref = False
					for v2 in f1.verts:
						if pref: break
						
						for f2 in v2.link_faces:
							if f2 in preferred:
								pref =True
								break

					# If the corner is connected to a preferred face it is inserted at the start of the list
					if pref:
						corners.insert(0, f1)
					else:
						corners.append(f1)
					
					break
				
		if len(corners):
			return corners
		
	return False


	
# Get a cluster starting with a specific face	
def get_cluster(face=None, faces=None, limit=8):

	clusterFaces = [face]
	clusterVerts = [v.index for v in face.verts]
	clusterEdges = [e.index for e in face.edges]
	addedFace = True
	lastConnect = 0
	
	# As long as we haven't reached the limit and keep adding faces... keep going
	while len(clusterFaces) < limit and addedFace:
	
		addedFace = False
		biggestFace = False
		biggestConnection = False
		biggestEdge = False
	
		# Loop through all faces to check the connections
		for f in faces:
			if not f in clusterFaces:
				
				# Count all verts and edges connecting this face to the cluster
				connectCount = 0

				for e in f.edges:
					connectCount += clusterEdges.count(e.index)
					
				for v in f.verts:
					connectCount += clusterVerts.count(v.index)
			
				# OK... so We want more and more connections... because that means we loop around nicely, but if the previous connection was 7 we can start fresh
				if connectCount and (connectCount > lastConnect or lastConnect >= 7):
					if biggestFace is False or connectCount > biggestConnection or (connectCount == biggestConnection and is_outer_face(f, faces)):
						biggestFace = f
						biggestConnection = connectCount
		
		# if we found a face that is connected well add it, and it's verts n edges to the cluster
		if biggestFace:
			addedFace = True
			lastConnect = biggestConnection
			clusterFaces.append(biggestFace)
			for v in biggestFace.verts:
				clusterVerts.append(v.index)
			for e in biggestFace.edges:
				clusterEdges.append(e.index)

	return clusterFaces
	
	
	
# Add a faces in a list to a vertex group
def add_to_group(bme=None, faces=None, newGroup=True, groupName='group'):
		
	if not bme:
		bm = get_bmesh()
	else:
		bm = bme
	
	# If no faces are supplied make a new list from the selection
	if not faces:
		faces = [f for f in bm.faces if f.select]
		
	dvert_lay = bm.verts.layers.deform.active
	if dvert_lay is None: dvert_lay = bm.verts.layers.deform.new()
	
	# Create a new vertex group if required
	if newGroup:
		group = bpy.context.active_object.vertex_groups.new(groupName)
		group_index = group.index
	else:
		# Try to retrieve the vertex group, and if we can't make a new one anyway
		try:
			group_index = bpy.context.active_object.vertex_groups[groupName]
		except:
			group = bpy.context.active_object.vertex_groups.new(groupName)
			group_index = group.index
	
	# Put all verts of the faces in this group!
	for f in faces:
		for v in f.verts:
			v[dvert_lay][group_index] =1.0
			
	if not bme:
		put_bmesh(bm)
		return group_index
	else:
		return bm, group_index
	
	
	
# Take the current selection and make a series of vertex groups for it
def cluster_selection(limit=8,groupName='cluster'):
	
	bm = get_bmesh()
	newGroups = []
	
	# Get all selected faces
	selFaces = [f for f in bm.faces if f.select]

	cornerCounter = 0
	faceCounter = 0
	cluster = []
	
	# Try to use up all selected faces (break gets us out if no more options are found)
	while len(selFaces):
		
		# Find a corner in the current selection (only if we need to start fresh)
		if not cornerCounter:
			corners = get_corners(faces=selFaces,preferred=cluster)
		
		# If there's no corner... we just use the first face... whatever
		if corners and len(corners) and cornerCounter < len(corners):
			face = corners[cornerCounter]
			cornerCounter += 1
		elif faceCounter < len(selFaces):
			face = selFaces[faceCounter]
			faceCounter += 1
		else:
			break
			
		cluster = get_cluster(face=face, faces=selFaces, limit=limit)
		
		# If we made a neat cluster...
		if len(cluster) == limit:
			
			bm, group_index = add_to_group(bme=bm, faces=cluster, newGroup=True,groupName=groupName)
			
			# Keep track of all added vertex groups!
			newGroups.append(group_index)
			
			 # Remove this cluster from the selection of faces we started with
			for face in cluster:
				selFaces.remove(face)
			
			# Reset the counters
			cornerCounter = 0
			faceCounter = 0

	put_bmesh(bm)
	
	return newGroups
	
	
# Apply some color to a face
def color_face(lay=None, face=None, col=None, hard=None):
	for L in face.loops:
		L[lay] = col
		if not hard:
			v = L.vert
			for L2 in v.link_loops:
				L2[lay] = col
	
	
	
# Set the base color for the entire mesh at the start
def color_mesh(col):

	bm = get_bmesh()
	
	# Get the crease custom data layer or make one if it doesn't exist
	col_lay = bm.loops.layers.color.active
	if col_lay is None: col_lay = bm.loops.layers.color.new()
	
	for f in bm.faces:
		color_face(lay=col_lay, face=f, col=col, hard=True)
	
	put_bmesh(bm)	
	
	
	
# Add some vertex colour to a limb
def color_limb(bme = None, col=None, jon=None, hard=None):
	
	if not bme:
		bm = get_bmesh()
	else:
		bm = bme
	
	if col:
	
		# Get the crease custom data layer or make one if it doesn't exist
		col_lay = bm.loops.layers.color.active
		if col_lay is None: col_lay = bm.loops.layers.color.new()
		
		for f in bm.faces:
			if f.select:
			
				# Find out if this face is on the outside of the selection
				out = False
				for e in f.edges:
					for f2 in e.link_faces:
						if not f2.select:
							out = True
							break
							
				# Define which color to use
				if jon and out:
					c = jon
				else:
					c = col
					
				#Apply the color
				color_face(col_lay, f, c, hard)
	
	if not bme:
		put_bmesh(bm)
	else:
		return bm
		
	
	
# Smooth the position of the verts in this list based on their neighbours
def smooth_verts(verts=None,loops=1):
	
	for i in range(loops):
		for v1 in verts:
			
			cnt = 1
			pos = mathutils.Vector(v1.co)
			
			for f in v1.link_faces:
			
				for v2 in f.verts:
					
					cnt += 1
					pos += v2.co
					
			v1.co = pos / cnt
	
		
		
# Find the next vert and place it the correct nr of degrees clockwise around the midpoint
def loop_step(v1,loopVerts, step,outEdges, center, dVec):

	#Check both edges connected to this one
	for e in v1.link_edges:
		
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
				v2co =  misc.rotate_vector_to_vector(v2co, v1co, -step)
			else:
				v2co =  misc.rotate_vector_to_vector(v2co, v1co, step)
				
			# Put the vert in the right position
			v2.co = v2co + center
			
			outEdges.remove(e)
			loopVerts.append(v2)
			
			dVec = v2co - v1co
			outEdges, loopVerts = loop_step(v2, loopVerts, step, outEdges, center, dVec)
			
			break
			
	return outEdges, loopVerts
		
# Casting loops is cool... hopefully it works well in bmesh! Yaya
# Scale can be a nr between 0.01 and 100.0
# Scale falloff should be a curve shape. ('STR', 'Straight',''),('SPI', 'Spike',''),('BUM', 'Bump',''),('SWE', 'Sweep',''),
def cast_loop(bme=None, corners=0, scale=1.0, scale_falloff='STR'):

	if not bme:
		bm = get_bmesh()
	else:
		bm = bme
		
	# Get a heap of lists to work with later!
	selFaces = get_selected_faces(bm)
	selVerts = get_selected_verts(bm)
	outVerts = get_outer_verts(selFaces)
	outEdges = get_outer_edges(selFaces)
	cent = get_center(selFaces)
	normal = get_normal(selFaces)
	
	# Let's quickly make a list of inner verts
	inVerts = []
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
	step = math.radians(360) / len(outEdges)
	
	# Now that we found the top vert we can start looping through to put them in the right position
	loopVerts = [outVerts[topVert]]
	outEdges, loopVerts = loop_step(outVerts[topVert],loopVerts,step,outEdges,cent,False)
	
	# At this point the shape of the loop should be a circle... so we can consider deforming it..
	if corners:
		c = 360.0 / corners
		a = (180.0 - c) * 0.5
		
		stepLen = math.ceil(len(outVerts) / corners)
		
		aLine = False
		
		currentX = 0.0
		vec = scale
		factor = 1.0
		curve = falloff_curve.curve(scale_falloff, 'mult')
		
		for i, v in enumerate(loopVerts):
		
			stepPos = i % stepLen
			
			# Get a normalized version of the current relative position
			line = mathutils.Vector(v.co - cent).normalized()
			
			# Get the starting line as a reference (is also a corner
			if not aLine:
				aLine = line
				currentX = 0.0
				factor = 1.0
				
				#if corner_group: corner_group.add([v.index], 1.0, 'REPLACE')
				
			else:
			
				# Find the angle from the current starting line
				cAng = aLine.angle(line)
				
				# If the angle is bigger than a step, we make this the new start
				if cAng > math.radians(c):
				
					#if corner_group: corner_group.add([v.index], 1.0, 'REPLACE')
					
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
					if scale != 1.0 and scale_falloff != 'STR':
					
						# Find out how far we are from the start as a factor (fraction of one?)
						angFac = cAng / math.radians(c)
						newX = angFac
						
						# Create a nice curve object to represent the falloff
						
						curve.update(1.0, 0.0, vec, currentX, newX)
						
						fac = abs(curve.currentVal)
						
						factor *= fac
						
						currentX = newX
						
					# Find the corner of the new triangle
					b = 180 - (a+math.degrees(cAng))
					
					# find the distance from the midpoint
					A = math.sin(math.radians(a)) / (math.sin(math.radians(b))/midDist)
					
					bLine = line * A
					
					bLine *= factor
					
					v.co = bLine + cent
					
	# I want to make sure these verts are inside the loop!
	# So we move all verts halfway towards the center before smoothing (neat results in entoforms)
	for v in inVerts:
		relPos = cent - v.co
		v.co += (relPos * 0.5)
		
	#for i in range(100):
	# SMOOTH THE VERTS MAN!!!
	smooth_verts(verts=inVerts,loops=10)
	#bmesh.ops.smooth_vert(bm, verts=inVerts,use_axis_x=True, use_axis_y=True, use_axis_z=True)

				
	if not bme:
		put_bmesh(bm)
	else:
		return bm