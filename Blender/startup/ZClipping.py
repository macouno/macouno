import bpy, bmesh
from bpy.app.handlers import persistent
from bpy.props import EnumProperty, FloatProperty

@persistent
def ZClipUpdate(context):
	
	ob = bpy.context.active_object
	nz = ob.zclip_newz
	oz = ob.zclip_oldz
	if not nz == oz:
		cnt = 0
		ob.zclip_oldz = nz
		b = ob.zclip_buf * 0.5
		me = ob.data
		hidden = []
		for v in me.vertices:
			if abs(v.co[2] - nz) <= b:
				v.hide = False
				cnt += 1
			else:
				v.hide = True
				hidden.append(v.index)
				
		if len(hidden):
			for e in me.edges:
				e.hide = False
				for v in hidden:
					if v in e.vertices:
						e.hide = True
						
			
		print(cnt)
		


class ZClipOperator(bpy.types.Operator):
	bl_idname = "object.zclip"
	bl_label = "Z Clip"
	bl_options = {'REGISTER', 'UNDO'}
	
	z = FloatProperty(name='Z', default=0.0, min=-1000.0, max=1000.0, soft_min=-10000.0, soft_max=10000.0)
	
	
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		print('running',z)
		return {'FINISHED'}





class ZClipPanel(bpy.types.Panel):
	bl_label = "ZClip"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"

	def draw(self, context):
		layout = self.layout

		scn = context.scene
		ob = context.active_object

		row = layout.row()
		row.prop(ob,'zclip_newz')
		row = layout.row()
		row.prop(ob,'zclip_buf')
		
	def update(self,context):
		print('UPDATE')
		
		

def register():
	
	bpy.utils.register_class(ZClipOperator)
	bpy.utils.register_class(ZClipPanel)
	
	bpy.types.Object.zclip_newz = bpy.props.FloatProperty(default=0.0,name="Z", precision=2,unit="LENGTH")
	bpy.types.Object.zclip_oldz = bpy.props.FloatProperty(default=0.0,name="OLDZ", precision=2,unit="LENGTH")
	bpy.types.Object.zclip_buf = bpy.props.FloatProperty(default=0.5,name="Buffer", precision=2,unit="LENGTH")

	bpy.app.handlers.scene_update_post.append(ZClipUpdate)

def unregister():
	bpy.utils.unregister_class(ZClipOperator)
	bpy.utils.unregister_class(ZClipPanel)
	
	del bpy.types.Object.zclip_newz
	del bpy.types.Object.zclip_oldz
	del bpy.types.Object.zclip_buf
	
	bpy.app.handlers.scene_update_post.remove(ZClipUpdate)


if __name__ == "__main__":
	register()