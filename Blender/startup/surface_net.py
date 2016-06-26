import bpy, sys, mathutils, math, random
from bpy.app.handlers import persistent
from bpy.props import EnumProperty, IntProperty

	
@persistent
def SurfaceNetUpdate(context):
	
	#scn = context.scene
	
	for ob in context.objects:
		if ob.sn_enabled:
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
		row.prop(ob,'sn_enabled')
		
		#These should only be visible whilst debugging really
		
		row = layout.row()
		row.prop(ob,'sn_growthRate')
		
		row = layout.row()
		row.prop(ob,'sn_gridSize')
		
		
		
def set_net(self, value):
	if self.sn_enabled:
		print('Enabling Surface Net')
	else:
		print('Disabling Surface Net')
		
	
	
def register():
	
	# Is this object a net?
	bpy.types.Object.sn_enabled = bpy.props.BoolProperty(default=False, name="Enable Surface Net", update=set_net)
	
	bpy.types.Object.sn_growthRate = bpy.props.FloatProperty(name="Growth Rate", description="", default=0.05, min=sys.float_info.min, max=sys.float_info.max, soft_min=sys.float_info.min, soft_max=sys.float_info.max, step=3, precision=2, options={'ANIMATABLE'}, subtype='NONE', unit='NONE', update=None, get=None, set=None)
	
	#bpy.types.Object.sn_growthRate = bpy.props.IntProperty(name="Growth Rate", description="", default=0, min=-2**31, max=2**31-1, soft_min=-2**31, soft_max=2**31-1, step=1, options={'ANIMATABLE'}, subtype='NONE', update=None, get=None, set=None)
	
	bpy.types.Object.sn_gridSize = bpy.props.IntVectorProperty(name="Grid Size", description="", default=(10, 10, 10), min=-2**31, max=2**31-1, soft_min=-2**31, soft_max=2**31-1, step=1, options={'ANIMATABLE'}, subtype='NONE', size=3, update=None, get=None, set=None)
	
	bpy.utils.register_class(Object_surface_net)
	#bpy.app.handlers.frame_change_pre.append(SurfaceNetUpdate)
	bpy.app.handlers.scene_update_pre.append(SurfaceNetUpdate)


	
def unregister():
	
	del bpy.types.Object.sn_enabled
	del bpy.types.Object.sn_growthRate
	del bpy.types.Object.sn_gridSize

	bpy.utils.unregister_class(Object_surface_net)
	#bpy.app.handlers.frame_change_pre.remove(SurfaceNetUpdate)
	bpy.app.handlers.scene_update_pre.remove(SurfaceNetUpdate)



if __name__ == "__main__":
	register()