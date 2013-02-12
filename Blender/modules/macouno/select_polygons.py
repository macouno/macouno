import bpy, mathutils
from macouno import mesh_extras


# Select all polygons (or deselect)
def all(invert=False):
	for p in bpy.context.active_object.data.polygons:
		p.select = True
	return



# Select all polygons (or deselect)
def none():
	me = bpy.context.active_object.data
	for p in me.polygons:
		p.select = False
	for v in me.vertices:
		v.select = False
	for e in me.edges:
		e.select = False
	return



# polygons connected to the current selection
def connected(extend=False):

	mesh = bpy.context.active_object.data

	if len(mesh.polygons):
	
		# Get a list of all vertices in selected polygons
		vList = []
		for p in mesh.polygons:
			if p.select:
				vList.extend(p.vertices)
				
		if len(vList):
			# For every deselected face, see if it shares a vert with a selected face
			selpolygons = []
			for p in mesh.polygons:
				if not p.select:
					for v in p.vertices:
						if v in vList:
							selpolygons.append(p)
							break
							
			if len(selpolygons):
				# Select only the connected polygons
				if not extend:
					for p in mesh.polygons:
						if p in selpolygons:
							p.select = True
						else:
							p.select = False
							
				# Add the connected polygons to the current selection
				else:
					for p in selpolygons:
						p.select=True

	return



# Innermost polygons
def innermost(invert=False):

	mesh = bpy.context.active_object.data

	# No use continueing if there's no edges
	if len(mesh.polygons):

		# Get a list with the selected items
		oItems = mesh_extras.get_selected('polygons',False)
		oLen = len(oItems)
		
		# No use continueing if there's no selected items and deselected items
		if oLen and mesh_extras.has_selected('polygons',True):
		
			nItems = oItems
			nLen = oLen
			
			while True:
				cLen = nLen
				cItems = nItems
		
				# Deselect the outermost items
				outermost(True)
				
				nItems = mesh_extras.get_selected('polygons',False)
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

	if len(mesh.polygons):
	
		# Get a list of all vertices in deselected polygons
		vList = []
		for p in mesh.polygons:
			if not p.select:
				vList.extend(p.vertices)
				
		if len(vList):
			# For every deselected face, see if it shares a vert with a selected face
			selpolygons = []
			for p in mesh.polygons:
				if  p.select:
					for v in p.vertices:
						if v in vList:
							selpolygons.append(p)
							break
							
			if len(selpolygons):
				# Select only the connected polygons
				if not invert:
					for p in mesh.polygons:
						if p in selpolygons:
							p.select = True
						else:
							p.select = False
							
				# Add the connected polygons to the current selection
				else:
					for p in selpolygons:
						p.select=False

	return



# Select checkered polygons
def checkered(seed=0, extend=False):
    
	import random
	random.seed(str(seed))
	
	mesh = bpy.context.active_object.data
	
	# Two lists of polygons selpolygons to be selected unpolygons to be deselected
	selpolygons = []
	unpolygons = list(mesh.polygons)
	
	# Put 1 face in the list of selected polygons (and remove from unselected polygons)
	p = random.choice(unpolygons)
	selpolygons.append(p)
	unpolygons.remove(p)
			
	preSel = len(selpolygons)
			
	# make sure there's polygons before we continue!
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
		
		# Add the polygons at the corners of the current selection to this one
		selpolygons, unpolygons = addCornered(selpolygons, unpolygons)
		
		postSel = len(selpolygons)
	
	# Select the polygons we found!
	selectpolygons(selpolygons, extend)
	
	return



def addCornered(selpolygons, unpolygons):

	# Loop through the unselected polygons to find out if they should be selected
	for p in unpolygons:
		
		verts = p.vertices
		sel = 0

		# Check against the selected polygons
		for ps in selpolygons:
		
			# Find the verts shared between these polygons
			intersection = [v for v in verts if v in ps.vertices]
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
			selpolygons.append(p)
			unpolygons.remove(p)

	
	return selpolygons, unpolygons
	
	

# Select all the polygons in a certain vertex group
def in_group(group,extend=False):

	groupId = group.index
	mesh = bpy.context.active_object.data
	
	selpolygons = []
	
	# Find all the polygons with all verts (3 or more) in this group
	for p in mesh.polygons:
		grCnt = 0
		for v in p.vertices:
			vert = mesh.vertices[v]
			try:
				for g in vert.groups:
					if g.group == groupId:
						grCnt += 1
						break
			except:
				pass
				
		if grCnt == len(p.vertices):
			selpolygons.append(p)
	
	selectpolygons(selpolygons, extend)
	
	return



# Go select a list of polygons (if they need to be, depending on settings and situations)
def selectpolygons(selpolygons, extend=False):

	mesh = bpy.context.active_object.data

	hasSelected = mesh_extras.contains_selected_item(mesh.polygons)
	
	for p in mesh.polygons:
	
		# We extend and have a selection, so we just need to select extra stuff 
		# Selecting what is already selected does no harm
		if extend and hasSelected:
		
			if p in selpolygons:
				p.select = True
				
		# If we already have a selection and we don't extend.. we just deselect what is selected
		elif hasSelected:
		
			if not p in selpolygons:
				p.select = False
		
		# If we have no selection yet.. we only select what's in the list
		else:
		
			if p in selpolygons:
				p.select = True
	
	return



# Select by direction
def by_direction(direction, divergence, extend=False):
	
	me = bpy.context.active_object.data
	direction = mathutils.Vector(direction)
	
	hasSelected = mesh_extras.contains_selected_item(me.polygons)
	
	# Make sure there's an actual directions
	if direction.length:

		# Loop through all the given polygons
		for p in me.polygons:
		
			isSelected = p.select
			s = selectCheck(isSelected, hasSelected, extend)
			d = deselectCheck(isSelected, hasSelected, extend)
			
			if p.normal.length:
				angle = direction.angle(p.normal)
			else:
				angle = 0.0
				
			if s and angle <= divergence:
				p.select = True
			elif d and angle > divergence:
				p.select = False
				
	return



# Do a semi random select based on a number				
def liberal(key='', extend=False):

	from macouno import liberty
	lib = liberty.liberty('bool', key)

	mesh = bpy.context.active_object.data

	hasSelected = mesh_extras.contains_selected_item(mesh.polygons)

	# Loop through all the given polygons
	for p in mesh.polygons:
			
		s = selectCheck(p.select, hasSelected, extend)
		d = deselectCheck(p.select, hasSelected, extend)
		
		# Check if the polygons match any of the directions
		if s and lib.Choose('bool'):
			p.select = True
			
		if d and not lib.Choose('bool'):
			p.select = False
			
	return



# Make sure there are less polygons selected than the limit
def limit(limit=1, key=''):

	from macouno import liberty
	lib = liberty.liberty('string', key)

	nupolygons = lib.makeDict(mesh_extras.get_selected_polygons())
	nuLen = len(nupolygons)
	
	while nuLen > limit:
	
		deFace = lib.Choose('select',nupolygons)
		
		deFace.select = False
	
		nupolygons = lib.makeDict(mesh_extras.get_selected_polygons())
		nuLen = len(nupolygons)
		
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