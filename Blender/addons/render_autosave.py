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
	"name": "Autosave Render",
	"author": "Dolf Veenvliet (macouno)",
	"version": (1,0),
	"blender": (2, 61, 4),
	"api": 41490,
	"location": "Properties > Render",
	"description": "Auto save every render",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Render"}

# ########################################################
# By macouno
#
# Set the target in the Autosave panel in the render settings
# Format your path like c:\something\####.png
#
# ########################################################

import bpy
from bpy.app.handlers import persistent
from bpy.props import StringProperty,BoolProperty
import os

if os.name == 'nt':
	default_path = "c:/tmp/"
else:
	default_path = "/tmp/"

bpy.types.Scene.autosavepath = StringProperty(name='Path',description='The location to auto save images to',default=default_path,subtype='FILE_PATH')
bpy.types.Scene.autosaveenable = BoolProperty(name='Enable auto save',description='Whether or not to auto save every render',default=False)

class DATA_PT_render_autosave(bpy.types.Panel):
	bl_label = "Autosave"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "render"

	@classmethod
	def poll(cls, context):
		return True
	
	def draw(self, context):
		layout = self.layout
		
		layout.prop(context.scene, "autosaveenable", text="Enable")
		layout.prop(context.scene, "autosavepath", text="")


def make_imagename(filename, number):

	fileBits = filename.split('#')
	bitLen = len(fileBits)
	imagenr = str(number).rjust(bitLen-1, '0')
	
	for i in range(bitLen-1):
		fileBits[i] = fileBits[i] + imagenr[i]
		
	return ''.join(fileBits)

# PERSISTENT STUFF
@persistent
def render_autosave(context):

	if context.autosaveenable:
	
		abspath = bpy.path.abspath(context.autosavepath)
		
		filename = os.path.basename(abspath)
		dirname = os.path.dirname(abspath)
		
		nr = 1
		tempName = make_imagename(filename, nr)
		tempPath = dirname+os.sep+tempName
		
		# See what files already exist in this directory
		if os.path.exists(dirname):
		
			print('Found directory',dirname)
		
			# Find the first nr of an image that doesn't exist yet
			while os.path.isfile(tempPath):

				nr += 1
				tempName = make_imagename(filename, nr)
				tempPath = dirname+os.sep+tempName
			
		else:
			print('Did not find directory',dirname)
			
		print('Auto saving image as ',tempPath);
		bpy.data.images['Render Result'].save_render(filepath=tempPath, scene=context)
		#bpy.ops.image.save_as(filepath=tempPath, check_existing=False, copy=True)

def register_callbacks():
	bpy.app.handlers.render_post.append(render_autosave)

def unregister_callbacks():
	bpy.app.handlers.render_post.remove(render_autosave)

# REGULAR REGISTER FOR THE INTERFACE STUFF
def register():
	bpy.utils.register_module(__name__)
	#bpy.app.handlers.render_post.append(render_autosave)
	register_callbacks()

def unregister():
	bpy.utils.unregister_module(__name__)
	#bpy.app.handlers.render_post.remove(render_autosave)
	unregister_callbacks()

if __name__ == "__main__":
	register()
