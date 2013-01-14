

# Remove the items in the current group from all others
def cleanGroup(self, ob, group):

	bpy.ops.object.mode_set(mode='EDIT')
	self.ob.vertex_groups.active_index = group.index
	
	# Make sure the entire group is selected
	bpy.ops.mesh.select_all(action='DESELECT')
	ob.vertex_groups.active_index = group.index
	bpy.ops.object.vertex_group_select()
	
	# Set editing to vert mode before selecting less
	bpy.ops.wm.context_set_value(data_path='tool_settings.mesh_select_mode', value="(True, False, False)")
	bpy.ops.mesh.select_less()
	
	# Set editing back to face mode
	bpy.ops.wm.context_set_value(data_path='tool_settings.mesh_select_mode', value="(False, False, True)")
	
	for g in self.newGroups:
		if g.index != group.index:
			#print('cleaning',g.index,g.name)
			self.ob.vertex_groups.active_index = g.index
			bpy.ops.object.vertex_group_remove_from(all=False)