import bpy, sys, mathutils, math, random
from bpy.app.handlers import persistent
from bpy.props import EnumProperty, IntProperty
	
	
@persistent
def SNet_Update(context):
	
	
	#scn = context.scene
	
	for ob in context.objects:
		if ob.SNet_enabled and ob.location[0] < 10.0:
			ob.location[0] += 0.01
			
			


	
	
# Add a charm panel to every object
class Object_SNet(bpy.types.Panel):
	bl_label = "Surface Net"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"

	def draw(self, context):
		layout = self.layout

		scn = context.scene
		ob = context.object
		
		row = layout.row()
		row.prop(ob,'SNet_enabled')
		
		
		
def SNet_Set(self, value):
	if self.SNet_enabled:
		print('Enabling Surface Net')
	else:
		print('Disabling Surface Net')
		
	
	
def register():
	
	# Is this object a net?
	bpy.types.Object.SNet_enabled = bpy.props.BoolProperty(default=False, name="Enable Surface Net", update=SNet_Set)
	
	bpy.utils.register_class(Object_SNet)
	#bpy.app.handlers.frame_change_pre.append(SurfaceNetUpdate)
	bpy.app.handlers.scene_update_pre.append(SNet_Update)


	
def unregister():
	
	del bpy.types.Object.SNet_enabled

	bpy.utils.unregister_class(Object_SNet)
	#bpy.app.handlers.frame_change_pre.remove(SurfaceNetUpdate)
	bpy.app.handlers.scene_update_pre.remove(SNet_Update)



if __name__ == "__main__":
	register()