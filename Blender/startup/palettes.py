import bpy
from bpy.props import EnumProperty, IntProperty, BoolProperty


class PaletteOperator(bpy.types.Operator):
	bl_idname = "scene.get_palettes"
	bl_label = "Get palettes"
	bl_options = {'REGISTER', 'UNDO'}
	
	entoform = BoolProperty(name='Entoform', description='Acquire a single colour from the Entoforms.com database', default=True)
	
	seed = IntProperty(name='Seed', default=1, min=0, max=1000000, soft_min=0, soft_max=1000000)	
	
	days = IntProperty(name='Days', default=1, min=0, max=365, soft_min=0, soft_max=365)
	
	# The methods we use
	types=(
		('NEW', 'recent', ''),
		('RAT', 'rating', ''),
		('POP', 'popular', ''),
		)
		
	type = EnumProperty(items=types, name='Type', description='The filter for getting the palettes', default='NEW')
	
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		from macouno import color
		if self.entoform:
			color.get_entoform_palette(self.seed)
		else:
			color.get_palettes(self.days, self.type)
		return {'FINISHED'}





class SCENE_PT_palettes(bpy.types.Panel):
	bl_label = "Palettes"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "scene"

	def draw(self, context):
		layout = self.layout

		scn = context.scene

		row = layout.row()
		row.operator("scene.get_palettes", text="Get palettes")

def register():
	bpy.utils.register_class(PaletteOperator)
	bpy.utils.register_class(SCENE_PT_palettes)


def unregister():
	bpy.utils.unregister_class(PaletteOperator)
	bpy.utils.unregister_class(SCENE_PT_palettes)


if __name__ == "__main__":
	register()