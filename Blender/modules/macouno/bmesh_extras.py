import bpy, mathutils, bmesh


# Get the bmesh data from the current mesh object
def get_bmesh():
	
	# Get the active mesh
	ob = bpy.context.object
	me = ob.data
	
	sel = 0
	for f in me.polygons:
		if f.select:
			sel += 1

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
	ob = bpy.context.object
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
def get_selected(bm):
	return [f for f in bm.faces if f.select]

	

def has_selected(bm):
	for f in bm.faces:
		if f.select:
			return True
	return False
	
	
	
# Crease all edges sharper than 60 degrees (1 radians-ish)
def crease_edges(sharpness='', limit=1.0, group=''):
	bm = get_bmesh()
	
	# Get the crease custom data layer or make one if it doesn't exist
	crease_lay = bm.edges.layers.crease.active
	if crease_lay is None: crease_lay = bm.edges.layers.crease.new()
	
	# Create edge creases based on a group
	if group:
		gi = bpy.context.active_object.vertex_groups[group].index
	
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
	