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
	"name": "GCODE PEN format",
	"author": "macouno",
	"version": (1, 0),
	"blender": (2, 69, 0),
	"location": "File > Import-Export > Gcode Pen",
	"description": "Import-Export Gcode Pen files",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"support": 'TESTING',
	"category": "Import-Export"}


import os, math
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
	

class ExportGCODEPEN(Operator, ExportHelper):
	'''Save STL triangle mesh data from the active object'''
	bl_idname = "export_mesh.gcode_pen"
	bl_label = "Export Gcode Pen"

	filename_ext = ".gcode"
	filter_glob = StringProperty(default="*.gcode", options={'HIDDEN'})
	
	newlines = []
	dEdges = []
	bm = None
	dvert_lay = None
	Arot = 0.0
	slice = {'nr': 0, 'position': 0.0}
	percentage = 0.0
	Anchored = False
	xyz = ''
	x= 0.0
	y = 0.0
	z = 0.0
	move = ''
	moveName = ''
	moveSpeed = 9000.0
	

	## Make the start tot the gcode
	def makeStart(self):
		self.newlines.append("""M136 (enable build progress)
M73 P0
G162 X Y F2000(home XY axes maximum)
G161 Z F900(home Z axis minimum)
G92 X0 Y0 Z-5 (set Z to -5)
G1 Z0.0 F900(move Z to '0')
G161 Z F100(home Z axis minimum)
M132 X Y Z (Recall stored home offsets for XYZ axis)
G92 X152 Y75 Z0
G1 X-112 Y-73 Z150 F3300.0 (move to waiting position)
G130 X20 Y20(Lower stepper Vrefs while heating)
M135 T0
M133 T0
G130 X127 Y127(Set Stepper motor Vref to defaults)
; Slice 0
; Position  0
; Thickness 0.2
; Width 0.4
M73 P0;
""")
		return
		
		
	# Make the end of the gcode
	def makeEnd(self):	
		self.newlines.append("""G1 Z155 F900
G162 X Y F2000
M18 X Y Z(Turn off steppers after a build)
M70 P5 (We <3 Making Things!)
M72 P1  ( Play Ta-Da song )
M73 P100 (end  build progress )
M137 (build end notification)
""")
		return

		
		
	# Find the vertex group for this vertex
	def findGroup(self,v):
		
		for g in bpy.context.active_object.vertex_groups:
		
			groupIndex = g.index
			if not groupIndex is None:
					try:
						x = v[self.dvert_lay][groupIndex]
						return g.name, g.name
					except:
						pass
					
		print('Found a vert without a group!')
		return None
		
		
		
	# Make a line of gcode for this vertex
	def makeLine(self, v, e):
	
		line = ''
		
		# Add a nice percentage counter for display on the makerbot
		prcnt =  math.floor((len(self.dEdges) / len(self.bm.edges) )* 100)
		if prcnt > self.percentage:
			self.percentage = prcnt
			line = 'M73 P'+str(prcnt)+';\n'+line
			
		# Make the line!
		line = line + 'G1' + self.xyz+' F'+str(self.moveSpeed)+'; '+self.moveName+'\n'
			
		
		# Get the specific values for this type of movement!
		self.move, self.moveName = self.findGroup(v)
		
		# Put all this in self because we want to make sure we keep it for the next move (in case it's a travel move!)
		self.xyz = ''
		self.x = round(v.co[0],3)
		self.y = round(v.co[1],3)
		self.z = round(v.co[2],3)
		self.xyz = self.xyz+' X'+str(self.x)
		self.xyz = self.xyz+' Y'+str(self.y)
		self.xyz = self.xyz+' Z'+str(self.z)
		
		# Check for the end of the print and add two fresh slices as a buffer!
		if self.moveName == 'End':
			self.slice['nr'] += 1
			self.slice['position'] += 0.2
			sliceLine = '; Slice '+str(self.slice['nr'])+'\n; Position '+str(round(self.slice['position'],2))+'\n; Thickness 0.2\n; Width 0.4\n'
			self.slice['nr'] += 1
			self.slice['position'] += 0.2
			sliceLine = sliceLine + '; Slice '+str(self.slice['nr'])+'\n; Position '+str(round(self.slice['position'],2))+'\n; Thickness 0.2\n; Width 0.4\n'
			line = sliceLine + line
			
		return line
	
	
	
	# Step through the code to be printed!
	def step(self, vert):
	
		for e in vert.link_edges:
			if not e.index in self.dEdges:
				for v in e.verts:
					if not v is vert:
						self.dEdges.append(e.index)
						self.newlines.append(self.makeLine(v,e))
						self.step(v)
						
		return
	
	
	# Execute the code
	def execute(self, context):
	
		self.newlines = []
		self.dEdges = []
		self.bm = None
		self.dvert_lay = None
		self.slice = {'nr': 0, 'position': 0.0}
		self.percentage = 0.0
		self.Anchored = False
		
		self.makeStart()
		
		# Let's go make some lines with gcode!
		self.bm = bmesh_extras.get_bmesh()
		
		# Check to see if there are any vertex groups on this mesh... they need to be there
		self.dvert_lay = self.bm.verts.layers.deform.active
		if self.dvert_lay is None:
			print('Cancelling export... no use to try without vertex groups')
			return
			
		# Here we get all the group indexes and add them to the dict!
		try:
			group = bpy.context.active_object.vertex_groups['Start']
			start_index = group.index
		except:
			print('Can not find start group... cancelling')
			return
			
		# Find the starting vert based on the index
		startV = None
		for v in self.bm.verts:
			try:
				x = v[self.dvert_lay][start_index]
				startV = v
			except:
				pass
			
		if startV:
			self.newlines.append(self.makeLine(startV,None))
			self.step(startV)
		else:
			print('Unable to retrieve start position')
		
		self.bm.free()
		self.makeEnd()
		
		fOut = self.filepath
		with open(fOut, 'w') as f:
			for line in self.newlines:
				f.write(line)
		

		return {'FINISHED'}


def menu_export(self, context):
	default_path = os.path.splitext(bpy.data.filepath)[0] + ".gcode"
	self.layout.operator(ExportGCODEPEN.bl_idname, text="Gcode Pen (.gcode)")


def register():
	bpy.utils.register_module(__name__)

	bpy.types.INFO_MT_file_export.append(menu_export)


def unregister():
	bpy.utils.unregister_module(__name__)

	bpy.types.INFO_MT_file_export.remove(menu_export)


if __name__ == "__main__":
	register()
