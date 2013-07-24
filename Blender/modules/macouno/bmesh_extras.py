import bpy, mathutils, bmesh


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
def get_selected_faces(bme=None):
	if not bme:
		bm = get_bmesh()
	else:
		bm = bme
		
	selFaces = [f for f in bm.faces if f.select]
	
	if not bme: put_bmesh(bm)
	
	return selFaces

	

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
		for v in f1.verts:
			# Check all connected faces
			for f2 in v.link_faces:
				if not f2 == f1 and not f2.select:
					outFaces.append(f1)
					
	return outFaces
	
	
	
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
def color_limb(b = None, col=None, jon=None, hard=None):
	
	if not b:
		bm = get_bmesh()
	else:
		bm = b
	
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
	
	if not b:
		put_bmesh(bm)
	else:
		return bm