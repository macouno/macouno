# Entoform.py Copyright (C) 2011, Dolf Veenvliet
#
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
	"name": "Entoform",
	"author": "Dolf Veenvliet",
	"version": 1,
	"blender": (2, 5, 6),
	"api": 31847,
	"location": "object > Entoform ",
	"description": "Build an entoform",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Object"}

"""
Usage:

Launch from Object menu 


Additional links:
	Author Site: http://www.macouno.com
	e-mail: dolf {at} macouno {dot} com
"""

import bpy, mathutils, math, cProfile, colorsys, datetime, time
from mathutils import geometry
from bpy.props import StringProperty, IntProperty, BoolProperty
from macouno import mesh_extras, misc, colour, select_faces, falloff_curve, liberty

# Make it as a class
class Entoform():

	# Initialise the class
	def __init__(self, context, dnaString, subdivide, keepgroups, finish, run):
	
		if not run:
			return
	
		# Start by setting up some default vars and such (in sepparate function because it's a bit much)
		self.setup(context, dnaString, keepgroups)
		
		# GO make the DNA strings
		self.createDNA()
		
		# Make the base group
		baseGroups = self.makeBaseGroup()
		
		for string in self.dna['strings']:
			self.executeDNA(string, baseGroups, 1.0)
				
		# Make sure we're shaded smoothly
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.shade_smooth()
		
		# Add self shadow (after the first subdivision)!
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')
		bpy.ops.paint.self_shadow(contrast=3.0,method='EDG',normalize=True)
		
		# Subsurf the first time if required
		if subdivide:
		
			# Split the edges!
			'''
			bpy.ops.object.modifier_add(type='EDGE_SPLIT')
			mod = self.ob.modifiers[0]
			mod.use_edge_angle = False
			mod.use_edge_sharp = True
			bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")
			'''
			
			bpy.ops.object.mode_set(mode='OBJECT')
			bpy.ops.object.modifier_add(type='SUBSURF')
			mod = self.ob.modifiers[0]
			mod.levels = subdivide
			bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
		
		bpy.ops.object.mode_set(mode='EDIT')
		
		if finish:
			self.finish(context)
			
		self.reset(context)
		
		
		
	# Go grow something!
	def executeDNA(self, string, baseGroups, baseWeight):
		
		'''
		if string['number'] >= 1:
			#if string['number'] in [0,1,3]:
			return
		
		elif string['number'] == 5 or string['number'] == 6:
			return	
		'''
		# Redraw hack to see what is happening
		# bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
		
		newGroups, formmatrix, growmatrices = self.makeAffectedGroups(string, baseGroups)
		groupLen = len(newGroups)\
		
		pad = str(' ').rjust(string['level'], ' ')
		
		idText = 'limb '+misc.nr4(string['number'])+' '+string['name'].ljust(10, ' ')
		print(pad,idText)
		
		# only if we made a group with something in it do we continue
		if not groupLen:
			print('  - No group!')
		else:
				
			# Loop through all the groups
			for i, group in enumerate(newGroups):
			
				# The step number to print out
				stepText = misc.nr4(i+1)+' of '+misc.nr4(groupLen)
			
				# We need a check matrix only if we're not on the head or body
				if string['name'] == 'head' or string['name'] == 'body' or True:
					try:
						del(self.ob['formmatrix'])
					except:
						pass
				# If not... then just try to get rid of it
				else:
					self.ob['formmatrix'] = formmatrix
			
				# Body gets a set matrix (so it grows nice and straight)
				if string['name'] == 'head':
					growmatrix = mathutils.Matrix(((1.0,0.0,0.0),(0.0,0.0,1.0),(0.0,-1.0,0.0))).transposed()
					
				# Head gets a set matrix (so it grows nice and straight)
				elif string['name'] == 'body':
					growmatrix = mathutils.Matrix(((-1.0,0.0,0.0),(0.0,0.0,1.0),(0.0,1.0,0.0))).transposed()
					
				# In all other cases the matrix can be dealt with by the grow addon
				else:
					growmatrix = growmatrices[i]
					
				self.ob['growmatrix'] = growmatrix
			
				# Select a group
				select_faces.none()
				select_faces.in_group(group)
				
				# No need to continue if we have no selected faces
				if not mesh_extras.contains_selected_item(self.me.faces):
					print(pad,'skip ',stepText,'no selection',string['action']['name'])
					
				else:
					
					a = string['action']
					
					if a['type'] == 'grow':
							
						# Check for mirroring
						right = mathutils.Vector((1.0,0.0,0.0))
						check = mathutils.Vector(growmatrix[2])
						
						# If we're aiming left we "invert" the rotation
						if right.dot(check) < 0.0:
							rot = mathutils.Vector((-a['rotation'][0],a['rotation'][1],-a['rotation'][2]))
						else:
							rot = a['rotation']
					
						# Add relative intensity here (half the original + half the weight)
						weight = baseWeight * self.getWeight(groupLen, a['scalin'])
						
						trans = a['translation']
						#trans = self.applyIntensity(a['translation'], weight, 'float')
						#rot = self.applyIntensity(rot, weight, 'inc')
					
					if a['type'] == 'grow' and trans == 0.0:
					
						print(pad,'skip ',stepText,'too short',trans,'from',a['translation'])
					
					else:
					
						print(pad,'step ',stepText,a['name'])
						#print(self.applyIntensity(a['push'], weight, 'float'))
						
						bpy.ops.object.mode_set(mode='EDIT')
						
						if a['type'] == 'bump':
						
							bpy.ops.mesh.bump(
								type=a['bumptype'],
								scale=a['bumpscale'],
								steps=True,
								)
								
						else:
						
							bpy.ops.mesh.grow(
								translation=trans,
								rotation=rot,
								rotation_falloff=a['rotation_falloff'],
								scale=a['scale'],
								scale_falloff=a['scale_falloff'],
								retain=True,
								steps=True,
								debug=False,
								)
							
						bpy.ops.object.mode_set(mode='OBJECT')
							
						
						select_faces.none()
						select_faces.in_group(group)
						
						self.applyGrowthColor(a)
						if a['type'] == 'grow':
							self.applyGrowthCrease(a)
						
						# Remove new stuff from all but the current group
						self.cleanGroup(group)
						
						# Keep track of how much steps we've taken
						self.dnaStep += 1
						
						# If there's a sub
						if len(string['strings']):
							for s in string['strings']:
								#print('going sub', string['name'], s['name'])
								self.executeDNA(s, [group], weight)
		
		
		
	def createDNA(self):
	
		# Make the color palette
		if self.options['palettes']:
			self.options['basecolor'] = self.choose('select', 'palette', 'base color')
			colour.setBaseColor(self.options['basecolor'])
			
			print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
		
		# Make the head
		print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
		print((self.stringCount+1),"Making nr",(self.stringCount+1),"DNA string for the head\n")
		
		# Start with all directions
		self.options['local_directions'] = self.options['directions']
		selection = self.getSelection('head')
		
		action = self.makeAction(selection, 'head')
		string = {'name': 'head', 'action':action, 'selection':selection, 'strings':[], 'level':1,'number':self.stringCount}
		
		self.dna['strings'].append(string)
		self.stringCount += 1
		
		
		# Make eyes on the head!
		print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
		print((self.stringCount+1),"Making nr",(self.stringCount+1),"DNA string for eyes\n")
		
		selection = self.getSelection('eyes')
		action = self.makeAction(selection, 'eyes')
		
		string = {'name': 'eyes', 'action':action, 'selection':selection, 'strings':[], 'level':2,'number':self.stringCount}
		
		self.dna['strings'][0]['strings'].append(string)
		self.stringCount += 1


		# Mirror the action in case it's left or right
		if selection['type'] == 'direction' and (selection['vector'] == mathutils.Vector((1.0,0.0,0.0)) or selection['vector'] == mathutils.Vector((-1.0,0.0,0.0))):
		
			string = self.mirrorDNA(action, selection, 2)
			
			self.dna['strings'][0]['strings'].append(string)
			
			
			
		# SUB HEAD!
		print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
		print((self.stringCount+1),"Making nr",(self.stringCount+1),"DNA string for sub head\n")
		
		selection = self.getSelection('sub head')
		action = self.makeAction(selection, 'bump')
		
		string = {'name': 'sub head', 'action':action, 'selection':selection, 'strings':[], 'level':2,'number':self.stringCount}
		
		self.dna['strings'][0]['strings'].append(string)
		self.stringCount += 1


		# Mirror the action in case it's left or right
		if selection['type'] == 'direction' and (selection['vector'] == mathutils.Vector((1.0,0.0,0.0)) or selection['vector'] == mathutils.Vector((-1.0,0.0,0.0))):
		
			string = self.mirrorDNA(action, selection, 2)
			self.dna['strings'][0]['strings'].append(string)
			
		
		
		# Make the body
		print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
		print((self.stringCount+1),"Making nr",(self.stringCount+1),"DNA string for the body\n")
		
		self.options['local_directions'] = self.options['directions']
		selection = self.getSelection('body')
		
		action = self.makeAction(selection, 'body')
		
		string = {'name': 'body', 'action':action, 'selection':selection, 'strings':[], 'level':1,'number':self.stringCount}
		
		self.dna['strings'].append(string)
		self.stringCount += 1
		
		
		
		# Make a tail!
		print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
		print((self.stringCount+1),"Making nr",(self.stringCount+1),"DNA string for the tail\n")
		
		selection = self.getSelection('tail')
		action = self.makeAction(selection, 'tail')
		
		string = {'name':'tail', 'action':action, 'selection':selection, 'strings':[], 'level':2,'number':self.stringCount}
		
		self.dna['strings'][1]['strings'].append(string)
		self.stringCount += 1
		
		
		
		# Make some legs (well hopefully)
		print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
		print((self.stringCount+1),"Making nr",(self.stringCount+1),"DNA string for the legs\n")
		
		selection = self.getSelection('legs')
		
		action = self.makeAction(selection, 'legs')
		#action['translation'] *= 2
		
		string = {'name':'left legs', 'action':action, 'selection':selection, 'strings':[], 'level':2,'number':self.stringCount}
		
		self.dna['strings'][1]['strings'].append(string)
		self.stringCount += 1
		
		# Mirror the legs
		string = self.mirrorDNA(action, selection, 3)
		self.dna['strings'][1]['strings'].append(string)
		
		
		
		# Lower legs
		print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
		print((self.stringCount+1),"Making nr",(self.stringCount+1),"DNA string for the lower legs\n")
		
		selection = self.getSelection('lowerlegs')
		action = self.makeAction(selection, 'lower legs')
		#action['translation'] *= 2
		
		string = {'name':'lower legs', 'action':action, 'selection':selection, 'strings':[], 'level':3,'number':self.stringCount}
		self.dna['strings'][1]['strings'][1]['strings'].append(string)
		self.stringCount += 1
		
		string = self.mirrorDNA(action, selection, 3)
		self.dna['strings'][1]['strings'][2]['strings'].append(string)
		
		
		
		# SUB body!
		print("\n - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n")
		print((self.stringCount+1),"Making nr",(self.stringCount+1),"DNA string for the tail\n")
		
		selection = self.getSelection('sub body')
		action = self.makeAction(selection, 'bump')
		
		string = {'name':'sub body', 'action':action, 'selection':selection, 'strings':[], 'level':2,'number':self.stringCount}
		
		self.dna['strings'][1]['strings'].append(string)
		self.stringCount += 1
		
		# Mirror the action in case it's left or right
		if selection['type'] == 'direction' and (selection['vector'] == mathutils.Vector((1.0,0.0,0.0)) or selection['vector'] == mathutils.Vector((-1.0,0.0,0.0))):
			
			string = self.mirrorDNA(action, selection, 2)
			self.dna['strings'][1]['strings'].append(string)	
		
		print("\n - - - DONE MAKING DNA - - - LETS GO GROW SOMETHING - - -\n")
		
		
	
	# Take a dna's action and selection and mirror the vector
	def mirrorDNA(self, action, selection, level):
	
		a = action.copy()
		s = selection.copy()
		
		s['vector'] = mathutils.Vector(s['vector']).copy()
		s['vector'][0] = -s['vector'][0]
		
		self.cleanDirections(s['vector'])
		
		str = {'name':'mirrored', 'action': action, 'selection': s, 'strings': [], 'level':level,'number':self.stringCount}
		
		self.stringCount += 1
		return str
		
		
		
	# Make an action for the dna string
	def makeAction(self, selection, style='shape'):
	
		if style == 'eyes':
			action = {
				'name':style,
				'type': 'bump',
				'bumptype': 'BUM',
				'bumpscale': 0.5, 
				'vertexcolor': (0.0,0.0,0.0),
				'jointcolor': (1.0,1.0,1.0),
				'colorstyle': 'hard',
				'crease': self.choose('float', 'crease', 'crease'),
				'sub': False,
				}
				
		elif style == 'bump' or selection['type'] == 'loops':
		
			action = {
				'name':style,
				'type': 'bump',
				'bumptype': self.choose('select','bumptypes','bump type'),
				'bumpscale': self.choose('float','bumpscale','bump factor'),
				'vertexcolor': self.choose('select','palette','vertex color'),
				'jointcolor': self.choose('select','palette','joint color'),
				'colorstyle': self.choose('select','colorstyles','color style'),
				'crease': self.choose('float', 'crease', 'crease'),
				'sub': False,
				}
		
		else:
	
			axis = 'all'
			
			print('\n    style = ',style,'\n')
			
			if style == 'head' or style == 'body' or style == 'tail':
				axis = 'x'
			
			action = {
				'name':style,
				'type': 'grow',
				'translation':					self.choose('float', 'translate', 'translation'),
				'rotation':							self.makeRotationVector(axis),
				'rotation_falloff':				self.choose('select', 'falloffs', 'rotation falloff'),
				'scale':								self.choose('float', 'scale', 'scale'),
				'scale_falloff':					self.choose('select', 'falloffs', 'scale falloff'),
				'vertexcolor':					self.choose('select','palette', 'vertex color'),
				'jointcolor': 						self.choose('select','palette','joint color'),
				'colorstyle': 					self.choose('select','colorstyles','color style'),
				'crease':							self.choose('float', 'crease', 'crease'),
				'scalin':								'preset',
				'sub':									False,
				}
		
		return action
		
		
		
	# Set the intensity for a vector
	def applyIntensity(self, vector, intensity, mode):
	
		if mode == 'float':
			return vector * intensity
	
		if mode == 'int':
			return math.ceil(vector * intensity)
		
		vector = mathutils.Vector((vector[0], vector[1], vector[2]))
		
		if mode == 'inc':
			vector *= intensity
		else:
			for i, v in enumerate(vector):
				if v > 1.0:
					vector[i] = ((v-1.0) * intensity) + 1.0
				elif v < 1.0:
					vector[i] = 1.0 - ((1.0 - v) * intensity)
		
		return vector
		
		
		
	# Apply a vertex colour to a vertex group
	def applyGrowthColor(self, a):
	
		# Just apply the vertex colour to all the verts if it applies... easy!
		if self.options['palettes']:
		
			vec = list(a['vertexcolor'])
			selFaces = []
			
			for f in self.ob.data.faces:
			
				if f.select:
					selFaces.append(f)
					
					if a['colorstyle'] == 'soft':
						for v in f.vertices:
							self.applyColorToVert(v, vec)
							
					else:
						self.applyColorToFace(f.index, vec)
						
			select_faces.outermost()
			
			vec = list(a['jointcolor'])
			
			selVerts = []
			outFaces = []
			
			for f in self.ob.data.faces:
			
				if f.select:
					if a['colorstyle'] == 'soft':
						for v in f.vertices:
							self.applyColorToVert(v, vec)
					else:
						selVerts.extend(f.vertices)
						outFaces.append(f)
						self.applyColorToFace(f.index, vec)
						
			# Lets make some sharp edges
			if  a['type'] == 'bump' and a['colorstyle'] == 'hard':
			
				# Check every edge
				for e in self.ob.data.edges:
				
					v0 = e.vertices[0]
					v1 = e.vertices[1]
					
					# If both verts in the edge are selected... this could be sharp
					if v0 in selVerts and v1 in selVerts:
						ond = 0
						snd = 0
						
						# See how many faces this edge is part of
						for f in outFaces:
							if v0 in f.vertices and v1 in f.vertices:
								ond += 1
								
						for f in selFaces:
							if not f in outFaces:
								if v0 in f.vertices and v1 in f.vertices:
									snd += 1
								
						# If the edge is only part of one seleced face it's on the outside
						if ond == 1: # and snd == 1:
							e.crease = 1.0
							'''
							sharp = 0
							pole = 1
							
							for ec in self.ob.data.edges:
								if not ec == e:
									ecVerts = ec.vertices
									if v0 in ecVerts or v1 in ecVerts:
										pole += 1
										if ec.use_edge_sharp:
											sharp += 1
						
							if pole == 4 and sharp < 2:
								e.use_edge_sharp = True
							'''
						
			# Set the selection of faces back to the original
			for f in selFaces:
				f.select = True
				
					
					
	def applyGrowthCrease(self, a):
		
		# LETS LOOK AT CREASES!
		vec = a['crease']
		
		# Now we want to find out how many steps we made
		steps = self.ob['growsteps']
		if steps:
			
			# Loop through all the steps
			for i in range(int(steps)):
			
				select_faces.outermost(True)		
			
				# Find all the selected vertices
				selFaces = mesh_extras.get_selected_faces()
				selVerts = []
				for f in selFaces:
					selVerts.extend(f.vertices)
				
				# Loop through all edges
				for e in self.me.edges:
				
					eVerts = e.vertices
					
					# If an edge has only 1 selected vert... it's "long" and on the outside of the selection
					intersection = [v for v in e.vertices if v in selVerts]

					if len(intersection) == 1 and e.crease < 1.0:
						e.crease = vec
						
						
						
	# Apply a color to a face for a harsh transition
	def applyColorToFace(self, fInd, vCol):
	
		# Get the faces
		face = bpy.context.active_object.data.faces[fInd]
		vColFace = self.me.vertex_colors.active.data[fInd]
	
		vColFace.color1 = vCol
		vColFace.color2 = vCol
		vColFace.color3 = vCol
		if len(face.vertices) == 4:
			vColFace.color4 = vCol
			
					
					
	# Apply a vertex colour to a vert
	def applyColorToVert(self, vInd, vCol):
		
		# Get the faces
		for f in bpy.context.active_object.data.faces:
			if vInd in f.vertices:
				vColFace = self.me.vertex_colors.active.data[f.index]
			
				for r, v in enumerate(f.vertices):
				
					if v == vInd:
					
						if not r:
							vColFace.color1 = vCol
						elif r == 1:
							vColFace.color2 = vCol
						elif r == 2:
							vColFace.color3 = vCol
						elif r == 3:
							vColFace.color4 = vCol
							
						break
	
	
	
	# Make a section type for the dna string	
	def getSelection(self, type='none'):
		
		selection = {
			'type': 'direction',
			'area': 'area',
			'vector': mathutils.Vector(),
			'divergence': math.radians(90),
			'method': 'generated'
			}
		
		## HEAD AND BODY
		if type == 'head' or type == 'body' or type == 'tail' or type == 'legs' or type == 'lowerlegs':

			if type == 'head':
				selection['vector'] = mathutils.Vector((0.0,-1.0,0.0))
				
			elif type == 'body' or type == 'tail':
				selection['vector'] = mathutils.Vector((0.0,1.0,0.0))
				
			elif type == 'legs':
				selection['vector'] = mathutils.Vector((1.0,0.0,0.0))
				selection['area'] = 'faces'
				
			elif type == 'lowerlegs':
				selection['vector'] = self.choose('select', 'local_directions', 'selection direction')
				selection['type'] = 'joint'
				
			if type == 'tail' or type == 'legs':
				selection['divergence'] = self.choose('float', 'divergence', 'directional divergence')
				
			# Remove the opposite!
			self.cleanDirections(selection['vector'])
			
			selection['method'] = 'forced'
			
			
		elif type == 'eyes':
		
			
			selection['type'] = self.choose('select', 'selectioneyes', 'selection type')
			selection['area'] = 'faces'
		
			selection['method'] = 'limited'
				
		# Now we just pick what's nice
		else:
			
			selection['type'] = self.choose('select', 'selectiontypes', 'selection type')
			
			if selection['type'] == 'all':
				selection['area'] = 'faces'
			
			elif selection['type'] == 'direction':
				selection['vector'] = self.choose('select', 'local_directions', 'selection direction')
				self.cleanDirections(selection['vector'])
				
				selection['area'] = self.choose('select', 'areatypes', 'area for selection')
				selection['divergence'] =  self.choose('float', 'divergence', 'directional divergence')
				
			elif selection['type'] == 'liberal':
				selection['area'] = 'faces'
				
			elif selection['type'] == 'checkered':
				selection['area'] = 'faces'
				
			elif selection['type'] == 'loops':
				selection['frequency'] = self.choose('select', 'frequencies', 'loop frequencies')
					
			elif selection['type'] == 'tip':
				selection['area'] = self.choose('select', 'areatypes', 'area for selection')
					
			elif selection['type'] == 'joint':
				selection['vector'] = self.choose('select', 'local_directions', 'selection direction')
				self.cleanDirections(selection['vector'])
			
				selection['divergence'] = self.choose('float', 'divergence', 'directional divergence')
					
					
		if selection['area'] == 'faces':
			selection['limit'] =  self.choose('int', 'limit', 'selection limit')
			
		selection['formmatrix'] = ''
		selection['growmatrices'] = []
	
		return selection
		
		
		
	# Make a rotation vector
	def makeRotationVector(self, axis='all'):
		
		# For the body head and tail we only rotate up and down
		if axis == 'x':
			return mathutils.Vector((self.choose('float', 'rotation', 'X rotation'),0.0,0.0))
	
		vector = mathutils.Vector((
			self.choose('float', 'rotation', 'X rotation'),
			self.choose('float', 'rotation', 'Y rotation'),
			self.choose('float', 'rotation', 'Z rotation')
			))
	
		return vector
		
		
		
	# Remove the items in the current group from all others
	def cleanGroup(self, group):
	
		bpy.ops.object.mode_set(mode='EDIT')
		self.ob.vertex_groups.active_index = group.index
		
		# Make sure the entire group is selected
		bpy.ops.mesh.select_all(action='DESELECT')
		self.ob.vertex_groups.active_index = group.index
		bpy.ops.object.vertex_group_select()
		
		# Set editing to vert mode before selecting less
		bpy.ops.wm.context_set_value(data_path='tool_settings.mesh_select_mode', value="(True, False, False)")
		bpy.ops.mesh.select_less()
		
		# Set editing back to face mode
		bpy.ops.wm.context_set_value(data_path='tool_settings.mesh_select_mode', value="(False, False, True)")
		
		for g in self.newGroups:
			if g.index != group.index:
				self.ob.vertex_groups.active_index = g.index
				bpy.ops.object.vertex_group_remove_from(all=False)
				
		bpy.ops.object.mode_set(mode='OBJECT')
		
		
		
	# Make all the faces that are affected selected and return them as a list
	def makeAffectedGroups(self, string, baseGroups):
			
		selection = string['selection']
		newGroups = []
		formmatrix = mathutils.Matrix()
		growmatrices = []
		
		# Deselect all faces to start clean!
		select_faces.none()
		
		# Select everything in the base groups
		for g in baseGroups:
			select_faces.in_group(g,True)
			
		#print('in_group',len(mesh_extras.get_selected_faces()))
			
		# If nothing is selected there's nothing to do
		if mesh_extras.contains_selected_item(self.me.faces):
		
			# Select the faces at the tip in a certain direction
			if selection['type'] == 'joint' or selection['type'] == 'tip':
			
				select_faces.innermost()
					
				if mesh_extras.contains_selected_item(self.me.faces):
					
					if selection['type'] == 'joint':
					
						select_faces.connected(True)
						
						selCnt = len(mesh_extras.get_selected_faces())
						nuCnt = selCnt
						div = selection['divergence']
						
						# If the nr of faces selected isn't diminished... we select less!
						while selCnt and selCnt == nuCnt and div > 0.1:
						
							select_faces.by_direction(selection['vector'],div)
							div = div * 0.75
							selFaces = mesh_extras.get_selected_faces()
							nuCnt = len(selFaces)
							
						# Check for opposing normals.. .cause they should not be there!
						for f1 in selFaces:
							if f1.select:
								f1No = f1.normal
								for f2 in selFaces:
									if f2.select and not f1 is f2:
										f2No = f2.normal
										ang = f2No.angle(f1No)
										if ang > math.radians(120):
											f1.select = False
											break
						
						selFaces = mesh_extras.get_selected_faces()
						nuCnt = len(selFaces)
							
						if nuCnt == selCnt:
							select_faces.none()
					
					# If we have selected faces... we can add em to a new group
					newGroups, formmatrix, growmatrices = self.addToNewGroups(string, newGroups, growmatrices)
					
			
			# Select by pi (fake random)
			elif selection['type'] == 'liberal':
			
				select_faces.liberal(self.dnaString)
				
				# If we have selected faces... we can add em to a new group
				newGroups, formmatrix, growmatrices = self.addToNewGroups(string, newGroups, growmatrices)
				
				
			# Select all loops in the group
			elif selection['type'] == 'loops':
				
				select_faces.connected()
				self.deselectUnGrouped()
				
				step = 0
				
				# As long as something is selected, we can continue
				while mesh_extras.contains_selected_item(self.ob.data.faces):
					
					select_faces.connected()
					self.deselectGrouped(baseGroups)
					
					# Skip selection just in case
					if not step % selection['frequency']:
						
						# If we have selected faces... we can add em to a new group
						newGroups, formmatrix, grw = self.addToNewGroups(string, newGroups, growmatrices)
						growmatrices.extend(grw)
						
					step += 1
					
				print(step)
				
				
			# Select by direction
			elif selection['type'] == 'direction':

				select_faces.by_direction(selection['vector'],selection['divergence'])
				
				newGroups, formmatrix, growmatrices = self.addToNewGroups(string, newGroups, growmatrices)
				
			# All!
			else:
				newGroups, formmatrix, growmatrices = self.addToNewGroups(string, newGroups, growmatrices)
				
		return newGroups, formmatrix, growmatrices
		
		
	
	# Deselect all the faces that are not in a group
	def deselectUnGrouped(self):
	
		# Get the faces (and go into object mode)
		faces = mesh_extras.get_selected_faces()
		
		if len(faces):
		
			for f in faces:
				if f.select:
				
					inGroup = True
					
					# See all the verts (all should be in the group!)
					for v in f.vertices:
					
						found = False
						vert = self.ob.data.vertices[v]
						vertGroups = vert.groups
						for g in vert.groups:
							if g.weight:
								found = True
								
						if not found:
							inGroup = False
							
					if not inGroup:
						f.select = False
		
						
		
	# Deselect all faces that are already grouped, but not in the baseGroups
	def deselectGrouped(self, baseGroups):
	
		# Get the faces (and go into object mode)
		faces = mesh_extras.get_selected_faces()
		
		if len(faces):
						
			# First lets make sure the faces are in the current base groups
			for g in baseGroups:
			
				# Check all selected faces
				for f in faces:
					if f.select:
					
						inGroup = True
						
						# See all the verts (all should be in the group!)
						for v in f.vertices:
						
							found = False
							vert = self.ob.data.vertices[v]
							vertGroups = vert.groups
							for vg in vert.groups:
								if vg.group == g.index:
									found = True
							
							if not found:
								inGroup = False
								
						if not inGroup:
							f.select = False
						
			faces = mesh_extras.get_selected_faces()
			
			if len(faces):
	
				for g in self.newGroups:
					if not g in baseGroups:
						
						# Check all selected faces
						for f in faces:
							if f.select:
							
								inGroup = True
								
								# See all the verts (all should be in the group!)
								for v in f.vertices:
								
									found = False
									vert = self.ob.data.vertices[v]
									vertGroups = vert.groups
									for vg in vert.groups:
										if vg.group == g.index:
											found = True
									
									if not found:
										inGroup = False
										
								if inGroup:
									f.select = False
				
		
		
	# Adding the current selection to a new group
	def addToNewGroups(self, string, newGroups, growmatrices=[]):
	
		selection = string['selection']
		self.doubleCheckSelection(selection)
	
		faces = mesh_extras.get_selected_faces()
		
		formmatrix = mathutils.Matrix()
		growmatrices = []
		
		if len(faces):
		
			verts = []
			inds = []
			for f in faces:
				for v in f.vertices:
					if not v in inds:
						inds.append(v)
						verts.append(self.me.vertices[v])

			# NOW WE GO MAKE THE GROUPS
			if len(verts):

				weights = self.makeWeights(verts)
				
				formmatrix = mesh_extras.get_selection_matrix(faces)
				
				# If we do this per area, we want the entire area to be part of one group
				if selection['area'] == 'area':
					growmatrices.append(formmatrix)
					newGroup = self.ob.vertex_groups.new(string['name']+'.'+selection['type'])
					newGroups.append(newGroup)
					self.newGroups.append(newGroup)
					
					for v in verts:
							newGroup.add([v.index], 1.0, 'REPLACE')
					
				# If we have it per face, we need sepparate weights and groups
				elif selection['area'] == 'faces':
				
					if len(faces):
					
						for i, f in enumerate(faces):
							growmatrices.append(mesh_extras.get_selection_matrix([f]))
							newGroup = self.ob.vertex_groups.new(string['name']+'.'+selection['type']+'.'+misc.nr4(i))
							newGroups.append(newGroup)
							self.newGroups.append(newGroup)
							
							vertList = f.vertices
							
							for i,v in enumerate(verts):
								ind = v.index
								if ind in vertList:
									newGroup.add([v.index], weights[i], 'REPLACE')

								
		return newGroups, formmatrix, growmatrices
		
		
		
	# make the base group that we're working with
	def makeBaseGroup(self):

		newGroup = self.ob.vertex_groups.new('base')
		self.ob.vertex_groups.active_index = newGroup.index
		
		baseGroupList = [newGroup]
		self.newGroups.append(newGroup)
		
		vList = [v.index for v in self.ob.data.vertices]
		newGroup.add(vList, 1.0, 'REPLACE')
			
		return baseGroupList
		
		
		
	# Just some nice checks to do with selections
	def doubleCheckSelection(self, selection):
		
		# Make sure there's never more than 12 faces we grow out of
		if selection['area'] == 'faces':
			select_faces.limit(selection['limit'], self.dnaString)
				
		# If we still have something selected, then we need to check for Islands (only one coninuous island should be selected)
		if selection['type'] == 'direction' and selection['area'] == 'area' and mesh_extras.contains_selected_item(self.me.faces):
			self.checkForIslands(selection['vector'])

			
	
	
	# Make sure only one "island" is selected
	def checkForIslands(self, vector):
		
		faces = mesh_extras.get_selected_faces()
		
		# Find the face furthest along the vector
		max = 0.0
		closestFace = 0
		closestVerts = 0
		for i,f in enumerate(faces):
			dist = vector.dot(f.center)
			if dist > max or not i:
				max = dist
				closestFace = f
				closestVerts = f.vertices
			
		# Find the faces connected to this one!
		connectedFaces = [closestFace]
		connectedVerts = list(closestVerts)
		foundNew = True
		
		# As long as we can find connected faces we continue
		while foundNew:
			foundNew = False
			
			for f in faces:
				addThis = False
				# If we haven't done this one yet
				if not f in connectedFaces:
				
					intersection = [v for v in f.vertices if v in connectedVerts]
					if len(intersection):
						addThis = True
						
				if addThis:
					foundNew = True
					connectedFaces.append(f)
					connectedVerts.extend(f.vertices)
					
		# Deselect disconnected faces
		for f in faces:
			if not f in connectedFaces:
				f.select = False
					
		
		
	# Make relative weights for the verts
	def makeWeights(self, verts):
		
		cen = mathutils.Vector()
	
		for v in verts:
			cen += v.co
		cen *= (1.0/len(verts))
		
		# Find the minimum and maximum distance from the centre
		min = 0.0
		max = 0.0
		distances = []
		for i, v in enumerate(verts):
			dist = (v.co - cen).length
			distances.append(dist)
			if not i or dist < min:
				min = dist
			if not i or dist > max:
				max = dist
				
		max = max - min
		
		if max > 0.0:
			factor = (1.0 / max)
		else:
			factor = 1.0
		
		# Make the weights
		weights = []
		for i, v in enumerate(verts):
			weight = (max - (distances[i] - min)) * factor
			weights.append(weight)
			
		return weights
		
		
		
	# Get the weight of the current selection
	def getWeight(self, groupLen, scalin):
	
		weight = 1.0
		
		# If we're applying the weight based on the edge, we find the shortest edge
		if scalin == 'edge':
		
			short = 0.0
			check = 0
			bpy.ops.object.mode_set(mode='OBJECT')
			
			# Find the shortest edge
			for e in self.ob.data.edges:
				if e.select == True:
					v0 = self.ob.data.vertices[e.vertices[0]]
					v1 = self.ob.data.vertices[e.vertices[1]]
					
					ed = v1.co - v0.co
					leng = ed.length
					
					if leng < short or not check:
						short = leng
						check = 1
						
			weight *= short
		
		# If we're doing multiple groups, we find out the distance from the centre of the group
		if groupLen > 1:
		
			bpy.ops.object.mode_set(mode='EDIT')
			groupId = self.ob.vertex_groups.active_index
			
			verts = mesh_extras.get_selected_vertices()
			vLen = len(verts)
			
			if vLen:
				w = 0.0
				
				for v in verts:
					for g in v.groups:
						if g.group == groupId:
							w += g.weight
					
				w *= (1.0/vLen)
			
				weight *= w
			
		return weight
		
		
		
	# Remove a specific direction from the dict and rebuild it
	def cleanDirections(self, direction):
	
		directions = self.options['local_directions']
	
		# We actually remove the negated direction (can't grow backwards!)
		direction = mathutils.Vector((-direction[0],-direction[1],-direction[2]))
		key = False
		
		# See if the direction is still in the dict at all, and find it's key
		for k in directions.keys():
			angle = direction.angle(mathutils.Vector(directions[k]))
			if angle == 0.0:
				key = k
				
		# If the direction is not there, we just return the original list... fine
		if key is False:
			return
			
		# Make a new fresh dict (a-z) with the remaining directions
		newDirections = {}
		letter = 97
		for k in directions.keys():
			if not k == key:
				newDirections[chr(letter)] = directions[k]
				letter+=1
			
		self.options['local_directions'] = newDirections
		return

		
	
	# Get the palette!
	def getPalette(self):
	
		try:
			self.options['palettes'] = bpy.context.scene['palettes']
			palette = self.choose('select', 'palettes', 'palette')
			print(palette['title'])

			self.paletteAuthor = palette['author']
			self.paletteTitle = palette['title']
			self.paletteId = palette['id']
			self.paletteHexes = palette['hexes']
			
			letter = 97
			self.options['palette'] = {}
			
			for swatch in palette['swatches']:
				print('swatch', float(swatch[0]),float(swatch[1]),float(swatch[2]))
				self.options['palette'][chr(letter)] = [float(swatch[0]),float(swatch[1]),float(swatch[2])]
				letter += 1
			
		except:
			self.options['palettes'] = False
			print('no palette available')
		
			
			
			
	# Go choose something
	def choose(self, type, val, desk):
	
		if val in self.options.keys():
			if val == 'palette':
				result = self.secondary.Choose(type,self.options[val],desk)
			else:
				result = self.primary.Choose(type,self.options[val],desk)
			
		elif val in self.options['primary'].keys():
			pl = self.primary.key[self.primary.pos]
			p = self.primary.Choose(type,self.options['primary'][val])
			sl = self.secondary.key[self.secondary.pos]
			s =  self.secondary.Choose(type,self.options['secondary'][val])
			
			result = p+s
			print(' ',pl,sl,desk.ljust(22, ' '),'=',round(p,2),'+',round(s,2),'=',round(result,2))
				
		else:
			print('ERROR Unable to choose',val,desk)
			result = False
				
		return result

		
		
	# Start with some setup
	def setup(self, context, dnaString, keepgroups):
	
		print("\n\n->-> Starting Entorform <-<-\n")
		print('  - DNA string',dnaString,"\n")
		
		# Get the active object
		self.ob = context.active_object
		self.me = self.ob.data
		
		self.dnaString = dnaString
		
		# Split the dna string into two parts if possible
		prt = dnaString.partition(' ')
		if not prt[2]:
			self.dnaParts = {
				'primary': dnaString,
				'secondary': dnaString
				}
		else:
		
			sec = ''
			for i, p in enumerate(prt):
				if i > 1:
					sec = sec + p
		
			self.dnaParts = {
				'primary': prt[0],
				'secondary': sec
			}
			
		self.primary = liberty.liberty('string', self.dnaParts['secondary'])
		self.secondary = liberty.liberty('string', self.dnaParts['primary'])
		
		self.options = {}
		
		self.options['basecolor'] = [0.0,0.0,0.0]
		self.options['bool'] = {'a': True,'b': False}
		
		self.options['primary'] = {
			'translate': {'min': 2.0, 'max': 3.0},
			'scale': {'min': 0.4, 'max': 0.7},
			'crease': {'min': 0.4, 'max': 0.7},
			'bumpscale': {'min': 0.4, 'max': 0.7},
			'rotation': {'min': math.radians(-60.0), 'max': math.radians(60.0)},
			'divergence': {'min': math.radians(45),'max': math.radians(75)},
			'limit': {'min': 4, 'max': 6},
			}
			
		self.options['secondary'] = {
			'translate': {'min': -0.5, 'max': 1.5},
			'scale': {'min': -0.3, 'max': 0.3},
			'crease': {'min': -0.3, 'max': 0.3},
			'bumpscale': {'min': -0.35, 'max': 0.3},
			'rotation': {'min': math.radians(-60.0), 'max': math.radians(60.0)},
			'divergence': {'min': math.radians(-15),'max': math.radians(15)},
			'limit': {'min': -2, 'max': 2},
			}
			
		self.options['falloffs'] = {'a': 'LIN', 'b': 'INC', 'c': 'DEC', 'd': 'SWO', 'e': 'SPI', 'f': 'BUM', 'g': 'SWE'}
		
		self.options['bumptypes'] = {'a': 'BUM', 'b': 'SPI', 'c': 'DIM', 'd': 'PIM'}
		
		self.options['selectiontypes'] = {'a': 'direction', 'b': 'liberal', 'c': 'joint', 'd': 'all', 'e': 'checkered', 'f': 'loops'} # tip = disabled
		self.options['selectioneyes'] = {'a': 'direction', 'b': 'liberal', 'c': 'joint', 'd': 'all', 'e': 'checkered'}
		
		self.options['directions'] = {
			'a': mathutils.Vector((1.0,0.0,0.0)), 	#top
			'b': mathutils.Vector((-1.0,0.0,0.0)),	#bottom
			'c': mathutils.Vector((0.0,1.0,0.0)),		#front
			'd': mathutils.Vector((0.0,-1.0,0.0)),	#rear
			'e': mathutils.Vector((0.0,0.0,1.0)),		#right
			'f': mathutils.Vector((0.0,0.0,-1.0)),		#left
			}
			
		self.options['areatypes'] = {'a': 'area','b': 'faces'}
		self.options['frequencies'] = {'a': 1, 'b': 2}
		self.options['colorstyles'] = {'a': 'hard','b': 'soft'}
		
		self.getPalette()
		
		# Set the editing to face mode only
		#bpy.ops.wm.context_set_value(data_path='tool_settings.mesh_select_mode', value="(False, False, True)")
		
		self.startTime = time.time()
		
		self.dnaPos = 0
		self.dnaStep = 1
		self.dna = {'name':'base','strings': []}
		
		self.palette = []

		self.keepgroups = keepgroups
		
		# Total number of strings
		self.stringCount = 0
		
		# Level of deepness
		self.LOD = 2
		
		# If the grow function made a matrix previously, we can remove it now
		try:
			del(self.ob['growmatrix'])
		except:
			pass

		# Get the vertex colours
		if not self.ob.data.vertex_colors.active:
			self.ob.data.vertex_colors.new()
			for f in self.ob.data.vertex_colors.active.data:
				try:
					f.color1 = f.color2 = f.color3 = f.color4 = (0.0,0.0,0.0)
				except:
					f.color1 = f.color2 = f.color3 = (0.0,0.0,0.0)
					
		self.vCols = self.ob.data.vertex_colors.active.data
		
		# Save the dna string in a property if we want!
		self.ob['dnastring'] = dnaString
			
		# Convert the string to a list
		self.origDNA = dnaString

		self.newGroups = []
		
		# Change Selection mode to face selection
		self.lastSelectioMode = bpy.context.tool_settings.mesh_select_mode[:]
		if bpy.context.tool_settings.mesh_select_mode != (False, False, True):
			bpy.context.tool_settings.mesh_select_mode = (False, False, True)
			
			
	# Set some variables before finishing 
	def finish(self, context):
	
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.shade_smooth()
		
		#self.setFloor()
		
		#self.setDefaultView()
		#bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
		
		# Temporarily rescale the object for camera view stuff
		bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
		bpy.ops.wm.redraw_timer(type='DRAW', iterations=1)
	
		# Lets scale the object
		dimensions = self.ob.dimensions
		max = 0.0
		for i, d in enumerate(dimensions):
			if (not i) or d > max:
				max = d
		
		if max != 0.0:		
			ratio = 15 / max
		
			self.ob.scale *= ratio
		
		#bpy.ops.object.scale_apply()
		bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
		
		# Lets put the floor in the correct location
		if 'floor' in bpy.data.objects:
			for i, v in enumerate(self.ob.data.vertices):
			
				loc = v.co[2]
				if (not i) or loc < max:
					max = loc
				
			bpy.data.objects['floor'].location[2] = max
			
		
		
		# Entoform number
		filePath = bpy.data.filepath.split('\\')
		fileName = filePath[len(filePath)-1]
		
		numbers = fileName.split('.')
		for n in numbers:
			if n.isdigit():
				bpy.data.objects['text-form'].data.body = 'Entoform '+n
	
		# Dna string
		if 'text-dna' in bpy.data.objects:
			bpy.data.objects['text-dna'].data.body = self.origDNA
		
		# Datetime
		if 'text-date' in bpy.data.objects:
			now = datetime.datetime.today()
			dateString = str(now.day)+' '+misc.int_to_roman(now.month)+' '+str(now.year)+' '+str(now.hour)+':'+str(now.minute)+':'+str(now.second)
			bpy.data.objects['text-date'].data.body = dateString
		
		# execution time
		if 'text-maketime' in bpy.data.objects:
			bpy.data.objects['text-maketime'].data.body = str(round(time.time() - self.startTime))+'s'
		
		if self.options['palettes']:
		
			# Palette
			if 'text-paletter' in bpy.data.objects:
				bpy.data.objects['text-paletter'].data.body = self.paletteAuthor
				bpy.data.objects['text-palettid'].data.body = self.paletteId
				bpy.data.objects['text-palette'].data.body = self.paletteTitle
				
			self.ob['paletter'] = self.paletteAuthor
			self.ob['paletteId'] = self.paletteId
			self.ob['palette'] = self.paletteTitle
			
			#paletteQuery = "INSERT INTO ff_palettes(id, theme_id, name, creator, colour_1, colour_2, colour_3, colour_4, colour_5) VALUES (NULL,'"+self.paletteId+"','"+self.paletteTitle+"','"+self.paletteAuthor+"'"
			
			#swatches
			if 'swatches' in bpy.data.objects:
				paletteOb = bpy.data.objects['swatches']
			else:
				paletteOb = None
				
			for j, k in enumerate(self.options['palette'].keys()):
				hex = self.paletteHexes[j]
				
				#paletteQuery = paletteQuery+",'"+hex+"'"
				swatch = self.options['palette'][k]
				col = 'colour_'+str(j+1)
				
				self.ob[col] = hex #colour.rgb_to_hex(swatch)
				if paletteOb:
					for i, f in enumerate(paletteOb.data.vertex_colors.active.data):
						if i == j:
							try:
								f.color1 = f.color2 = f.color3 = f.color4 = swatch
							except:
								f.color1 = f.color2 = f.color3 = swatch
							
							
			#paletteQuery = paletteQuery+")"
			
			#self.ob['paletteQuery'] = paletteQuery
			'''
			INSERT INTO `admin_entoforms`.`ff_palettes` (`id`, `theme_id`, `name`, `creator`, `colour_1`, `colour_2`, `colour_3`, `colour_4`, `colour_5`) VALUES (NULL, '1373430', 'giblythe1', 'jakestolte', '3d3d3f', 'bf8c2f', 'bcbfbf', 'f2f2f2', 'f2dfba');
			'''
		
		
		# Geometry
		if 'text-faces' in bpy.data.objects:
			bpy.data.objects['text-faces'].data.body = str(len(self.ob.data.faces))
		if 'text-edges' in bpy.data.objects:
			bpy.data.objects['text-edges'].data.body = str(len(self.ob.data.edges))
		if 'text-verts' in bpy.data.objects:
			bpy.data.objects['text-verts'].data.body = str(len(self.ob.data.vertices))
		
		# Frame number
		fr = bpy.context.scene.frame_current
		if 'text-frame' in bpy.data.objects:
			bpy.data.objects['text-frame'].data.body = str(fr)
		#		it means fr % 360 
		#		while fr > 360:
		#			fr -= 360
		fr = fr % 360
		if 'text-angle' in bpy.data.objects:
			bpy.data.objects['text-angle'].data.body = str(fr)
		
		
		
	# Reset everything at the very end
	def reset(self, context):
	
		print("\n    Cleanup\n")
	
		if not self.keepgroups:
			for g in self.newGroups:
				self.ob.vertex_groups.active_index = g.index
				bpy.ops.object.vertex_group_remove()
		
		# Return selection mode to previous value
		bpy.context.tool_settings.mesh_select_mode[:] = self.lastSelectioMode
		    
		print("->-> Finished Entorform <-<-\n")
		
		
	# Scale the selection (always relative to the normal)
	# val = (0.5, 0.5, 0.5)
	def scale(self, val):
		bpy.ops.transform.resize(value=val, constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional=bpy.context.tool_settings.proportional_edit, proportional_edit_falloff=bpy.context.tool_settings.proportional_edit_falloff, proportional_size=1, snap=bpy.context.tool_settings.use_snap, snap_target=bpy.context.tool_settings.snap_target, snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)
		
		
	# Mark this point in time and print if we want... see how long it takes
	def mark(self,desc):
		if self.debug:
			now = time.time()
			jump = now - self.markTime
			self.markTime = now
			print(desc.rjust(10, ' '),jump)	

		
		
		
class Entoform_init(bpy.types.Operator):
	'''Build an Entoform'''
	bl_idname = 'object.entoform'
	bl_label = 'Entoform'
	bl_options = {'REGISTER', 'UNDO'}
	
	d=''

	dnaString = StringProperty(name="DNA", description="DNA string to define your shape", default=d, maxlen=100)
	
	subdivide = IntProperty(name='Subdivide', default=0, min=0, max=10, soft_min=0, soft_max=100)
	
	keepgroups = BoolProperty(name='Keep groups', description='Do not remove the added vertex groups', default=True)
	
	finish = BoolProperty(name='Finish', description='Do some final touches', default=True)
	
	run = BoolProperty(name='Execute', description='Go and actually do this', default=False)

	@classmethod
	def poll(cls, context):
		obj = context.active_object
		return (obj and obj.type == 'MESH')

	def execute(self, context):
		ENTOFORM = Entoform(context, self.dnaString, self.subdivide, self.keepgroups, self.finish, self.run) 
		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(Entoform_init.bl_idname, text="Entoform")
	
def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
	register()