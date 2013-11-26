# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

bl_info = {
	"name": "GCODE format",
	"author": "macouno",
	"version": (1, 0),
	"blender": (2, 69, 0),
	"location": "File > Import-Export > Gcode",
	"description": "Import-Export Gcode files",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"support": 'TESTING',
	"category": "Import-Export"}


import os
import bpy, bmesh
from macouno import bmesh_extras
from bpy.props import (StringProperty,
					   BoolProperty,
					   CollectionProperty,
					   EnumProperty,
					   FloatProperty,
					   )
from bpy_extras.io_utils import (ImportHelper,
								 ExportHelper,
								 axis_conversion,
								 )
from bpy.types import Operator, OperatorFileListElement

# Get the float from a line segment of gcode
def gVal(input):
	input = input.replace(';','')
	return float(input[1:])
	

class ImportGCODE(Operator, ImportHelper):
	"""Load Gcode into mesh data"""
	bl_idname = "import_mesh.gcode"
	bl_label = "Import Gcode"
	bl_options = {'UNDO'}

	filename_ext = ".gcode"

	filter_glob = StringProperty(
			default="*.gcode",
			options={'HIDDEN'},
			)
	files = CollectionProperty(
			name="File Path",
			type=OperatorFileListElement,
			)
	directory = StringProperty(
			subtype='DIR_PATH',
			)

	def execute(self, context):
	
		paths = [os.path.join(self.directory, name.name)
				 for name in self.files]

		if not paths:
			paths.append(self.filepath)

		if bpy.ops.object.mode_set.poll():
			bpy.ops.object.mode_set(mode='OBJECT')

		if bpy.ops.object.select_all.poll():
			bpy.ops.object.select_all(action='DESELECT')

		for path in paths:
			objName = bpy.path.display_name(os.path.basename(path))
			print("FOUND FILE",objName)
			
			with open(path,'r') as f:
			
				slice = False
				bm = False
				me = False
				ob = False
				preI =False
				x = 0.0
				y = 0.0
				z = 0.0
				e = 0.0
				aPrev = False
				t = False
				extrusions = False
				
				
				for li, line in enumerate(f.readlines()):
				
					# Keep track of what slice we're on
					if line.startswith('; Slice'):
						
						slice = line.replace('; Slice ', '')
						slice = int(slice)
					
					# Only slices are added! The stuff before we don't need
					if not slice is False:
					
						if line.startswith('G1 '):
						
							if bm is False:
								bm = bmesh.new()
								me = bpy.data.meshes.new(objName)
								ob = bpy.data.objects.new(objName, me)
								scn =bpy.context.scene
								scn.objects.link(ob)
								ob.select = True
								scn.objects.active = ob
								
								try:
									ex = bm.verts.layers.float['extrusions']
								except KeyError:
									ex = bm.verts.layers.float.new('extrusions')

							# Lets get coordinates
							words = line.split(' ')
							t = None
							for word in words:
								if len(word) > 1:
									if word.startswith('X'):
										x = gVal(word)		
									elif word.startswith('Y'):
										y = gVal(word)
									elif word.startswith('Z'):
										z = gVal(word)
										
									elif word.endswith('\n'):
										t = word.replace('\n','')
										if t == 'move':
											t = 'Travel move'
										elif t == 'position':
											t = 'Move to start position'
										elif t == 'print':
											t = 'End of print'
										
									elif word.startswith('A'):
										aCur = gVal(word.replace(';',''))
										if aPrev:
											e = aCur - aPrev
										else:
											e = 0.0
										aPrev = aCur
											
										if li < 100:
											print(e,aCur,aPrev)
											

									
							#	Only add a point for actual defined positions
							if t:
								
								# Add a vert at the correct coords
								curV = bm.verts.new((x,y,z))
								curV[ex] = e
								curI = len(bm.verts)-1
								
								# Add the vert to the correct vertex group
								bm, group_index = bmesh_extras.add_to_group(bme=bm, verts = [curV], newGroup=False, groupName=t)
								
								# Add an edge if we can!
								if not preI is False:
									bm.edges.new([bm.verts[curI], bm.verts[preI]])
									
								
									
								# Set the previous vert index to the current index
								preI = curI
							

						
							
			if not bm is False:
				bm.to_mesh(me)
				bm.free()
				
				ob['extrusions'] = extrusions
				

		return {'FINISHED'}


class ExportGCODE(Operator, ExportHelper):
	"""Save STL triangle mesh data from the active object"""
	bl_idname = "export_mesh.gcode"
	bl_label = "Export Gcode"

	filename_ext = ".gcode"
	filter_glob = StringProperty(default="*.gcode", options={'HIDDEN'})

	# The extrusion speed for any normal move!!!
	# This is normally 0.035
	ExtrusionSpeed = FloatProperty(
			name="Extrusion speed",
			min=0.001, max=10.0,
			default=0.035,
			)

	def execute(self, context):
		from mathutils import Matrix

		global_matrix = axis_conversion(to_forward=self.axis_forward,
										to_up=self.axis_up,
										).to_4x4() * Matrix.Scale(self.global_scale, 4)

		faces = itertools.chain.from_iterable(
			blender_utils.faces_from_mesh(ob, global_matrix, self.use_mesh_modifiers)
			for ob in context.selected_objects)

		stl_utils.write_stl(self.filepath, faces, self.ascii)

		return {'FINISHED'}


def menu_import(self, context):
	self.layout.operator(ImportGCODE.bl_idname, text="Gcode (.gcode)")


def menu_export(self, context):
	default_path = os.path.splitext(bpy.data.filepath)[0] + ".gcode"
	self.layout.operator(ExportGCODE.bl_idname, text="Gcode (.gcode)")


def register():
	bpy.utils.register_module(__name__)

	bpy.types.INFO_MT_file_import.append(menu_import)
	bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
	bpy.utils.unregister_module(__name__)

	bpy.types.INFO_MT_file_import.remove(menu_import)
	bpy.types.INFO_MT_file_export.remove(menu_export)


if __name__ == "__main__":
	register()
