# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Scale by angle",
    "author": "macouno",
    "version": (0, 1),
    "blender": (2, 70, 0),
    "location": "View3D > Add > Mesh > Light",
    "description": "Grow a street light",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
	"support": 'TESTING',
    "category": "Add Mesh"}

import bpy, mathutils, math
from macouno import mesh_extras, cast_loop, scene_update
from bpy.props import FloatProperty, BoolProperty
from mathutils import Matrix


def scale_by_angle(context, scale, limit, frontal):

	if frontal:
		y = -1.0
	else:
		y = 1.0
		
	ang = mathutils.Vector((0.0,y,0.0))

	bpy.ops.object.mode_set(mode='OBJECT')
	
	ob = context.active_object
	me = ob.data
	
	# Get or make the shape key
	try:
		shapeKey = me.shape_keys.key_blocks[ob.active_shape_key_index]
	except:
		shapeKey = ob.shape_key_add(from_mix=False)
		shapeKey.name = 'Scaled'

		shapeKey = me.shape_keys.key_blocks[1]
	
	for p in me.polygons:
		
		if p.select:
			
			cent = p.center.copy()
			norm = p.normal.copy()
			if norm.length:
				
				dif = 180.0 - math.degrees(norm.angle(ang))
				dif -= limit
				
				if dif >180:
					dif = 180
				elif dif < 0.0:
					dif = 0.0

				scale = 0.4
				
				relScale = 1.0 - scale
				
				relScale = (relScale / 180.0) * dif
				
				fact = 1.0 - relScale
				
				
				for vIn in p.vertices:
					v = me.vertices[vIn]
					
					vRel = v.co - cent
					
					vRel *= fact
					
					shapeKey.data[vIn].co = vRel + cent
					
					v.co = vRel + cent

	bpy.ops.object.mode_set(mode='EDIT')
	
	return


class ScaleByAngle(bpy.types.Operator):
	"""Add a street light mesh"""
	bl_idname = "mesh.scale_by_angle"
	bl_label = "Scale by Angle"
	bl_options = {"REGISTER", "UNDO"}

	scale = FloatProperty(name='Scale', description='Scale as a factor', default=0.4, min=0.0, max=100.0, soft_min=0.0, soft_max=1000.0, step=1, precision=1)
	limit = FloatProperty(name='Limit', description='Limit the scaling angle', default=10.0, min=0.0, max=180.0, soft_min=0.0, soft_max=180.0, step=1, precision=1)
	frontal = BoolProperty(name='Frontal', description='Front', default=True)

	def execute(self, context):
		scale_by_angle(context, self.scale, self.limit, self.frontal);
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(ScaleByAngle.bl_idname, text="Scale by Angle", icon="MESH_CUBE")


def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_func)


def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)

if __name__ == "__main__":
	register()