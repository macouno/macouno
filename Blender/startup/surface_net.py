import bpy, sys, mathutils, math, random
from bpy.app.handlers import persistent
from bpy.props import EnumProperty, IntProperty

	
@persistent
def SurfaceNetUpdate(context):
	
	cntx = bpy.context
	scn = cntx.scene
	
	for ob in scn.objects:
		if ob.surface_net_enabled:
			ob.location[0] += 0.01


	
	
# Add a charm panel to every object
class Object_surface_net(bpy.types.Panel):
	bl_label = "Surface Net"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"

	def draw(self, context):
		layout = self.layout

		scn = context.scene
		ob = context.object
		
		row = layout.row()
		row.prop(ob,'surface_net_enabled')
		
		
		
def set_net(self, value):
	if self.surface_net_enabled:
		print('Enabling Surface Net')
	else:
		print('Disabling Surface Net')
		
	
	
def register():
	
	# Is this object a net?
	bpy.types.Object.surface_net_enabled = bpy.props.BoolProperty(default=False, name="Enable Surface Net", update=set_net)
	
	bpy.utils.register_class(Object_surface_net)
	#bpy.app.handlers.frame_change_pre.append(SurfaceNetUpdate)
	bpy.app.handlers.scene_update_pre.append(SurfaceNetUpdate)


	
def unregister():
	
	del bpy.types.Object.surface_net_enabled

	bpy.utils.unregister_class(Object_surface_net)
	#bpy.app.handlers.frame_change_pre.remove(SurfaceNetUpdate)
	bpy.app.handlers.scene_update_pre.remove(SurfaceNetUpdate)



if __name__ == "__main__":
	register()