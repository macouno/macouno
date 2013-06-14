import random

# Once in how many layers can it change temp??
rd = 5

# Input file name
fIn = 'C:\Users\Macouno\Desktop\laywoo.gcode'

# Output file name
fOut = 'C:\Users\Macouno\Desktop\laywoo-out.gcode'

with open(fIn,'r') as f:
	
	newlines = []
	i = 0
	for line in f.readlines():
	
		if line.startswith('(Slice'):
			print('FOUNDSLICE')
			i+=1
			if not i % rd:
				newlines.append(line.replace('(Slice', 'M104 S'+str(random.randint(180,210))+' T0\n(Slice'))
			else:
				newlines.append(line)
		else:
			newlines.append(line)
		
with open(fOut, 'w') as f:
	for line in newlines:
		f.write(line)