import bpy, time, math

'''
This module is used to trigger a certain action... 
It can be any of the following
	
	Nothing
	Debug info (writes debug info to console)
	Redraw scene (refresh interface)
	Render animation (increases frame and renders a single image)
'''

def go(debug=False, action='NON'):

	if action == 'NON':
		return

	else:
		
		bpy.ops.object.mode_set(mode='OBJECT')
		
		bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
		
		if action == 'ANI':
		
			scn = bpy.context.scene
			
			# Get start and end frames for later resetting
			frm_start = scn.frame_start
			frm_end = scn.frame_end
			frm_cur = scn.frame_current + 1
			
			# Set all frames to the same number
			scn.frame_current = frm_cur
			scn.frame_start = frm_cur
			scn.frame_end = frm_cur
			
			bpy.ops.render.render(animation=True,write_still=False, use_viewport=False)
			
			# Reset start and end frames
			scn.frame_start = frm_start
			scn.frame_end = frm_end
			
			bpy.ops.object.mode_set(mode='EDIT')
			
	return
			
			
			
			
			

	