import bpy, bmesh
from bpy.app.handlers import persistent
from bpy.props import EnumProperty, FloatProperty

@persistent
def ZClipUpdate(context):

	# See if zclipping is enabled... if not... we don't do anything
	try:
		ob = bpy.context.active_object
		if not ob.zclip_enabled:
			return
	except:
		return

	# We need bmesh stuff... and since it isn't available when blender starts up we get it here
	from macouno import bmesh_extras
	
	bm = bmesh_extras.get_bmesh()
	
	nz = ob.zclip_newz
	oz = ob.zclip_oldz
	if not nz == oz:
		cnt = 0
		ob.zclip_oldz = nz
		b = ob.zclip_buf * 0.5
		hidden = []
		
		# Hide all verts that are too far from the z we want
		if len(bm.verts):
			for v in bm.verts:
				if abs(v.co[2] - nz) <= b:
					v.hide = False
				else:
					v.hide = True
					v.select = False
					hidden.append(v)
				
		if len(hidden) and len(bm.edges):
			for e in bm.edges:
				e.hide = False
				for v in hidden:
					if v in e.verts:
						e.hide = True
						e.select = False
						break
						
		if len(hidden) and len(bm.faces):
			for f in bm.faces:
				f.hide = False
				for v in hidden:
					if v in f.verts:
						f.hide = True
						f.select = False
						break
		

	try:
		ex = bm.verts.layers.float['extrusions']
		et = bm.edges.layers.string['types']

		for i, e in enumerate(bm.edges):
			if e.select:
				ob.edgetrusion = float(e.verts[0][ex]) / e.calc_length()
				ob.edgetype =  str(e[et], 'utf-8')
	except:
		pass
		
	bmesh_extras.put_bmesh(bm)



# Make a panel to controll mesh object zclipping
class ZClipPanel(bpy.types.Panel):
	bl_label = "ZClip visibility"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		return (ob and ob.type == 'MESH' and context.mode == 'EDIT_MESH')

	def draw(self, context):
		layout = self.layout

		scn = context.scene
		ob = context.active_object
		et = ob.edgetype
		if not et == 'None':
			print('NONE?',et)
			et = 'edgetype: '+et
			ex = 'extrusion: '+str(round(ob.edgetrusion,4))
		else:
			ex = ''
			et = 'no edge selected'
		row = layout.row()
		row.prop(ob,'zclip_enabled')
		row = layout.row()
		row.prop(ob,'zclip_newz')
		row = layout.row()
		row.prop(ob,'zclip_buf')
		row = layout.row()
		layout.label(text=ex)
		layout.label(text=et)
		
	def update(self,context):
		print('UPDATE')
		
		

def register():
	
	bpy.utils.register_class(ZClipPanel)
	
	bpy.types.Object.zclip_enabled = bpy.props.BoolProperty(default=False,name="Enabled")
	bpy.types.Object.zclip_newz = bpy.props.FloatProperty(default=0.0,name="Z", precision=3,unit="LENGTH")
	bpy.types.Object.zclip_oldz = bpy.props.FloatProperty(default=0.0,name="OLDZ", precision=3,unit="LENGTH")
	bpy.types.Object.zclip_buf = bpy.props.FloatProperty(default=0.25,name="Buffer", precision=3,unit="LENGTH")
	
	bpy.types.Object.edgetrusion = bpy.props.FloatProperty(default=0.00,name="Edgetrusion", precision=3,unit="LENGTH")
	bpy.types.Object.edgetype = bpy.props.StringProperty(default='None',name="EdgeType")

	bpy.app.handlers.scene_update_post.append(ZClipUpdate)

def unregister():
	bpy.utils.unregister_class(ZClipPanel)
	
	del bpy.types.Object.zclip_enabled
	del bpy.types.Object.zclip_newz
	del bpy.types.Object.zclip_oldz
	del bpy.types.Object.zclip_buf
	
	del bpy.types.Object.edgetrusion
	del bpy.types.Object.edgetype
	
	bpy.app.handlers.scene_update_post.remove(ZClipUpdate)


if __name__ == "__main__":
	register()