# mesh_grow.py Copyright (C) 2011, Dolf Veenvliet
#
# Extrude a selection from a mesh multiple times
#
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
	"name": "Grow",
	"author": "Dolf Veenvliet",
	"version": 1,
	"blender": (2, 5, 6),
	"api": 31847,
	"location": "View3D > Specials > Grow",
	"description": "Extrude and translate/rotate/scale multiple times",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"}
	
	
"""
Usage:

Launch from "W-menu"

Additional links:
	Author Site: http://www.macouno.com
	e-mail: dolf {at} macouno {dot} com
"""

import bpy, mathutils, math, time
from bpy.props import IntProperty, EnumProperty, FloatVectorProperty, FloatProperty, BoolProperty
from macouno import  mesh_extras, misc, falloff_curve

# Grow stuff!
class Grow():

	# Initialise the class
	def __init__(self, context, translation, rotation, rotation_falloff, scale, scale_falloff, retain, steps, debug):
		
		self.startTime = time.time()
		self.markTime = self.startTime
		self.debug = debug
		
		self.context = context
		self.ob = context.active_object
		self.selectNr = len(mesh_extras.get_selected_polygons())
		
		if not self.selectNr:
			print('Grow error no polygons selected')
			return
			
		if steps:
			self.ob['growsteps'] = 0
		
		self.factor = 0.0
		
		self.iteration = 0
		self.reachedGoal = False
		
		self.translated = 0.0
		self.currentX = 0.0
		self.averagelength = 0.0
		
		# Go into object mode for the initial stages
		bpy.ops.object.mode_set(mode='OBJECT')
		self.averageLength = mesh_extras.get_average_outer_edge_length()
		translation *= self.averageLength
		
		# Now this is an added bit only for use with entoform.py
		
		# This matrix may already be set by a previous grow function running making this shape (just being consistent)
		try:
			self.transformMatrix = mathutils.Matrix((self.ob['growmatrix'][0],self.ob['growmatrix'][1],self.ob['growmatrix'][2]))
		except:
			self.transformMatrix = mesh_extras.get_selection_matrix()
			
		# This matrix is just there to check whether the "directions" are correct
		try:
			self.checkMatrix = mathutils.Matrix((self.ob['formmatrix'][0],self.ob['formmatrix'][1],self.ob['formmatrix'][2]))
			print('GOT checkmatrix')
		except:
			self.checkMatrix = False
		
		# Make the actions
		actions = []
		actions.append({'type': 'extrude'})
		actions.append({'type': 'scale', 'vector': scale, 'falloff': scale_falloff})
		actions.append({'type': 'rotate', 'vector': mathutils.Vector(rotation), 'falloff': rotation_falloff})
		actions.append({'type': 'translate', 'vector': translation})
			
		# Add the extrude at the start (doing it this way in case we'd like to invert the list)
		#actions.insert(0, {'type': 'extrude'})
		
		# Loop through all the actions
		bpy.ops.object.mode_set(mode='EDIT')
		self.mark('startloop')
		
		while not self.reachedGoal:
		
			self.mark('step '+str(self.iteration))
			
			# Window redraw nice as a hack!
			#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
			#time.sleep(0.5)
			
			# Figure out how much to translate and where we are on the curves
			self.currentX = self.translated / translation
			self.translated += self.averageLength
			self.newX = self.translated / translation
			
			self.mark('transcal')
			
			# Lets check.. if we move beyond the wanted result in this step... we quit!
			if self.translated == translation:
				self.reachedGoal = True
			elif self.translated > translation:
				self.reachedGoal = True
				self.newX = 1.0
				break
			
			self.mark('actions')
			for action in actions:
				self.mark(action['type']+' start')
				self.spurt(action)
				self.mark(action['type']+' end')
				
			self.iteration += 1
			if steps:
				self.ob['growsteps'] = self.iteration
					
		# Save this matrix, in case we grow again...
		if retain:
			self.ob['growmatrix'] = self.transformMatrix
		else:
			try:
				del(self.ob['growmatrix'])
			except:
				pass

		self.mark('end')
		
		
		
		
	# Execute all moves in a step
	def spurt(self, action):
	
		# Extrude simply extrudes
		if action['type'] == 'extrude':
			self.extrude()
			return
		
		# Scaling is simple... no per axis value right now
		if action['type'] == 'scale':
		
			vec = action['vector']
			
			if not vec == 1.0:
			
				curve = falloff_curve.curve(action['falloff'], 'mult')
				curve.update(1.0, 0.0, vec, self.currentX, self.newX)
				vec = abs(curve.currentVal)
				del curve
				
				if not vec == 1.0:
					self.averageLength *= vec
					vec = mathutils.Vector((vec, vec, vec))
					self.scale(vec)
					
			return
		
			
		# Movement!
		if action['type'] == 'translate':
			
			vec = mathutils.Vector((0.0,0.0,self.averageLength))
			
			vLen = vec.length
			#vec *= self.transformMatrix
			vec = self.transformMatrix * vec
			vec = vec.normalized() * vLen
			
			self.translate(vec)
			return

			
		# Rotation!
		if action['type'] == 'rotate':
		
			vec = action['vector']
			leng = vec.length
				
			# No need to do anything if there's nothing to do
			if vec and leng:
			
				rotationMatrix = mathutils.Matrix(self.transformMatrix)
				
				for j in range(len(vec)):
					nr = j
					v = vec[nr]
						
					if v:
					
						curve = falloff_curve.curve(action['falloff'], 'inc')
						curve.update(0.0, 0.0, v, self.currentX, self.newX)
						v = curve.currentVal
						del curve
						
						if v:
							x = mathutils.Vector(rotationMatrix[nr])
							
							# Added for use with entoform.py only
							if self.checkMatrix and round(x.dot(mathutils.Vector(self.checkMatrix[nr])),5) <= 0.0:
								x = x.negate()
								
							self.rotate(v, x)
							
							rotMat = mathutils.Matrix.Rotation(v, 3, x)
							
							rotationMatrix = rotMat * rotationMatrix
						
				self.transformMatrix = rotationMatrix
					
			return
		
		
		
	# Extrude the selection (do not move it)
	def extrude(self):
		bpy.ops.mesh.extrude_region()
		
		
	# Move the selection (always relative to the normal)
	# val = (0, 0, 1.0)
	def translate(self, val):
		bpy.ops.transform.translate(value=val, constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional=bpy.context.tool_settings.proportional_edit, snap=bpy.context.tool_settings.use_snap, release_confirm=False)
		
		
	# Scale the selection (always relative to the normal)
	# val = (0.5, 0.5, 0.5)
	def scale(self, val):
		bpy.ops.transform.resize(value=val, constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional=bpy.context.tool_settings.proportional_edit, proportional_edit_falloff=bpy.context.tool_settings.proportional_edit_falloff, proportional_size=1, snap=bpy.context.tool_settings.use_snap, snap_target=bpy.context.tool_settings.snap_target, snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)
		
		
	# Rotate the selection (always relative to the normal)
	# val = rotation in radians
	# ax = x, y or z
	def rotate(self, val, x ,c=(False, False, False)):
		bpy.ops.transform.rotate(value=val, axis=x, constraint_axis=c, constraint_orientation='GLOBAL', mirror=False, proportional=bpy.context.tool_settings.proportional_edit, proportional_edit_falloff=bpy.context.tool_settings.proportional_edit_falloff, proportional_size=1, snap=bpy.context.tool_settings.use_snap, snap_target=bpy.context.tool_settings.snap_target, snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)
		
		
		
	# Mark this point in time and print if we want... see how long it takes
	def mark(self,desc):
		if self.debug:
			now = time.time()
			jump = now - self.markTime
			self.markTime = now
			print(desc.rjust(10, ' '),jump)		
		
		
		
	

class Grow_init(bpy.types.Operator):
	'''Grow by extruding and moving/rotating/scaling multiple times'''
	bl_idname = 'mesh.grow'
	bl_label = 'Grow'
	bl_options = {'REGISTER', 'UNDO'}
	
	# The falloffs we use
	falloffs=(
		('LIN', 'Linear', ''),
		('INC', 'Increasing', ''),
		('DEC', 'Decreasing', ''),
		('SWO', 'Swoosh',''),
		('SPI', 'Spike',''),
		('BUM', 'Bump',''),
		('SWE', 'Sweep',''),
		)
	
	# Translation
	translation = FloatProperty(name='Translation', description='Translation in Blender units', default=12.0, min=-1000.0, max=1000.0, soft_min=-1000.0, soft_max=1000.0, step=100, precision=2)

	# Rotation
	rotation = FloatVectorProperty(name="Rotation", description="Rotation in degrees", default=(0.0, 0.0, 0.0), min=math.radians(-360.0*10), max=math.radians(360.0*10), soft_min=-math.radians(360.0), soft_max=math.radians(360.0), step=500, precision=2, subtype='EULER')
	
	rotation_falloff = EnumProperty(items=falloffs, name='Falloff', description='The falloff of the rotation', default='LIN')
	
	# Scale
	scale = FloatProperty(name='Scale', description='Translation in Blender units', default=1.0, min=0.01, max=1000.0, soft_min=0.01, soft_max=1000.0, step=10, precision=2)
	
	scale_falloff = EnumProperty(items=falloffs, name='Falloff', description='The falloff of the scale', default='LIN')
	
	# Miscellaneous
	retain = BoolProperty(name='Retain matrix', description='Keep the matrix in a property', default=False)
	
	steps = BoolProperty(name='Retain steps', description='Keep the step count in a property', default=False)
	
	debug = BoolProperty(name='Debug', description='Get timing info in the console', default=False)

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH' and bpy.context.tool_settings.mesh_select_mode[0] == False and bpy.context.tool_settings.mesh_select_mode[1] == False and bpy.context.tool_settings.mesh_select_mode[2] == True)

	def execute(self, context):
		GROW = Grow(context, self.translation, self.rotation, self.rotation_falloff, self.scale, self.scale_falloff, self.retain, self.steps, self.debug) 
		return {'FINISHED'}

		

def menu_func(self, context):
	self.layout.operator(Grow_init.bl_idname, text="Grow")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_specials.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)

if __name__ == "__main__":
	register()