import bpy, sys, mathutils
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
		
	# Yaw = rotate around the local Z (side to side)
	
	# Pitch = rotate around the local x (nose up)
	
	# Roll = rotate around the local y (roll/twist)


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
		row.prop(ob,'finch_thrust')
		row = layout.row()
		row.prop(ob,'finch_target')
		row.prop(ob,'finch_rotation')


def register():
	
	# Is this object a finch?
	bpy.types.Object.finch_enabled = bpy.props.BoolProperty(default=False,name="Finch")
	
	# The target speed & direction
	bpy.types.Object.finch_target = bpy.props.FloatVectorProperty(name="Target", description="The direction and speed the finch wants to move in", default=(0.0, 0.01, 0.0), min=sys.float_info.min, max=sys.float_info.max, soft_min=sys.float_info.min, soft_max=sys.float_info.max, step=3, precision=2, options={'ANIMATABLE'}, subtype='NONE', size=3, update=None, get=None, set=None)
	
	# The current rotational forces
	bpy.types.Object.finch_rotation = bpy.props.FloatVectorProperty(name="Rotation", description="The current rotational forces", default=(0.0, 0.0, 0.0), min=sys.float_info.min, max=sys.float_info.max, soft_min=sys.float_info.min, soft_max=sys.float_info.max, step=3, precision=2, options={'ANIMATABLE'}, subtype='NONE', size=3, update=None, get=None, set=None)
	
	# The current ammount of thrust
	bpy.types.Object.finch_thrust = bpy.props.FloatProperty(default=0.1,name="Thrust", precision=3,unit="LENGTH")

	bpy.utils.register_class(Object_finch)
	bpy.app.handlers.scene_update_post.append(CharmUpdate)


def unregister():
	
	del bpy.types.Object.finch_enabled
	del bpy.types.Object.finch_target
	del bpy.types.Object.finch_rotation
	del bpy.types.Object.finch_thrust

	
	bpy.utils.unregister_class(Object_finch)
	bpy.app.handlers.scene_update_post.remove(CharmUpdate)


if __name__ == "__main__":
	register()