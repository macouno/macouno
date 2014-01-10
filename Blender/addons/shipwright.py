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


import bpy, mathutils, math, random, time
from bpy.props import StringProperty, IntProperty


# Make it as a class
class ShipWright():



	# Initialise the class
	def __init__(self, context, seed, limit):
	
		random.seed(seed)
		self.startTime = time.time()
		self.markTime = self.startTime
		self.debug = True
		self.partCount = 0
		self.connectors = []
		
		self.scn = bpy.data.scenes[0]
		for ob in self.scn.objects:
			ob.select = False
		self.scn.objects.active = None
		
		self.mark('START')
		
		# Get a random starting point!
		basesGroup = bpy.data.groups['bases']
		partsGroup = bpy.data.groups['parts']
		
		# Get a nr to select a part
		
		self.setPart(connector=None, part=None, group=basesGroup)
		
		while self.partCount < limit and len(self.connectors):
			
			self.setPart(connector=self.getConnector(), part=None, group=partsGroup)
			
		if self.partCount >= limit:
			self.mark('END > reached limit')			
		elif not len(self.connectors):
			self.mark('END > no more connectors')
		return
	
		
	
	def setPart(self, connector=None, part=None, group=None):
		
		oPart = None
		
		if group is None:
			return
			
		if part is None:
			part = self.getPart(group)
			oPart = part
		
		part.select = True
		self.scn.objects.active = part
		bpy.ops.object.select_grouped(extend=True, type='CHILDREN_RECURSIVE')
		bpy.ops.object.duplicate(linked=True)

		bpy.ops.object.move_to_layer(layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
		
		part = self.scn.objects.active
		if connector is None:
			part.location = (0.0,0.0,0.0)
			part.rotation_euler = (0.0,0.0,0.0)
		else:
			self.connectors.remove(connector)
			part.matrix_world = connector.matrix_world
			
			
		self.partCount += 1
		
		if len(part.children):
			for c in part.children:
				cMat = mathutils.Matrix(c.matrix_world)
				c.parent = None
				self.connectors.append(c)
				c.matrix_world = cMat
				c.select = False
				
		part.select = False
		self.scn.objects.active = None
		
		# mirror all this
		if oPart and not connector is None:
			checkLoc = mathutils.Vector(connector.location)
			for c in self.connectors:
				if round(c.location[1],4) == round(connector.location[1],4) and round(c.location[2],4) == round(connector.location[2],4):
					if random.random() > 0.5:
						self.mark('mirroring')
						self.setPart(connector=c, part=oPart, group=group)
		
		return
		
		
	# Select a random connector(child)
	def getConnector(self):
	
		if not len(self.connectors):
			return None
			
		sel = int(math.floor(random.random() * len(self.connectors)))
		self.mark('selecting '+str(sel)+' from connectors')
		
		return self.connectors[sel]
	
		
	# Select a random part
	def getPart(self, group):
	
		if not len(group.objects):
			return None
	
		# Get a nr to select a part
		sel = int(math.floor(random.random() * len(group.objects)))
		self.mark('selecting '+str(sel)+' from '+group.name)
		
		return group.objects[sel]
		
		
		
	# Mark this point in time and print if we want... see how long it takes
	def mark(self,desc):
		if self.debug:
			now = time.time()
			jump = now - self.markTime
			self.markTime = now
			print(desc.rjust(30, ' '),round(jump,5))		
		
		
		

		
		
class Shipwright_init(bpy.types.Operator):
	'''Build a Ship'''
	bl_idname = 'object.shipwright'
	bl_label = 'Shipwright'
	bl_options = {'REGISTER', 'UNDO'}
	
	d = int(random.random()*1000)

	seed = IntProperty(name="Seed", description="Nr to seed your ship with", default=d)
	
	limit = IntProperty(name="Limit", description="Limit the nr of parts", default=5)

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		bpy.context.scene.layers = [True,True,True,True,True,True,True,True,True,True,True, True,True,True,True,True,True,True,True,True]
		ship = ShipWright(context, self.seed, self.limit) 
		bpy.context.scene.layers = [True,False,False,False,False,False,False,False,False,False,False, False,False,False,False,False,False,False,False,False]
		bpy.ops.object.select_all(action='SELECT')

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