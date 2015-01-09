import bpy, sys, mathutils, math
from bpy.app.handlers import persistent
from bpy.props import EnumProperty, IntProperty

	

@persistent
def CharmUpdate(context):

	# See if zclipping is enabled... if not... we don't do anything
	try:
		ob = bpy.context.active_object
		if not ob.finch_enabled:
			return
	except:
		return
		
	# Some basic settings
	maxSpeed = 0.5
	maxRot = math.radians(10.0)
	maxDist = 15.0
	
	# Retrieve the values for this Finch
	movement = mathutils.Vector(ob.finch_move)
	target = mathutils.Vector(ob.finch_target)
	speed = movement.length

	
	# See if the Finch is too far from the scene center
	loc = ob.location
	if loc.length > maxDist:
		
		print('setting loc')
		target = mathutils.Vector(loc)
		target.negate()
		target.normalize()
		
	# If we need to change where we're going... do so here
	if target != movement:
	
		ang = movement.angle(target)
		
		if ang < maxRot:
			movement = target
			
		else:
			
			targetAngle = ang - maxRot
		
			#cross =movement.cross(target)
			mat = mathutils.Matrix.Rotation(maxRot, 3, 'Z')
			
			movement.rotate(mat)
			ob.rotation_euler.rotate(mat)
		
		#cross = movement.cross(target)
		
		#ob.rotation_euler.rotate_axis(cross, maxRot)
		
	movement.normalize()
		
	if movement.length:
	
		ob.location += movement
	
	# Yaw = rotate around the local Z (side to side)
	# Pitch = rotate around the local x (nose up)
	# Roll = rotate around the local y (roll/twist)
	print(1, mathutils.Vector(ob.finch_move))
	
	ob.finch_move = [movement[0], movement[1], movement[2]]
	
	print(2, mathutils.Vector(ob.finch_move))
	
	ob.finch_target = [target[0], target[1], target[2]]

# Add a charm panel to every object
class Object_finch(bpy.types.Panel):
	bl_label = "Charm"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"

	def draw(self, context):
		layout = self.layout

		scn = context.scene
		ob = context.object
		
		row = layout.row()
		row.prop(ob,'finch_enabled')
		
		row = layout.row()
		row.prop(ob,'finch_target')
		row = layout.row()
		row.prop(ob,'finch_move')


	
def register():
	
	# Is this object a finch?
	bpy.types.Object.finch_enabled = bpy.props.BoolProperty(default=False,name="Finch")
	
	# The target speed & direction
	bpy.types.Object.finch_target = bpy.props.FloatVectorProperty(name="Target", description="The direction and speed the finch wants to move in", default=(0.0, 0.1, 0.0), step=3, precision=2, options={'ANIMATABLE'})
	
	# The thrust/displacement
	bpy.types.Object.finch_move = bpy.props.FloatVectorProperty(name="Movement", description="The current movement", default=(0.0, 0.1, 0.0), step=3, precision=2, options={'ANIMATABLE'})
	

	bpy.utils.register_class(Object_finch)
	bpy.app.handlers.scene_update_post.append(CharmUpdate)


	
def unregister():
	
	del bpy.types.Object.finch_enabled
	del bpy.types.Object.finch_target
	del bpy.types.Object.finch_move

	
	bpy.utils.unregister_class(Object_finch)
	bpy.app.handlers.scene_update_post.remove(CharmUpdate)



if __name__ == "__main__":
	register()