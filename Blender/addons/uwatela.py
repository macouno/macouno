
bl_info = {
	"name": "Uwatela",
	"author": "Dolf Veenvliet",
	"version": 1,
	"blender": (2, 6, 9),
	"api": 31847,
	"location": "Nodes",
	"description": "Nodes for messing around",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"}


import bpy, bmesh
from macouno import bmesh_extras
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import StringProperty, EnumProperty

# Implementation of custom nodes from Python

def input_nodes(ntree, node):
    for link in ntree.links:
        if link.to_node == node:
            yield link.from_node

def sort_nodes(ntree):
    nodelist = []
    visited = set()
    def sort_node(node):
        if node in visited:
            return
        visited.add(node)

        for inode in input_nodes(ntree, node):
            sort_node(inode)
        nodelist.append(node)
    for node in ntree.nodes:
        sort_node(node)
    return nodelist


# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class UwatelaNodeTree(NodeTree):
	# Description string
	'''A custom node tree type that will show up in the node editor header'''
	# Optional identifier string. If not explicitly defined, the python class name is used.
	bl_idname = 'UwatelaTreeType'
	# Label for nice name display
	bl_label = 'Uwatela Node Tree'
	bl_icon = 'NODETREE'
	

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class UwatelaTreeNode :
	@classmethod
	def poll(cls, ntree):
		return ntree.bl_idname == 'UwatelaTreeType'
		
		
		
# Generic socket type for Uwatela nodes
class UwatelaNodeSocket(NodeSocket):
        bl_idname = "UwatelaNodeSocket"
        bl_label = "Uwatela Socket"

        def draw(self, context, layout, node, text):
                layout.label(text)

        def draw_color(self, context, node):
                return (1.0, 0.4, 0.216, 0.5) 
		
		
class UwatelaMeshMoveNode(Node, UwatelaTreeNode):
	bl_idname = 'UwatelaMeshMove'
	# Label for nice name display
	bl_label = 'Move mesh'
	# Icon identifier
	bl_icon = 'SOUND'

	ObjectName = bpy.props.StringProperty()
	
	def init(self, context):
		self.inputs.new('UwatelaNodeSocket', "Object in")
		#self.outputs.new('ObjectName', "Out")
		
	def draw_buttons(self, context, layout):
		#layout.prop(self, "")
		print('b')
		
	def update(self):
		print('a')
		#print('got',self.ObjectName)
		#print('in',self.NodeSocketString)
		
	def update_socket(self, context):
		self.update()
		
	# Copy function to initialize a copied node from an existing one.
	def copy(self, node):
		print("Copying from node ", node)

	# Free function to clean up on removal.
	def free(self):
		print("Removing node ", self, ", Goodbye!")
		

# Derived from the Node base type.
class UwatelaObjectInputNode(Node, UwatelaTreeNode):
	# === Basics ===
	# Description string
	'''A custom node'''
	# Optional identifier string. If not explicitly defined, the python class name is used.
	bl_idname = 'UwatelaObjectInput'
	# Label for nice name display
	bl_label = 'Object input'
	# Icon identifier
	bl_icon = 'SOUND'

	# === Custom Properties ===
	ObjectName = bpy.props.StringProperty()
	
	def object_select(self, context):
		return [tuple(3 * [ob.name]) for ob in context.scene.objects if ob.type == 'MESH']

	ObjectProperty = EnumProperty(items = object_select, name = 'ObjectProperty')
	
	# === Optional Functions ===
	def init(self, context):
		self.outputs.new('NodeSocketString', "Out")
		
	def update(self):
		if self.ObjectProperty:
			obj = bpy.data.objects[self.ObjectProperty]
			try:
				newObject = bpy.data.objects['uwatelaTempObject']
				newObject.data = obj.data.copy()
			except:
				newObject = bpy.data.objects.new('uwatelaTempObject',obj.data.copy())
			
			newObject.data.name = 'uwatelaTempMesh'
			
			self.ObjectName = newObject.name
			print('made',newObject.name)
			
	def update_socket(self, context):
		self.update()
		
	# Copy function to initialize a copied node from an existing one.
	def copy(self, node):
		print("Copying from node ", node)

	# Free function to clean up on removal.
	def free(self):
		print("Removing node ", self, ", Goodbye!")

	# Additional buttons displayed on the node.
	def draw_buttons(self, context, layout):
		#layout.label("Settings")
		layout.prop(self, "ObjectProperty", text="Object", icon='OBJECT_DATA')
		layout.prop(self, "ObjectName")




### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class UwatelaNodeCategory(NodeCategory):
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'UwatelaTreeType'

# all categories in a list
node_categories = [
	# identifier, label, items list
	UwatelaNodeCategory("UWATELA", "Uwatela", items=[
		# our basic node
		NodeItem("UwatelaMeshMove"),
		NodeItem("UwatelaObjectInput"),
		])
	]


def register():
	bpy.utils.register_class(UwatelaNodeTree)
	bpy.utils.register_class(UwatelaNodeSocket)
	bpy.utils.register_class(UwatelaMeshMoveNode)
	bpy.utils.register_class(UwatelaObjectInputNode)

	nodeitems_utils.register_node_categories("UWATELA", node_categories)


def unregister():
	nodeitems_utils.unregister_node_categories("UWATELA")

	bpy.utils.unregister_class(UwatelaNodeTree)
	bpy.utils.unregister_class(UwatelaNodeSocket)
	bpy.utils.unregister_class(UwatelaMeshMoveNode)
	bpy.utils.unregister_class(UwatelaObjectInputNode)


if __name__ == "__main__":
	register()
