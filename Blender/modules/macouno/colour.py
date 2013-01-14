import bpy, mathutils, colorsys
from macouno import misc



# Convert an rgb tuple (or list) to a hex string
def rgb_to_hex(rgb):
    rgb = list(rgb)
    for i, c in enumerate(rgb):
        if not c.is_integer():
            rgb[i] = int(c*255)
    rgb = tuple(rgb)
    return '%02x%02x%02x' % rgb



# Set the base color for the entire mesh at the start
def setBaseColor(baseColor):
	
	vertex_colors = bpy.context.active_object.data.vertex_colors
	
	# Get the vertex colors
	if not vertex_colors.active:
		vertex_colors.new()
		
	for f in vertex_colors.active.data:
		try:
			f.color1 = f.color2 = f.color3 = f.color4 = baseColor
		except:
			f.color1 = f.color2 = f.color3 = baseColor
		
		
		
def applyColorToSelection(vCol):

	mesh = bpy.context.active_object.data
	
	# Get the faces
	for f in mesh.faces:
		if f.select:
		
			vColFace = mesh.vertex_colors.active.data[f.index]
			
			for r in range(len(f.vertices)):
					
				if not r:
					vColFace.color1 = vCol
				elif r == 1:
					vColFace.color2 = vCol
				elif r == 2:
					vColFace.color3 = vCol
				elif r == 3:
					vColFace.color4 = vCol




# Shift the hue of a color a certain ammount
def HueShift(hue,shift):
	hue += shift
	while hue >= 1.0:
		hue -= 1.0
	while hue < 0.0:
		hue += 1.0
	return hue
	
	
	
# Make nice colors based on grades
def setColors(r,g,b,g1,g2,g3,g4):

	colors = []

	ra = (r+(1.0-r)*g1)
	ga = (g+(1.0-g)*g1)
	ba = (b+(1.0-b)*g1)

	rb = (r+(1.0-r)*g2)
	gb = (g+(1.0-g)*g2)
	bb = (b+(1.0-b)*g2)

	rc = (r*g3)
	gc = (g*g3)
	bc = (b*g3)

	rd = (r*g4)
	gd = (g*g4)
	bd = (b*g4)

	colors.append(mathutils.Vector((ra,ga,ba)))
	colors.append(mathutils.Vector((rb,gb,bb)))
	colors.append(mathutils.Vector((r,g,b)))
	colors.append(mathutils.Vector((rc,gc,bc)))
	colors.append(mathutils.Vector((rd,gd,bd)))
	
	return colors
	
	
# GET KULER PALETTES
def get_palettes(days=1, type='NEW'):

	import urllib.request
	from xml.dom import minidom, Node
	
	if type == 'NEW':
		listType = 'newest'
	elif type == 'RAT':
		listType = 'rating'
	else:
		listType = 'popular'
	
	# listType can be newest, rating, popular, timespan=0 = all
	url_info = urllib.request.urlopen('http://kuler-api.adobe.com//feeds/rss/get.cfm?timeSpan='+str(days)+'&listType='+listType)
		
	xmldoc = minidom.parse(url_info)

	rootNode = xmldoc.documentElement

	palettes = {}
	letter = 97
	
	for theme in xmldoc.getElementsByTagName('kuler:themeItem'):
		
		mode = theme.getElementsByTagName('kuler:swatchColorMode')
			
		if mode[0].firstChild.nodeValue == 'rgb':
			
			item = {}
			item['author'] =  theme.getElementsByTagName('kuler:authorLabel')[0].firstChild.nodeValue
			item['title'] = theme.getElementsByTagName('kuler:themeTitle')[0].firstChild.nodeValue
			item['id'] = theme.getElementsByTagName('kuler:themeID')[0].firstChild.nodeValue
			
			item['hexes'] = []
			for el in theme.getElementsByTagName('kuler:swatchHexColor'):
				item['hexes'].append(el.firstChild.nodeValue)				
			
			r = []
			
			for el in theme.getElementsByTagName('kuler:swatchChannel1'):
				r.append(el.firstChild.nodeValue)
				
			g = []
				
			for el in theme.getElementsByTagName('kuler:swatchChannel2'):
				g.append(el.firstChild.nodeValue)
				
			b = []
				
			for el in theme.getElementsByTagName('kuler:swatchChannel3'):
				b.append(el.firstChild.nodeValue)\
				
			if len(r) == len(g) == len(b) == 5:
			
				item['swatches'] = []
				
				for i in range(len(r)):
						
					c = [r[i],g[i],b[i]]
						
					item['swatches'].append(c)
						
				palettes[chr(letter)] = item
				letter += 1
			
	if len(palettes):
		bpy.context.scene['palettes'] = palettes
		
	print('Retrieved',len(palettes),'palettes')