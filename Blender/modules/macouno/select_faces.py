import bpy, mathutils
from macouno import mesh_extras


# Select all faces (or deselect)
def all(invert=False):
	for f in bpy.context.active_object.data.faces:
		f.select = True
	return



# Select all faces (or deselect)
def none():
	for p in bpy.context.active_object.data.polygons:
		f.select = False
	return



# Faces connected to the current selection
def connected(extend=False):

	mesh = bpy.context.active_object.data

	if len(mesh.faces):
	
		# Get a list of all vertices in selected faces
		vList = []
		for f in mesh.faces:
			if f.select:
				vList.extend(f.vertices)
				
		if len(vList):
			# For every deselected face, see if it shares a vert with a selected face
			selFaces = []
			for f in mesh.faces:
				if not f.select:
					for v in f.vertices:
						if v in vList:
							selFaces.append(f)
							break
							
			if len(selFaces):
				# Select only the connected faces
				if not extend:
					for f in mesh.faces:
						if f in selFaces:
							f.select = True
						else:
							f.select = False
							
				# Add the connected faces to the current selection
				else:
					for f in selFaces:
						f.select=True

	return



# Innermost faces
def innermost(invert=False):

	mesh = bpy.context.active_object.data

	# No use continueing if there's no edges
	if len(mesh.faces):

		# Get a list with the selected items
		oItems = mesh_extras.get_selected('faces',False)
		oLen = len(oItems)
		
		# No use continueing if there's no selected items and deselected items
		if oLen and mesh_extras.has_selected('faces',True):
		
			nItems = oItems
			nLen = oLen
			
			while True:
				cLen = nLen
				cItems = nItems
		
				# Deselect the outermost items
				outermost(True)
				
				nItems = mesh_extras.get_selected('faces',False)
				nLen = len(nItems)
				
				if nLen >= cLen or not nLen:
					break
					
			# If we have a list with items, and it's smaller than the original
			if cLen and cLen < oLen:
				for item in oItems:
					if not invert and item in cItems:
						item.select = True
						
					elif invert and not item in cItems:
						item.select = True
				
	return



# Select the outermost items in the current selection
# mesh=mesh data, invert = True or False
def outermost(invert=False):

	mesh = bpy.context.active_object.data

	if len(mesh.faces):
	
		# Get a list of all vertices in deselected faces
		vList = []
		for f in mesh.faces:
			if not f.select:
				vList.extend(f.vertices)
				
		if len(vList):
			# For every deselected face, see if it shares a vert with a selected face
			selFaces = []
			for f in mesh.faces:
				if  f.select:
					for v in f.vertices:
						if v in vList:
							selFaces.append(f)
							break
							
			if len(selFaces):
				# Select only the connected faces
				if not invert:
					for f in mesh.faces:
						if f in selFaces:
							f.select = True
						else:
							f.select = False
							
				# Add the connected faces to the current selection
				else:
					for f in selFaces:
						f.select=False

	return



# Select checkered faces
def checkered(seed=0, extend=False):
    
	import random
	random.seed(str(seed))
	
	mesh = bpy.context.active_object.data
	
	# Two lists of faces selFaces to be selected unFaces to be deselected
	selFaces = []
	unFaces = list(mesh.faces)
	
	# Put 1 face in the list of selected faces (and remove from unselected faces)
	f = random.choice(unFaces)
	selFaces.append(f)
	unFaces.remove(f)
			
	preSel = len(selFaces)
			
	# make sure there's faces before we continue!
	if not preSel:
		return

	postSel = preSel + 1
	start = True
	
	# As long as we keep selecting more... we have to continue (to go over all the mesh)
	while postSel > preSel:
		
		if start:
			start = False
		else:
			preSel = postSel
		
		# Add the faces at the corners of the current selection to this one
		selFaces, unFaces = addCornered(selFaces, unFaces)
		
		postSel = len(selFaces)
	
	# Select the faces we found!
	selectFaces(selFaces, extend)
	
	return



def addCornered(selFaces, unFaces):

	# Loop through the unselected faces to find out if they should be selected
	for f in unFaces:
		
		verts = f.vertices
		sel = 0

		# Check against the selected faces
		for fs in selFaces:
		
			# Find the verts shared between these faces
			intersection = [v for v in verts if v in fs.vertices]
			intLen = len(intersection)
			
			# If there's just the one intersection it's a corner connection
			if intLen == 1 and sel == 0:
				sel = 1
				
			# If there's more than one... it's sharing an edge
			elif intLen > 1:
				sel = 2
				break
				
		# If it's just a corner
		if sel == 1:
			selFaces.append(f)
			unFaces.remove(f)

	
	return selFaces, unFaces
	
	

# Select all the faces in a certain vertex group
def in_group(group,extend=False):

	groupId = group.index
	mesh = bpy.context.active_object.data
	
	selFaces = []
	
	# Find all the faces with all verts (3 or more) in this group
	for f in mesh.faces:
		grCnt = 0
		for v in f.vertices:
			vert = mesh.vertices[v]
			try:
				for g in vert.groups:
					if g.group == groupId:
						grCnt += 1
						break
			except:
				pass
				
		if grCnt == len(f.vertices):
			selFaces.append(f)
	
	selectFaces(selFaces, extend)
	
	return



# Go select a list of faces (if they need to be, depending on settings and situations)
def selectFaces(selFaces, extend=False):

	mesh = bpy.context.active_object.data

	hasSelected = mesh_extras.contains_selected_item(mesh.faces)
	
	for f in mesh.faces:
	
		# We extend and have a selection, so we just need to select extra stuff 
		# Selecting what is already selected does no harm
		if extend and hasSelected:
		
			if f in selFaces:
				f.select = True
				
		# If we already have a selection and we don't extend.. we just deselect what is selected
		elif hasSelected:
		
			if not f in selFaces:
				f.select = False
		
		# If we have no selection yet.. we only select what's in the list
		else:
		
			if f in selFaces:
				f.select = True
	
	return



# Select by direction
def by_direction(direction, divergence, extend=False):
	
	mesh = bpy.context.active_object.data
	direction = mathutils.Vector(direction)
	
	hasSelected = mesh_extras.contains_selected_item(mesh.faces)
	
	# Make sure there's an actual directions
	if direction.length:

		# Loop through all the given faces
		for f in mesh.faces:
		
			isSelected = f.select
			s = selectCheck(isSelected, hasSelected, extend)
			d = deselectCheck(isSelected, hasSelected, extend)
			
			angle = direction.angle(f.normal)
			
			if s and angle <= divergence:
				f.select = True
			elif d and angle > divergence:
				f.select = False
				
	return



# Do a semi random select based on a number				
def liberal(key='', extend=False):

	from macouno import liberty
	lib = liberty.liberty('bool', key)

	mesh = bpy.context.active_object.data

	hasSelected = mesh_extras.contains_selected_item(mesh.faces)

	# Loop through all the given faces
	for f in mesh.faces:
			
		s = selectCheck(f.select, hasSelected, extend)
		d = deselectCheck(f.select, hasSelected, extend)
		
		# Check if the faces match any of the directions
		if s and lib.Choose('bool'):
			f.select = True
			
		if d and not lib.Choose('bool'):
			f.select = False
			
	return



# Make sure there are less faces selected than the limit
def limit(limit=1, key=''):

	from macouno import liberty
	lib = liberty.liberty('string', key)

	nuFaces = lib.makeDict(mesh_extras.get_selected_faces())
	nuLen = len(nuFaces)
	
	while nuLen > limit:
	
		deFace = lib.Choose('select',nuFaces)
		
		deFace.select = False
	
		nuFaces = lib.makeDict(mesh_extras.get_selected_faces())
		nuLen = len(nuFaces)
		
	return



# See if the current item should be selected or not
def selectCheck(isSelected, hasSelected, extend):
		
	# If we are extending or nothing is selected we want to select
	if extend or not hasSelected:
		return True
			
	return False



# See if the current item should be deselected or not
def deselectCheck(isSelected, hasSelected, extend):
	
	# If something is selected and we're not extending we want to deselect
	if hasSelected and not extend:
		return True

	return False