import bpy, mathutils, math
from mathutils import geometry

# Get a matrix for the selected polygons that you can use to do local transforms
def get_selection_matrix(polygons=False):
	
	me = bpy.context.active_object.data
	
	if not polygons:
		polygons = get_selected_polygons()
		
	# Only make a factor if there's more than one poly...!
	pLen = len(polygons)
	if pLen > 1:
		centre = get_selection_centre(polygons)
		
		# now lets find the points closest and furthest from the centre
		closest = False
		furthest = False

		for p in polygons:
		
			pCent = get_polygon_centre(p)
			
			pDist = pCent - centre
			pDist = pDist.length
			
			#print('dist',pDist)
			
			if furthest is False or pDist > furthest:
				furthest = pDist
			if closest is False or pDist < closest:
				closest = pDist
				
		#print('		close far',len(polygons),closest,furthest,centre)
	
	yVec = mathutils.Vector()
	zVec = mathutils.Vector()
	
	# Ok so we have a basic matrix, but lets base it more on the mesh!
	for p in polygons:
	
		if pLen > 1 and closest < furthest:
			# now we find out how close this poly is to the selection centre
			pCent = get_polygon_centre(p)
			pDist = pCent - centre
			pDist = pDist.length
			
			# Then we create a factor making polys closer to the centre of the selection bigger
			pDist -= closest
			pFact = (2.0 / (furthest - closest)) * pDist
		else:
			pFact = 1.0
		
			
		v1 = me.vertices[p.vertices[0]].co
		v2 = me.vertices[p.vertices[1]].co
		edge = v2-v1
		
		yVec += (edge.normalized() * pFact)
		
		if len(p.vertices) == 4:
			v1 = me.vertices[p.vertices[2]].co
			v2 = me.vertices[p.vertices[3]].co
			edge = v1-v2
			
			yVec += (edge.normalized() * pFact)
		
		zVec += mathutils.Vector(p.normal)
					
	if not yVec.length:
		quat = zVec.to_track_quat('-Z', 'Y')
		tMat = quat.to_matrix()
		yVec = tMat[1]
	yVec = yVec.normalized()
		
	if not zVec.length:
		quat = yVec.to_track_quat('-Z', 'Y')
		tMat = quat.to_matrix()
		zVec = tMat[1]
	zVec = zVec.normalized()
	
	#print('check',yVec.length,zVec.length)
	
	# Rotate yVec so it's 90 degrees to zVec
	cross =yVec.cross(zVec)
	vec = float(yVec.angle(zVec) - math.radians(90))
	mat = mathutils.Matrix.Rotation(vec, 3, cross)
	yVec =  (yVec * mat)
	
	xVec = yVec.cross(zVec)
	
	xVec = xVec.normalized()
	
	nMat = mathutils.Matrix((xVec, yVec, zVec)).transposed()
	
	return nMat


	
	
# Find the midpoint of your current selection
def get_selection_centre(polygons=False):
	
	me = bpy.context.active_object.data
	
	if not polygons:
		polygons = get_selected_polygons()
	
	centre = mathutils.Vector()
	
	i = 0
	for p in polygons:
		for v in p.vertices:
			centre += me.vertices[v].co
			i+=1
		
	centre /= i
	
	return centre
	
	
	
# Get the midpoint of a polygon
def get_polygon_centre(polygon=False):
	
	me = bpy.context.active_object.data
	
	centre = mathutils.Vector()
	
	for v in polygon.vertices:
		centre += me.vertices[v].co
		
	return centre / len(polygon.vertices)
	
	
	
# Smooth a specific list of verts
def smooth_selection(verts=False,loops=5):

	me = bpy.context.active_object.data

	if not verts:
		verts = get_selected_vertices()

	# Smooth the inner verts please (twice)
	for x in range(0,loops):
		# First create a list with neat average positions
		newCo = []
		for v1 in verts:
			
			v1co = mathutils.Vector(v1.co)
			v1in = v1.index
			v1cn = 1
			
			for p in me.polygons:
				if v1in in p.vertices:
					for v2in in p.vertices:
						v1co += me.vertices[v2in].co
						v1cn += 1
						
			v1co /= v1cn
			newCo.append(v1co)
			
		# Apply the list of neat average positions
		for i, v in enumerate(verts):
			v.co = newCo[i]
	
	
# Get the selection radius (minimum distance of an outer edge to the centre)
def get_selection_radius():

	ob = bpy.context.active_object

	radius = 0.0
	
	# no use continueing if nothing is selected
	if contains_selected_item(ob.data.polygons):
	
		# Find the center of the selection
		cent = mathutils.Vector()
		nr = 0
		nonVerts = []
		selVerts = []
		for p in ob.data.polygons:
			if p.select:
				for v in p.vertices:
					nr += 1
					cent += v.co
			else:
				nonVerts.extend(p.vertices)
				
		cent /= nr
		
		chk = 0
		
		# Now that we know the center.. we can figure out how close the nearest point on an outer edge is
		for e in get_selected_edges():
		
			nonSection = [v for v in e.vertices if v in nonVerts]
			if len(nonSection):
			
				v0 = ob.data.vertices[e.vertices[0]].co
				v1 = ob.data.vertices[e.vertices[1]].co
				
				# If there's more than 1 vert of this edge on the outside... we need the edge length to be long enough too!
				if len(nonSection) > 1:
					edge = v0 - v1
					edgeRad = edge.length * 0.5
					
					if edgeRad < radius or not chk:
						radius = edgeRad
						chk += 1
				
				int = geometry.intersect_point_line(cent, v0, v1)
				
				rad = cent - int[0]
				l = rad.length
				
				if l < radius or not chk:
					radius = l
					chk += 1
					
	return radius
	
	
	
# Get the average length of the outer edges of the current selection
def get_shortest_outer_edge_length():

	ob = bpy.context.active_object

	min = False
	me = ob.data
	
	delVerts = []
	for p in me.polygons:
		if not p.select:
			delVerts.extend(p.vertices)
	selEdges = [e.vertices for e in me.edges if e.select]

	if len(selEdges) and len(delVerts):
		
		for eVerts in selEdges:
			
			v0 = eVerts[0]
			v1 = eVerts[1]
			
			if v0 in delVerts and v1 in delVerts:
				ln = (me.vertices[v0].co - me.vertices[v1].co).length
				if min is False or (ln > 0.0 and ln < min):
					min = ln
						
	return min


# Get the average length of the outer edges of the current selection
def get_average_outer_edge_length():

	ob = bpy.context.active_object

	ave = 0.0
	me = ob.data
	
	delPolygons = [p.vertices for p  in me.polygons if not p.select]
	selEdges = [e.vertices for e in me.edges if e.select]

	if len(selEdges) and len(delPolygons):
	
		number = 0
		
		for eVerts in selEdges:
			
			v0 = eVerts[0]
			v1 = eVerts[1]
			
			for pVerts in delPolygons:
				if v0 in pVerts and v1 in pVerts:
					number += 1
					ave += (me.vertices[v0].co - me.vertices[v1].co).length
					break
						
		if number:
			ave /= number
			
	return ave


	
# Get the selected (or deselected items)
def get_selected(type='vertices',invert=False):
	
	mesh = bpy.context.active_object.data
	
	if type == 'vertices':
		items = mesh.vertices
	elif type == 'edges':
		items = mesh.edges
	else:
		items = mesh.polygons
		
	if invert:
		L = [i for i in items if not i.select]
	else:
		L = [i for i in items if i.select]
	return L
	
	
	
# See if the mesh has something selected
def has_selected(type='vertices',invert=False):
	
	mesh = bpy.context.active_object.data
	
	if type == 'vertices':
		items = mesh.vertices
	elif type == 'edges':
		items = mesh.edges
	else:
		items = mesh.polygons
		
	for i in items:
		if not invert and i.select:
			return True
		elif invert and not i.select:
			return True
			
	return False
		
		

# Get all the selected vertices (mode is selected or deselected)
def get_selected_vertices(mode='selected'):

	vertices = bpy.context.active_object.data.vertices

	if mode == 'deselected':
		L = [v for v in vertices if not v.select]
	else:
		L = [v for v in vertices if v.select]
	return L
	
	
	
# Get all the selected edges (mode is selected or deselected)
def get_selected_edges(mode='selected'):

	edges = bpy.context.active_object.data.edges

	if mode == 'deselected': 
		L = [e for e in edges if not e.select]
	else:
		L = [e for e in edges if e.select]
	return L


	
# Get all the selected polygons (mode is selected or deselected)
def get_selected_polygons(mode='selected', type='polys'):
	
	polygons = bpy.context.active_object.data.polygons
	
	if type == 'polys':
		if mode == 'deselected':
			L = [p for p in polygons if not p.select]
		else:
			L = [p for p in polygons if p.select]
	else:
		if mode == 'deselected':
			L = [p.index for p in polygons if not p.select]
		else:
			L = [p.index for p in polygons if p.select]
	return L
	
	
	
# See if there is at least one selected item in 'items'
def contains_selected_item(items):

	for item in items:
		if item.select:
			return True
				
	return False
	
	
	
# Weights for a list of verts relative to the centre of the selection
def makeWeights(verts):
	
	cen = mathutils.Vector()

	for v in verts:
		cen += v.co
	cen *= (1.0/len(verts))
	
	# Find the minimum and maximum distance from the centre
	min = 0.0
	max = 0.0
	distances = []
	for i, v in enumerate(verts):
		dist = (v.co - cen).length
		distances.append(dist)
		if not i or dist < min:
			min = dist
		if not i or dist > max:
			max = dist
			
	max = max - min
	
	if max > 0.0:
		factor = (1.0 / max)
	else:
		factor = 1.0
	
	# Make the weights
	weights = []
	for i, v in enumerate(verts):
		weight = (max - (distances[i] - min)) * factor
		weights.append(weight)
		
	return weights
	
	
	
# Function to find a corner in a list of polygons
# Finds a polygon with a vert that isn't shared
def get_corner_polygon(polygons):

	verts = []
	
	for p in polygons:
		for v in p.vertices:
			verts.append(v)
				
	for p in polygons:
		for v in p.vertices:
			if verts.count(v) == 1:
				return p
			
	return False


	
# Create vertex groups containing this selection (in different groupings)
# Written for use with the Entoforms addon
def group_selection(area='area', name='group', chunkProduct=1):

	ob = bpy.context.active_object
	polygons = get_selected_polygons()
	verts = []
	for p in polygons:
		for v in p.vertices:
			if not v in verts:
				verts.append(ob.data.vertices[v])
	
	# Make arrays for new groups and their matrices
	newGroups = []
	newMatrices = []

	
	# There really should be selected polygons
	if len(polygons):
	
		# There really should be verts
		if len(verts):
		
			# Add the entire selection in one
			if area == 'area':
		
				#make a new group called 'area'
				newGroup = ob.vertex_groups.new(name)
				newGroups.append(newGroup)
				
				newMatrices.append(get_selection_matrix(polygons))
				
				for v in verts:
						newGroup.add([v.index], 1.0, 'REPLACE')
						
						
						
			# Create a chunky selection (select a poly then select adjacent polys as well	
			elif area == 'chunks':
				
				selPolys = [p for p in polygons]
				
				while len(selPolys):
				
					chunkV = []
					chunkP = []
					
					# Get a poly at the corner.... or get a loose one if you can't... but you should always find one...
					p1 = get_corner_polygon(selPolys)
					if not p1:
						p1 = selPolys[0]
						
					chunkP.append(p1)
					for v in p1.vertices:
						chunkV.append(v)
					
					for p2 in selPolys:
						
						if not p1 == p2:
							int = set(p1.vertices).intersection( set(p2.vertices) )
							if len(int):
								for v in p2.vertices:
									if not v in chunkV:
										chunkV.append(v)
								chunkP.append(p2)
								
					# Make sure the chunk's size is a multiple of the product!
					# This usually to make sure the chunk is a multiple of 2....
					if not len(chunkP) % chunkProduct:
					
						newMatrices.append(get_selection_matrix(chunkP))
						
						newGroup = ob.vertex_groups.new(name)
						newGroups.append(newGroup)					
						for v in chunkV:
							newGroup.add([v], 1.0, 'REPLACE')
									 
					for p in chunkP:
						selPolys.remove(p)			

						
			# Add every polygon
			elif area == 'polygons':
			
				weights = makeWeights(verts)
			
				for i, p in enumerate(polygons):
					newMatrices.append(get_selection_matrix([p]))
					newGroup = ob.vertex_groups.new(name)
					newGroups.append(newGroup)
					
					vertList = p.vertices
					
					for i,v in enumerate(verts):
						ind = v.index
						if ind in vertList:
							newGroup.add([v.index], weights[i], 'REPLACE')
	
	return newGroups, newMatrices




	
	
		