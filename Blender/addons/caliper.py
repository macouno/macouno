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

bl_info = {
	"name": "Caliper",
	"author": "macouno",
	"version": (2, 1),
	"blender": (2, 6, 3),
	"location": "View3D > Add > Caliper",
	"description": "Add a caliper object",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Object"}

import bpy, mathutils, time, math
from bpy.app.handlers import persistent


# ########################################################
# By macouno
# ########################################################


# Add the distance to a string!
def addDistance(distance, length, unit):
	if distance:
		return distance+' '+str(int(length))+unit
	return str(int(length))+unit


	
# FUNCTION FOR MAKING A NEAT METRIC SYSTEM MEASUREMENT STRING
def getMeasureString(distance, unit_settings, precision):
	
	system = unit_settings.system
	# Whether or not so separate the measurement into multiple units
	separate = unit_settings.use_separate
	# The current measurement (multiplied by scale to get meters as a starting point)
	m = distance * unit_settings.scale_length
	fM = 0
	distance = False
	
	if system == 'METRIC':
		table = [['km', 0.001], ['m', 1000], ['cm', 100], ['mm', 10]]
	elif system == 'IMPERIAL':
		table = [['mi', 0.000621371], ['ft', 5280], ['in', 12], ['thou', 1000]]
	
	# Figure out where to end measuring
	last = len(table)
	if precision < last:
		last = precision
	
	for i, t in enumerate(table):
		step = i
		unit = t[0]
		factor = t[1]
		m = (m - fM) * factor
		fM = math.floor(m)
		
		if fM and not separate:
			return str(round(m,precision))+unit
		elif fM:
			# Make sure the very last measurement is rounded and not floored
			if step >= last:
				return addDistance(distance, round(m), unit)
			distance = addDistance(distance, fM, unit)

	if not distance:
		return '0'+unit

	return distance
	
	
	
# CLEANUP CALIPERS
@persistent
def CaliperCheck(dummy):
	
	# Lets see if the CaliperBits group exists... if not.. no action is required
	try:
		CaliperBits = bpy.data.groups['CaliperBits']
	except:
		CaliperBits = False
		
	# We do everything else outside the try except to get error messages in case anything is wrong
	if not CaliperBits is False:
	
		
		# Make a list of all caliper parts without a parent
		# And add the calipers that don't have enough children
		remove = [ob for ob in CaliperBits.objects if (ob.CaliperBit and (ob.parent == None or not ob.parent.name in CaliperBits.objects)) or (ob.Caliper and len(ob.children) < 4)]
		
		if len(remove):
			for ob in remove:
				ob.select = False
				CaliperBits.objects.unlink(ob)
				bpy.context.scene.objects.unlink(ob)
				
	return
	

	
# DRIVER TO UPDATE THE CALIPERS
def CaliperUpdate(caliperName, textCurve, distance):

	# We try an update
	try:
		caliper = bpy.data.objects[caliperName]
		precision = caliper.CaliperPrecision

		unit_settings = bpy.context.scene.unit_settings
		
		# Some preparation for whatever comes next
		if unit_settings.system != 'NONE':
			bpy.data.curves[textCurve].body = getMeasureString(distance, unit_settings, precision)
		
		# IF we do things in Blender units, we just round it somewhat... for precision
		else:
			# Just set the textCurve's body as the distance... done
			bpy.data.curves[textCurve].body = str(round(distance, precision))

		return distance
		
	# If the update fails we try a check
	except:
		bpy.data.curves[textCurve].body = 'error'
		return 0.0

	
	
# LOAD THE CALIPER INTO THE DRIVER NAMESPACE ON FILE LOAD	
@persistent
def load_caliper_on_load_file(dummy):
	CaliperCheck(0)
	bpy.app.driver_namespace['CaliperUpdate'] = CaliperUpdate

	
	
# LOAD THE CALIPER INTO THE DRIVER NAMESPACE ON SCENE UPDATE	
@persistent
def caliper_scene_update(dummy):

	
	if not bpy.app.driver_namespace.get('CaliperUpdate'):
		bpy.app.driver_namespace['CaliperUpdate'] = CaliperUpdate
	
	CaliperCheck(0)
	
	# Hack to update all curves that have a text body... hack!
	try:
		for c in bpy.data.curves:
			try:
				if c['previous'] != c.body:
					c.body = c.body
					c['previous'] = c.body
			except:
				try:
					c['previous'] = c.body
				except:
					pass
				pass
	except:
		pass
		
		
		
# GET THE END OR START OBJECT FROM THE CALIPER
def CaliperGet(caliper, type):

	# Get the start object
	for ob in caliper.children:
		if type == 'start' and ob.CaliperStart:
			return ob
		elif type == 'end' and ob.CaliperEnd:
			return ob
		elif type == 'arrow' and ob.type == 'MESH':
			return ob
			
	return False
	
	
	
# Set the targets/locations for the caliper
def CaliperSetTarget(self,context):
	try:
		
		caliper = context.object
		
		#Make sure this only runs on caliper objects, nothing else!
		if caliper.Caliper:
		
			start = CaliperGet(caliper, 'start')
			end = CaliperGet(caliper, 'end')
			
			# If the type is vector we just set the relative location
			if caliper.CaliperStartType == 'vector':
				start.location = caliper.CaliperStartVector
				
				# disable the copy location constraint
				start.constraints[0].mute = True
				
			# If it's object location we need to controll the constraint
			elif caliper.CaliperStartType == 'object':
				
				if caliper.CaliperStartTarget:
					start.constraints[0].mute = False
					start.constraints[0].target = bpy.data.objects[caliper.CaliperStartTarget]
					if caliper.CaliperStartSubtarget:
						start.constraints[0].subtarget = caliper.CaliperStartSubtarget
					else:
						start.constraints[0].subtarget = ''
						
				else:
					start.constraints[0].mute = True
				
			# We know the end empty is the only child of the start empty
			if caliper.CaliperEndType == 'vector':
				end.location = caliper.CaliperEndVector
				
				# Do not use the copy location constraint
				end.constraints[0].mute = True
				
			elif caliper.CaliperEndType == 'object':
				
				if caliper.CaliperEndTarget:
					end.constraints[0].mute = False
					end.constraints[0].target = bpy.data.objects[caliper.CaliperEndTarget]
					if caliper.CaliperEndSubtarget:
						end.constraints[0].subtarget = caliper.CaliperEndSubtarget
					else:
						end.constraints[0].subtarget = ''
				else:
					end.constraints[0].mute = True
							
			#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
	except:
		pass
	return
	
	
	
# MAKE THE ARROW OBJECT AND MESH
def CaliperArrowMake(scene, caliper):

	style = caliper.CaliperStyle
	
	try:
		CaliperBits = bpy.data.groups['CaliperBits']
	except:
		CaliperBits = bpy.data.groups.new('CaliperBits')
	
	if style == 'square':
		coList = [(0.1,-0.1,-0.1),(0.1,0.1,-0.1),(-0.1,0.1,-0.1),(-0.1,-0.1,-0.1),(0.1,-0.1,0.1),(0.1,0.1,0.1),(-0.1,0.1,0.1),(-0.1,-0.1,0.1),(0.0,0.0,0.0),(-0.0,0.0,0.0),(0.0,0.0,0.0)]
		poList = [(5,6,2,1),(5,1,9),(7,4,0,3),(0,1,2,3),(7,6,5,4),(7,3,8),(8,2,6),(3,2,8),(6,7,8),(4,5,9),(0,4,9),(1,0,9)]
		sList = [0,1,4,5,9]
		eList = [2,3,6,7,8]
		
	elif style == 'round':
		coList = [(0.1,-0.0924,-0.0383),(0.1,-0.0981,-0.0195),(0.1,-0.1,0.0),(0.1,-0.0981,0.0195),(0.1,-0.0924,0.0383),(0.1,-0.0831,0.0556),(0.1,-0.0707,0.0707),(0.1,-0.0556,0.0831),(0.1,-0.0383,0.0924),(0.1,-0.0195,0.0981),(0.1,0.0,0.1),(-0.1,0.0,0.1),(-0.1,-0.0195,0.0981),(-0.1,-0.0383,0.0924),(-0.1,-0.0556,0.0831),(-0.1,-0.0707,0.0707),(-0.1,-0.0831,0.0556),(-0.1,-0.0924,0.0383),(-0.1,-0.0981,0.0195),(-0.1,-0.1,0.0),(-0.1,-0.0981,-0.0195),(-0.1,-0.0924,-0.0383),(-0.1,-0.0831,-0.0556),(-0.1,-0.0707,-0.0707),(-0.1,-0.0556,-0.0831),(-0.1,-0.0383,-0.0924),(-0.1,-0.0195,-0.0981),(-0.1,0.0,-0.1),(-0.1,0.0195,-0.0981),(-0.1,0.0383,-0.0924),(-0.1,0.0556,-0.0831),(-0.1,0.0707,-0.0707),(-0.1,0.0831,-0.0556),(-0.1,0.0924,-0.0383),(-0.1,0.0981,-0.0195),(-0.1,0.1,0.0),(-0.1,0.0981,0.0195),(-0.1,0.0924,0.0383),(-0.1,0.0831,0.0556),(-0.1,0.0707,0.0707),(-0.1,0.0556,0.0831),(-0.1,0.0383,0.0924),(-0.1,0.0195,0.0981),(0.0,-0.0,0.0),(0.0,-0.0,0.0),(0.1,0.0195,0.0981),(0.1,0.0383,0.0924),(0.1,0.0556,0.0831),(0.1,0.0707,0.0707),(0.1,0.0831,0.0556),(0.1,0.0924,0.0383),(0.1,0.0981,0.0195),(0.1,0.1,0.0),(0.1,0.0981,-0.0195),(0.1,0.0924,-0.0383),(0.1,0.0831,-0.0556),(0.1,0.0707,-0.0707),(0.1,0.0556,-0.0831),(0.1,0.0383,-0.0924),(0.1,0.0195,-0.0981),(0.1,0.0,-0.1),(0.1,-0.0195,-0.0981),(0.1,-0.0383,-0.0924),(0.1,-0.0556,-0.0831),(0.1,-0.0707,-0.0707),(0.1,-0.0831,-0.0556)]
		poList = [(44,59,60),(44,54,55),(44,49,50),(44,10,45),(44,9,10),(44,4,5),(44,65,0),(44,60,61),(44,55,56),(44,50,51),(44,45,46),(44,5,6),(44,0,1),(44,61,62),(44,56,57),(44,51,52),(44,46,47),(44,6,7),(44,1,2),(44,62,63),(44,57,58),(44,52,53),(44,47,48),(44,7,8),(44,2,3),(44,63,64),(44,58,59),(44,53,54),(44,48,49),(44,8,9),(44,3,4),(44,64,65),(43,15,16),(43,41,42),(43,36,37),(43,31,32),(43,26,27),(43,21,22),(43,16,17),(43,11,12),(43,42,11),(43,37,38),(43,32,33),(43,27,28),(43,22,23),(43,17,18),(43,12,13),(43,38,39),(43,33,34),(43,28,29),(43,23,24),(43,18,19),(43,13,14),(43,39,40),(43,34,35),(43,29,30),(43,24,25),(43,19,20),(43,14,15),(43,40,41),(43,35,36),(43,30,31),(43,25,26),(43,20,21),(55,54,53,52,51,50,49,48,47,46,45,10,9,8,7,6,5,4,3,2,1,0,65,64,63,62,61,60,59,58,57,56),(13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,11,12),(10,9,12,11),(45,10,11,42),(46,45,42,41),(47,46,41,40),(48,47,40,39),(49,48,39,38),(50,49,38,37),(51,50,37,36),(52,51,36,35),(53,52,35,34),(54,53,34,33),(55,54,33,32),(56,55,32,31),(57,56,31,30),(58,57,30,29),(59,58,29,28),(60,59,28,27),(61,60,27,26),(62,61,26,25),(63,62,25,24),(64,63,24,23),(65,64,23,22),(0,65,22,21),(1,0,21,20),(2,1,20,19),(3,2,19,18),(4,3,18,17),(5,4,17,16),(6,5,16,15),(7,6,15,14),(8,7,14,13),(9,8,13,12)]
		sList = [0,1,2,3,4,5,6,7,8,9,10,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65]
		eList = [11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43]
		
	elif style == 'simple':
		coList = [(-0.5,0.0,-0.5),(-0.5,0.1,0.1),(-0.5,-0.1,0.1),(-0.5,0.0,0.5),(0.0,0.0,0.0),(0.5,0.0,-0.5),(-0.5,-0.1,-0.1),(-0.5,0.1,-0.1),(0.5,0.1,-0.1),(0.5,-0.1,-0.1),(0.5,0.1,0.1),(0.5,-0.1,0.1),(0.5,0.0,0.5),(0.0,0.0,0.0)]
		poList = [(4,7,1),(11,10,1,2),(1,10,8,7),(3,2,1),(3,2,4),(13,8,10),(6,7,8,9),(0,7,6),(5,8,9),(7,0,4),(9,5,13),(11,9,13),(12,11,13),(8,5,13),(2,6,4),(6,0,4),(11,2,6,9),(1,3,4),(10,12,13),(12,11,10)]
		sList = [5,8,9,10,11,12,13]
		eList = [0,1,2,3,4,6,7]


	
	# GET THE ARROW
	# Lets add a mesh for the indication
	me = bpy.data.meshes.new('arrow')
	arrow = bpy.data.objects.new('arrow', me)
	scene.objects.link(arrow)
	CaliperBits.objects.link(arrow)
	arrow.CaliperBit = True
	arrow.parent = caliper
	me.from_pydata(coList, [], poList)
	
	# Get the ends and the hooks!
	start = CaliperGet(caliper, 'start')
	sLoc = mathutils.Vector(start.location)
	sMute = start.constraints[0].mute
	start.constraints[0].mute = True
	sHook = start.children[0]
	
	end = CaliperGet(caliper, 'end')
	eLoc = mathutils.Vector(end.location)
	eMute = end.constraints[0].mute
	end.constraints[0].mute = True
	eHook = end.children[0]
	
	# Add vertex groups for the start and end
	sGroup = arrow.vertex_groups.new('start')
	sGroup.add(sList, 1.0, 'REPLACE')
	
	# Add a hook modifier to the new group
	m1 = arrow.modifiers.new('startHook', 'HOOK')
	m1.vertex_group = sGroup.name
	m1.show_in_editmode = True
	m1.show_on_cage = True
	m1.object = sHook
	
	eGroup = arrow.vertex_groups.new('end')
	eGroup.add(eList, 1.0, 'REPLACE')
	
	m2 = arrow.modifiers.new('endHook', 'HOOK')
	m2.vertex_group = eGroup.name
	m2.show_in_editmode = True
	m2.show_on_cage = True
	m2.object = eHook
	
	# Select the arrow object so that we can reset the hooks!
	bpy.ops.object.select_all(action='DESELECT')
	arrow.select = True
	scene.objects.active = arrow
	bpy.ops.object.mode_set(mode='EDIT')
	
	# Reset the hooks... so they start at 0,0,0
	start.location = mathutils.Vector((0.0,0.0,0.0))
	end.location = mathutils.Vector((2.5,0.0,0.0))
	bpy.ops.object.hook_reset(modifier=m1.name)

	start.location = mathutils.Vector((-2.5,0.0,0.0))
	end.location = mathutils.Vector((0.0,0.0,0.0))
	bpy.ops.object.hook_reset(modifier=m2.name)
	
	bpy.ops.object.mode_set(mode='OBJECT')
	
	bpy.ops.object.select_all(action='DESELECT')
	caliper.select = True
	scene.objects.active = caliper
	
	# Set the start and end location back to what they were
	start.location = sLoc
	start.constraints[0].mute = sMute
	end.location = eLoc
	end.constraints[0].mute = eMute
	
	return
	
	
	
# Create the mesh for the caliper object!
def CaliperArrowUpdate(self, context):

	try:
		caliper = context.object

		if caliper.Caliper:
		
			# Remove the old arrow if one was created!
			arrow = CaliperGet(caliper, 'arrow')
			if arrow:
				arrow.parent = None
				context.scene.objects.unlink(arrow)
		
			CaliperArrowMake(context.scene, caliper)
	except:
		pass
		


# Make a new caliper!
def CaliperCreation(context):

	bpy.ops.object.select_all(action='DESELECT')

	scn = context.scene
	
	try:
		CaliperBits = bpy.data.groups['CaliperBits']
	except:
		CaliperBits = bpy.data.groups.new('CaliperBits')
	
	
	'''
	try:
		caliperGroup = bpy.data.groups['calipers']
	except:
		caliperGroup = bpy.data.groups.new('calipers')
	'''
	# Add the caliper empty
	caliper = bpy.data.objects.new('caliper', None)
	scn.objects.link(caliper)
	CaliperBits.objects.link(caliper)
	#caliper.select = True
	#scn.objects.active = caliper
	
	caliper.Caliper = True
	caliper.show_name = True
	#caliper.CaliperStyle = 'square'
	caliper.CaliperStartVector = mathutils.Vector((-2.5,0,0))
	caliper.CaliperEndVector = mathutils.Vector((2.5,0,0))
	caliper.CaliperPrecision = 2
	
	print('added',caliper.name)
	
	# Make an empty for the start of measurement
	start = bpy.data.objects.new('start', None)
	scn.objects.link(start)
	CaliperBits.objects.link(start)
	start.CaliperBit = True
	start.CaliperStart = True
	c = start.constraints.new(type='COPY_LOCATION')
	c.mute = True
	#c.use_y = c.use_z =  False
	start.parent = caliper
	start.show_name = True
	#start.hide = True
	#start.hide_select = True
	#start.select = True
	
	# Make an empty for the end of the measurement
	end = bpy.data.objects.new('end', None)
	scn.objects.link(end)
	CaliperBits.objects.link(end)
	end.CaliperBit = True
	end.CaliperEnd = True
	c = end.constraints.new(type='COPY_LOCATION')
	c.mute = True
	end.parent = caliper
	end.show_name = True
	#end.hide = True
	#end.hide_select = True
	#end.select = True
	#end.location[0] = 2.0
	
	
	# Now lets see if we can add a text object
	crv = bpy.data.curves.new("length", 'FONT')
	crv.align = 'CENTER'
	crv.offset_y = 0.25
	crv.extrude = 0.05
	text = bpy.data.objects.new(crv.name, crv)
	text.CaliperBit = True
	scn.objects.link(text)
	CaliperBits.objects.link(text)
	text.parent = caliper
	
	
	# Add a custom measurement property to the caliper's end
	text['length'] = 0.0
	
	# Add the driver to the measurement so it gets auto updated
	fcurve = text.driver_add('["length"]')
	drv = fcurve.driver
	drv.type = 'SCRIPTED'
	
	drv.show_debug_info = True
	
	# Make a new variable that measures the distance!
	nvar = drv.variables.new()
	nvar.name = 'distance'
	nvar.type = 'LOC_DIFF'
	
	# Make the caliper the start of the measurement
	targ1 = nvar.targets[0]
	targ1.id = start
	
	# Make the end itself the end of the measurement
	targ2 = nvar.targets[1]
	targ2.id = end
	
	
	# Make the text object stay in the middle of the measurement
	c = text.constraints.new(type='COPY_LOCATION')
	c.target = start
	c = text.constraints.new(type='COPY_LOCATION')
	c.target = end
	c.influence = 0.5
	c = text.constraints.new(type='TRACK_TO')
	c.target = end
	c.track_axis = 'TRACK_X'
	c.up_axis = 'UP_Y'
	
	# Make the hooks!
	sHook = bpy.data.objects.new('startHook', None)
	scn.objects.link(sHook)
	CaliperBits.objects.link(sHook)
	sHook.CaliperBit = True
	sHook.parent = start
	sHook.hide = True
	
	eHook = bpy.data.objects.new('endHook', None)
	scn.objects.link(eHook)
	CaliperBits.objects.link(eHook)
	eHook.CaliperBit = True
	eHook.parent = end
	eHook.hide = True
	
	# Add constraints to the hook objects so they track each other
	c = sHook.constraints.new(type='TRACK_TO')
	c.target = end
	c.track_axis = 'TRACK_Z'
	c.up_axis = 'UP_Y'
	
	c = eHook.constraints.new(type='TRACK_TO')
	c.target = start
	c.track_axis = 'TRACK_NEGATIVE_Z'
	c.up_axis = 'UP_Y'
	

	# Create the mesh for the caliper
	CaliperArrowMake(scn, caliper)
	
	start.location[0] = -2.5
	end.location[0] = 2.5
	
	# AT THE VERY END
	# Set the expression to use the variable we created
	drv.expression = 'CaliperUpdate("'+caliper.name+'","'+crv.name+'", '+nvar.name+')'
	
	bpy.ops.object.select_all(action='DESELECT')
	caliper.select = True
	bpy.context.scene.objects.active = caliper
	
	
	bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
	
	# Returning caliper for @cloudforms additions
	return caliper

	
class SCENE_PT_caliper(bpy.types.Panel):
	bl_label = "Caliper"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "object"
	
	@classmethod
	def poll(cls, context):
		return (context.object.Caliper == True)

	def draw(self, context):
		
		layout = self.layout
		
		obj = context.object
		
		#row = layout.row()
		#self.layout.label(text="Caliper options")
		#row.operator("scene.new", text="Do something")
		#layout.prop(obj, "CaliperTarget", 'Target')
		
		#self.layout.label(text="Start")
		
		box = layout.box()
		box.label("Style")
		box.prop(obj, "CaliperStyle")
		box.prop(obj, "CaliperPrecision")
		#box.operator("object.caliper_mesh", text="Set")
	
		box = layout.box()
		box.label("Start")
		box.prop(obj, "CaliperStartType")
		if obj.CaliperStartType == 'vector':
			box.prop(obj, "CaliperStartVector")
		else:
			box.prop_search(obj, 'CaliperStartTarget', context.scene, 'objects')
		
			try:
				target = bpy.data.objects[obj.CaliperStartTarget]
				if target.type == 'MESH':
					box.prop_search(obj, 'CaliperStartSubtarget',	target, 'vertex_groups')
			except:
				pass
			
		#self.layout.label(text="End")
		box = layout.box()
		box.label("End")
		box.prop(obj, "CaliperEndType")
		if obj.CaliperEndType == 'vector':
			box.prop(obj, "CaliperEndVector")
		else:
			box.prop_search(obj, 'CaliperEndTarget', context.scene, 'objects')
			
			try:
				target = bpy.data.objects[obj.CaliperStartTarget]
				if target.type == 'MESH':
					box.prop_search(obj, 'CaliperEndSubtarget',	target, 'vertex_groups')
			except:
				pass

				
				
# Add properties to objects
def CaliperAddVariables():

	bpy.types.Object.Caliper = bpy.props.BoolProperty()
	bpy.types.Object.CaliperBit = bpy.props.BoolProperty()
	bpy.types.Object.CaliperStart = bpy.props.BoolProperty()
	bpy.types.Object.CaliperEnd = bpy.props.BoolProperty()

	bpy.types.Object.CaliperStyle = bpy.props.EnumProperty(name='Arrow',items = [('square','Square','A basic square pointed arrow'),('round','Round','A basic round pointed arrow'),('simple','Simple','The original wide pointed arrow')], update=CaliperArrowUpdate)
	bpy.types.Object.CaliperPrecision = bpy.props.IntProperty(name='Precision', min=1, max=10, step=1)
	
	bpy.types.Object.CaliperStartType = bpy.props.EnumProperty(name='Type',items = [('vector','Location','A location vector with x,y,z coordinates'),('object','Object','The location of a specific 3D object')], update=CaliperSetTarget)
	bpy.types.Object.CaliperStartVector = bpy.props.FloatVectorProperty(name='Location', update=CaliperSetTarget)
	bpy.types.Object.CaliperStartTarget = bpy.props.StringProperty(name='Target', update=CaliperSetTarget)
	bpy.types.Object.CaliperStartSubtarget = bpy.props.StringProperty(name='Vertex group', update=CaliperSetTarget)

	bpy.types.Object.CaliperEndType = bpy.props.EnumProperty(name='Type',items = [('vector','Location','A location vector with x,y,z coordinates'),('object','Object','The location of a specific 3D object')], update=CaliperSetTarget)
	bpy.types.Object.CaliperEndVector = bpy.props.FloatVectorProperty(name='Location', update=CaliperSetTarget)
	bpy.types.Object.CaliperEndTarget = bpy.props.StringProperty(name='Target', update=CaliperSetTarget)
	bpy.types.Object.CaliperEndSubtarget = bpy.props.StringProperty(name='Vertex group', update=CaliperSetTarget)
	
	
	
# FUNCTION TO ADD A CALIPER TO THE SCENE
class Caliper_Add(bpy.types.Operator):
	bl_idname = "object.caliper_add"
	bl_label = "Caliper"
	#bl_options = {'REGISTER', 'UNDO'}
		

	def execute(self, context):
		print('adding caliper')
		
		CaliperCreation(context)
		
		return {'FINISHED'}

		

# Define menu item
def menu_func(self, context):
	self.layout.operator(Caliper_Add.bl_idname, icon='PLUGIN')

	
	
# Load and register
def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_add.append(menu_func)
	
	CaliperAddVariables()
	#bpy.utils.register_class(SCENE_PT_caliper)
	
	bpy.app.handlers.load_post.append(load_caliper_on_load_file)
	bpy.app.handlers.scene_update_pre.append(caliper_scene_update)
	
	bpy.app.handlers.save_pre.append(CaliperCheck)

	
	
# Unregister
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_add.remove(menu_func)
	
	#bpy.utils.unregister_class(SCENE_PT_caliper)

	
	
if __name__ == "__main__":
	register()