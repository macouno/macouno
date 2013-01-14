# shipwright.py Copyright (C) 2011, Dolf Veenvliet
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
	"name": "ShipWright",
	"author": "Dolf Veenvliet",
	"version": 1,
	"blender": (2, 5, 6),
	"api": 31847,
	"location": "object > ShipWright ",
	"description": "Build a Ship",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Object"}

"""
Usage:

Launch from "object -> shipwright" 


Additional links:
	Author Site: http://www.macouno.com
	e-mail: dolf {at} macouno {dot} com
"""


import bpy, mathutils, math, random, colorsys, time
from bpy.props import StringProperty
from macouno import mesh_extras, select_faces


# Make it as a class
class ShipWright():



	# Initialise the class
	def __init__(self, context, dnaString):
	
		self.startTime = time.time()
		self.markTime = self.startTime
		self.debug = True
		
		self.mark('start')
		
		self.offset = 0.999
	
		self.xVec = mathutils.Vector((1.0,0.0,0.0))
		self.yVec = mathutils.Vector((0.0,1.0,0.0))
		self.zVec = mathutils.Vector((0.0,0.0,1.0))
		
		# Make the liberty class
		random.seed(dnaString)
		
		#Figure out what hull to use
		hulls = bpy.data.groups['hulls'].objects
		
		hull = self.prepObject(random.choice(hulls))

		select_faces.none()
		select_faces.in_group(hull.vertex_groups['mounts'])
		
		# Make sure there's some selected faces at least
		if not mesh_extras.has_selected('faces'):
		
			print('No faces found in hull');
		
		else:
			
			attachMents = mesh_extras.get_selected_faces()
			
			if len(attachMents):
				
				group = hull.vertex_groups['mounts']
				
				step = 0
				attachCount = 1
				vertLen = len(bpy.context.active_object.data.vertices) 
			
				while step < attachCount and step <= 13 and vertLen < 500000:
				
					print('')
					self.mark('- - - - - finished step '+str(step)+' with '+str(vertLen)+' verts')
					print('')
					
					step += 1
					
					#print('\n - step',step,'\n')
				
					# Deselect all faces
					#select_faces.none()
					#select_faces.in_group(group)
					
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.select_all(action='DESELECT')
					#bpy.ops.object.vertex_group_select()
					bpy.ops.object.vertex_group_select()
					bpy.ops.object.mode_set(mode='OBJECT')
					
					self.mark('deselected everything')
					
					#select_faces.in_group(group)
					
					#self.mark('selected mounts')
					
					hullMounts = mesh_extras.get_selected_faces()
					hullLen = len(hullMounts)
					
					self.mark('got mounts '+str(hullLen))

					attachCount = random.randint(int(round(hullLen*0.4)), hullLen)
					
					self.mark('made attachcount '+str(attachCount))

					
					if len(hullMounts):
					
						hullMount = random.choice(hullMounts)
								
						# PREP
						hullNormal = (hullMount.normal * hull.matrix_world).normalized()
						hullPos = hullMount.center * hull.matrix_world
						
						self.mark('prepped for attaching')
						self.attachPart(hull, hullMount, hullNormal, hullPos)
						
					self.mark('part attached')
						
					bpy.ops.object.modifier_add(type='EDGE_SPLIT')
					bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")
					
					self.mark('edges split')
						
					vertLen = len(bpy.context.active_object.data.vertices) 
		
		self.mark('done attaching at '+str(vertLen)+' verts')
		'''
		select_faces.none()
		ob = bpy.context.active_object
		
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.mesh.select_all(action='DESELECT')

		bpy.ops.wm.context_set_value(data_path='tool_settings.mesh_select_mode', value="(False, True, False)")
		bpy.ops.mesh.edges_select_sharp(sharpness=140.0)
		
		#bpy.ops.transform.edge_crease(value=1, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), release_confirm=False)
		

		bpy.ops.mesh.mark_sharp(clear=False)
		
		bpy.ops.object.mode_set(mode='OBJECT')
		
		for e in bpy.context.active_object.data.edges:
			if e.select:
				e.crease = 1.0
				
		bpy.ops.object.mode_set(mode='EDIT')
		bpy.ops.wm.context_set_value(data_path='tool_settings.mesh_select_mode', value="(False, False, True)")
		bpy.ops.object.mode_set(mode='OBJECT')
		
		
		bpy.ops.object.modifier_add(type='SUBSURF')
		m = ob.modifiers[0]
		m.show_viewport = False
		
		bpy.ops.object.modifier_add(type='EDGE_SPLIT')
		m = ob.modifiers[0]
		m.use_edge_angle = False
		m.use_edge_sharp = True
		m.show_viewport = False
		'''
		
		bpy.ops.object.modifier_add(type='EDGE_SPLIT')
		bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")
		#m = bpy.context.active_object.modifiers[0]
		#m.show_viewport = False
		
		bpy.ops.object.shade_smooth()
		
		self.mark('set edgesplit and shading')
		
		# Lets scale the object
		ob = bpy.context.active_object
		dimensions = ob.dimensions
		max = 0.0
		for i, d in enumerate(dimensions):
			if (not i) or d > max:
				max = d
		
		if max != 0.0:		
			ratio = 15 / max
		
			ob.scale *= ratio
			
		self.mark('found relative dimension')
		
		bpy.ops.object.scale_apply()
		
		bpy.ops.object.location_clear()
		bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
		
		self.mark('set scale and location')
		
		
		
		max  = mathutils.Vector()
		min = mathutils.Vector()
		
		for i, v in enumerate(ob.data.vertices):
			co = v.co * ob.matrix_world
			
			for j, c in enumerate(co):
				if c > max[j] or not i:
					max[j] = c
				
				if c < min[j] or not i:
					min[j] = c
					
		#print('vmax',max)
		#print('vmin',min)
			
		loc = (max + min) * 0.5
		
		ob.location = -loc
		
		self.mark('corrected location')
		#print('loc',loc)
			

		bpy.data.objects['name'].data.body = dnaString.upper()
		bpy.context.active_object.name = dnaString
		
		self.mark('finished')
		
		return
        
       
	   
	def attachPart(self, parent, parentMount, parentNormal, parentPos):
	
		print('')
			
		# NOW LETS FIND A PART
		#children = self.dna.makeDict(bpy.data.groups['parts'].objects)
		children = bpy.data.groups['parts'].objects
		
		if not len(children):
			return

		child = self.prepObject(random.choice(children))
		#child = self.prepObject(self.dna.Choose('select', children, 'part'))
		
		self.mark('prepped object')

		# Select all the mounts in the child part
		select_faces.in_group(child.vertex_groups['mounts'])
		
		# Make sure there's some selected faces at least
		if not mesh_extras.has_selected('faces'):
		
			print('No faces found in part');
		
		else:
		
			childMat = child.matrix_world
			
			childMounts = mesh_extras.get_selected_faces()
			
			# Deselect all faces
			select_faces.none()
			
			self.mark('finished selection')
			
			#childMounts = self.dna.makeDict(childMounts)
			childMount = random.choice(childMounts)
			#childMount = self.dna.Choose('select', childMounts, 'childMount')
			
			self.mark('chose mount')
			
			if childMount:
			
				childMount.select = True
			
				childNormal = (childMount.normal * child.matrix_world).normalized()
				
				# ROTATE THE CHILD AROUND THE GLOBAL Y AXIS TO MATCH THE PARENTMOUNT
				childY = mathutils.Vector((childNormal[0], 0.0, childNormal[2])).normalized()
				parentY = mathutils.Vector((parentNormal[0], 0.0, parentNormal[2])).normalized()
				
				if childY.length > 0.0 and parentY.length > 0.0:
				
					angY = childY.angle(parentY)

					print('   angY', math.degrees(angY))
					
					if angY > 0.0 and angY < 180.0:
						
						rotY = mathutils.Matrix.Rotation((math.radians(180) - angY), 4, mathutils.Vector((0.0,1.0,0.0))).to_4x4()
						
						child.matrix_world = rotY * child.matrix_world	

						childNormal = (childMount.normal * child.matrix_world).normalized()
						
				else:
				
					# ROTATE THE CHILD AROUND THE GLOBAL X AXIS TO MATCH THE PARENTMOUNT
					childX = mathutils.Vector((0.0, childNormal[1], childNormal[2])).normalized()
					parentX = mathutils.Vector((0.0, parentNormal[0], parentNormal[2])).normalized()
					
					if childX.length > 0.0 and parentX.length > 0.0:
					
						angX = childX.angle(parentX)

						print('   angX', math.degrees(angX))
						
						if angX > 0.0 and angX < 180.0:
							
							rotX = mathutils.Matrix.Rotation((math.radians(180) - angX), 4, mathutils.Vector((-1.0,0.0,0.0))).to_4x4()
							
							child.matrix_world = rotX * child.matrix_world	

							childNormal = (childMount.normal * child.matrix_world).normalized()
				
				# ROTATE THE CHILD AROUDN THE GLOBAL Z AXIS TO MATCH THE PARENTMOUNT
				childZ = mathutils.Vector((childNormal[0], childNormal[1], 0.0)).normalized()
				parentZ = mathutils.Vector((parentNormal[0], parentNormal[1], 0.0)).normalized()
				
				if childZ.length > 0.0 and parentZ.length > 0.0:
				
					angZ = childZ.angle(parentZ)
					
					print('   angZ', math.degrees(angZ))
					
					if angZ > 0.0 and angZ < 180.0:
						
						rotZ = mathutils.Matrix.Rotation((math.radians(180) - angZ), 4, mathutils.Vector((0.0,0.0,-1.0))).to_4x4()
						
						child.matrix_world = rotZ * child.matrix_world	
						
					elif angZ == 0.0:
					
						rotZ = mathutils.Matrix.Rotation(math.radians(180), 4, mathutils.Vector((0.0,0.0,-1.0))).to_4x4()
						
						child.matrix_world = rotZ * child.matrix_world	

						#childNormal = (childMount.normal * child.matrix_world).normalized()

				self.mark('fixed rotation')
				
				# SET CHILD POSITION
				childPos = childMount.center * child.matrix_world
				child.location = parentPos - childPos	
				bpy.ops.transform.resize(value=(self.offset,self.offset,self.offset), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.826446, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)
				#child.scale *= self.offset
				self.offset -= 0.001
				
				self.mark('fixed location')
				
				# MAKE THE PARENT THE PARENT! YEA
				parent.select = True
				bpy.context.scene.objects.active = parent
				#bpy.ops.object.parent_set(type='OBJECT')
				
				self.mirrorCheck(parent, parentMount, parentPos, child)
				self.mark('checked mirror')
				# Join the two meshes
				bpy.ops.object.join()
				
				#print('  post join selected',len(mesh_extras.get_selected_faces()))
				
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.object.vertex_group_remove_from(all=True)
				bpy.ops.object.mode_set(mode='OBJECT')
				
				self.mark('joined and cleaned')
				
		
		return

		
		
	def mirrorCheck(self, parent, parentMount, parentPos, child):
	
		mountX = round(parentPos[0],5)
		mountY = round(parentPos[1],5)
		mountZ = round(parentPos[2], 5)
		parentMat = parent.matrix_world
		
		bpy.context.scene.objects.active = parent
		
		cnt = 0
		selFaces = []
		
		# See if there's two or more faces on this axis
		for f in bpy.context.active_object.data.faces:
		
			loc = f.center * parentMat
			locX = round(loc[0],5)
			locY = round(loc[1],5)
			locZ = round(loc[2],5)
			
			if f == parentMount or ((locX == mountX or -locX == mountX) and locY == mountY and locZ == mountZ):
				f.select = True
				selFaces.append(f.index)
				cnt += 1
				
			else:
				f.select = False
		
		# If there's two selected faces... we can mirror around their midpoint
		if cnt == 2:
		
			print('  mirroring')
		
			bpy.ops.object.mode_set(mode='EDIT')
		
			bpy.ops.view3d.snap_cursor_to_selected()
			
			bpy.ops.object.mode_set(mode='OBJECT')
			
			bpy.context.scene.objects.active = child
			
			bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
			
			bpy.ops.object.rotation_apply()
			
			bpy.ops.object.scale_apply()
			
			bpy.ops.object.duplicate(linked=False)
			b = bpy.context.active_object
			
			#bpy.ops.object.duplicate(linked=False)
			bpy.context.active_object.scale[0] = -1.0
				
			#bpy.context.active_object.scale *= self.offset
			bpy.ops.transform.resize(value=(self.offset,self.offset,self.offset), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=0.826446, snap=False, snap_target='CLOSEST', snap_point=(0, 0, 0), snap_align=False, snap_normal=(0, 0, 0), texture_space=False, release_confirm=False)

			#b.scale *= self.offset
			#print('scale',b.scale)
			self.offset -= 0.001
			
			parent.select = True
			child.select = True

			bpy.context.scene.objects.active = parent
			
			for f in selFaces:
				bpy.context.active_object.data.faces[f].select = True
		
		
		
		
	# DUPLICATE THE OBJECT AND PLACE IT ON LAYER ONE AT 0,0,0
	def prepObject(self, ob):
		
		bpy.ops.object.select_all(action='DESELECT')
		
		ob.select = True
		bpy.context.scene.objects.active = ob
		
		bpy.context.scene.update()

		bpy.ops.object.duplicate(linked=False)

		ob = bpy.context.active_object

		ob.layers = (True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)

		bpy.ops.object.location_clear()
		
		bpy.ops.object.select_all(action='DESELECT')
		
		ob.select = True
		bpy.context.scene.objects.active = ob
		
		bpy.ops.group.objects_remove()
		
		return ob
		
		
		
	def makeSeedNumber(self, str):
	
		l = list(str)
		
		nr = 0
		
		for i in l:
			nr += ord(i)
			
			
		return nr
		
		
		
	# Mark this point in time and print if we want... see how long it takes
	def mark(self,desc):
		if self.debug:
			now = time.time()
			jump = now - self.markTime
			self.markTime = now
			print(desc.rjust(25, ' '),round(jump,5))		
		
		
		

		
		
class Shipwright_init(bpy.types.Operator):
	'''Build a Ship'''
	bl_idname = 'object.shipwright'
	bl_label = 'Shipwright'
	bl_options = {'REGISTER', 'UNDO'}
	
	d = ''

	dnaString = StringProperty(name="DNA", description="DNA string to define your ship", default=d, maxlen=100)

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		if(self.dnaString.__len__()):
			bpy.context.scene.layers = [True,True,True,True,True,True,True,True,True,True,True, True,True,True,True,True,True,True,True,True]
			ship = ShipWright(context, self.dnaString) 
			bpy.context.scene.layers = [True,False,False,False,False,False,False,False,False,False,True, False,False,False,False,False,False,False,False,False]

		return {'FINISHED'}


def menu_func(self, context):
	self.layout.operator(Shipwright_init.bl_idname, text="Shipwright")
	
def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.VIEW3D_MT_object.remove(menu_func)

if __name__ == "__main__":
	register()