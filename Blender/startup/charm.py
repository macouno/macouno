import bpy, sys, mathutils, math, random
from bpy.app.handlers import persistent
from bpy.props import EnumProperty, IntProperty

	

@persistent
def CharmUpdate(context):
	
	cntx = bpy.context
	scn = cntx.scene
	frm = scn.frame_current
	pi2 = math.pi * 2
	
	# Update/maintain the group!
	try:
		charm = bpy.data.groups['charm']
	except:
		charm = bpy.data.groups.new('charm')
	
	for ob in scn.objects:
		if ob.finch_enabled:
			try:
				charm.objects.link(ob)
			except:
				pass
			# Reset location and rotation on the first frame
			if frm == 1:
				ob.location = ob.finch_startPos
				ob.rotation_euler = ob.finch_startRot
		else:
			try:
				charm.objects.unlink(ob)
			except:
				pass

	# See if zclipping is enabled... if not... we don't do anything
	for finch in charm.objects:
	
		if finch.finch_enabled:
		
			# Some basic settings
			random.seed(1)
			maxSpeed = 1.0
			maxRot = math.radians(10.0)
			maxDist = 15.0
			
			# Retrieve the values for this Finch
			oldMove = mathutils.Vector(ob.finch_move)
			newMove = oldMove
			rotation = mathutils.Euler(ob.finch_rotate)
			target = mathutils.Vector(ob.finch_target)
			speed = newMove.length

			
			# See if the Finch is too far from the scene center
			loc = finch.location
			if loc.length > maxDist:
				
				#print('setting loc')
				target = mathutils.Vector(loc)
				target.negate()
				target.normalize()
				
			# If we need to change where we're going... do so here
			if target != newMove:
			
				ang = round(newMove.angle(target),2)
				
				# The cross is the vector we rotate around
				# Unable to make a cross product for angles of 0 and 180 degrees
				if ang == 0.0 or ang == round(math.pi,2):
					cross = 'Z'
					if random.random() > 0.5:
						ang = -ang
					
				else:
					cross = newMove.cross(target)
				
					
				#cross =movement.cross(target)
				rotZ = rotation[2]

				if abs(rotZ) < maxRot:
					if rotZ < 0.0:
						rotZ -= math.radians(1)
					else:
						rotZ += math.radians(1)

				mat = mathutils.Matrix.Rotation(rotZ, 3, cross)
				rotation[2] = rotZ
				newMove.rotate(mat)
				
				# We normalize and add the old move to make smooth transistions
				newMove.normalize()
				newMove *= 0.2
				newMove += oldMove
				
				quat = newMove.to_track_quat('Y', 'Z')
				finch.rotation_quaternion = quat
				
			# Hard limit for the speed
			if newMove.length > maxSpeed:
				newMove.normalize()
				newMove *= maxSpeed
				
			# So... if there is movement... apply it to the object's location
			if newMove.length:
			
				finch.location += newMove
			
			# Yaw = rotate around the local Z (side to side)
			# Pitch = rotate around the local x (nose up)
			# Roll = rotate around the local y (roll/twist)
			
			# Keep all these values for the next iteration
			finch.finch_move = newMove #[newMove[0], newMove[1], newMove[2]]
			finch.finch_rotate = rotation
			finch.finch_target = target

	
	
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
		
		
		
# Run this when enabling the finch... to save it's location and such
def set_finch(self, value):
	#self.finch_enabled = value
	if self.finch_enabled:
		self.rotation_mode = 'QUATERNION'
		self.finch_startPos = self.location
		self.finch_startRot = self.rotation_quaternion.to_euler('XYZ')
		
		target = mathutils.Vector((0.0,1.0,0.0))
		target = (target * self.matrix_world)
		target.normalize()
		
		self.finch_target = target
		self.finch_move = target
		
	else:
		self.location = self.finch_startPos
		self.rotation_quaternion = mathutils.Euler(self.finch_startRot).to_quaternion()
		
	
	
def register():
	
	# Is this object a finch?
	bpy.types.Object.finch_enabled = bpy.props.BoolProperty(default=False, name="Finch", update=set_finch)
	
	bpy.types.Object.finch_startPos = bpy.props.FloatVectorProperty(name="Start position", description="The direction and speed the finch wants to move in", default=(0.0, 0.1, 0.0), step=3, precision=2, options={'ANIMATABLE'})
	bpy.types.Object.finch_startRot = bpy.props.FloatVectorProperty(name="Start rotation", description="The direction and speed the finch wants to move in", default=(0.0, 0.1, 0.0), step=3, precision=2, options={'ANIMATABLE'})
	
	# The target speed & direction
	bpy.types.Object.finch_target = bpy.props.FloatVectorProperty(name="Target", description="The direction and speed the finch wants to move in", default=(0.0, 0.1, 0.0), step=3, precision=2, options={'ANIMATABLE'})
	
	# The thrust/displacement
	bpy.types.Object.finch_move = bpy.props.FloatVectorProperty(name="Movement", description="The current movement", default=(0.0, 0.1, 0.0), step=3, precision=2, options={'ANIMATABLE'})
	
	bpy.types.Object.finch_rotate = bpy.props.FloatVectorProperty(name="Rotation", description="The current movement", default=(0.0, 0.0, 0.0), step=3, precision=2, options={'ANIMATABLE'})
	

	bpy.utils.register_class(Object_finch)
	bpy.app.handlers.frame_change_pre.append(CharmUpdate)


	
def unregister():
	
	del bpy.types.Object.finch_enabled
	del bpy.types.Object.finch_startPosition
	del bpy.types.Object.finch_startRotation
	del bpy.types.Object.finch_target
	del bpy.types.Object.finch_move
	del bpy.types.Object.finch_rotation

	
	bpy.utils.unregister_class(Object_finch)
	bpy.app.handlers.frame_change_pre.remove(CharmUpdate)



if __name__ == "__main__":
	register()