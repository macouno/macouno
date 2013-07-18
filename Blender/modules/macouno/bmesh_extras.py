import bpy, mathutils, bmesh
from macouno import mesh_extras


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