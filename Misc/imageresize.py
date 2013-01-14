import math, os, glob, PIL
from PIL import Image

print '\nStarting resize!\n'

bigDir = 'high-res\\'
smallDir = 'low-res\\'

# image sizes
tileMax = 1280, 1280


def resizeAll(dir, depth, tileMax, bigDir, smallDir):

	thisDir = dir+'/*'

	imageFiles = glob.glob(thisDir) #('*.png')

	print '\n',depth,'- found',str(len(imageFiles)),'items in', thisDir, '\n'
	
	# Loop through all items
	for c, fName in enumerate(imageFiles):
	
		# Testing so only do the first image
		if 1 or not c:
	
			#Go into directories to resize in there
			if os.path.isdir(fName):
			
				resizeAll(fName, depth+'  ', tileMax, bigDir, smallDir)
				
			else:
			
				fileName, fileExtension = os.path.splitext(fName)
				
				lowExtension = fileExtension.lower()
				
				# Make sure it's an image
				if lowExtension == '.jpg' or lowExtension == '.png':
					
					# No need to continue if the file exists
					outfile = fName.replace('.\\'+bigDir, '.\\'+smallDir)
					outfile = outfile.replace('.png', '.jpg')
					if not os.path.exists(outfile):
					
						# Make sure the directory exists
						dirName = os.path.dirname(outfile)
						if not os.path.exists(dirName):
							os.makedirs(dirName)
						
						print depth,'   ',(c+1),outfile
						
						try:
							# Make the thumbnail
							im = Image.open(fName)
							im.thumbnail(tileMax, Image.ANTIALIAS)
						
							# Save the file!
							im.save(outfile, "JPEG")
						except:
							print depth,'   ERROR CREATING ',(c+1),outfile
					

			
	
	
resizeAll('.\\'+bigDir, '  ', tileMax, bigDir, smallDir)

# Pause the system
print ' -- DONE --'
print ''
os.system('pause')