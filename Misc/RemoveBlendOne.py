import os, glob

print '\nStarting cleanup!\n'

def removeAll(dir):

	thisDir = dir+'/*'
	
	# Get all the files in this directory
	cleanFiles = glob.glob(thisDir)

	print '- found',str(len(cleanFiles)),'files in', thisDir
	
	cnt = 0
	 
	# Loop through all items
	for c, fName in enumerate(cleanFiles):
		
		# Testing so only do the first image
		if 1 or not c:
	
			#Go into directories to resize in there
			if os.path.isdir(fName):
				removeAll(fName)
				
			else:
			
				# Get the file extension in lower case to see if we are dealing with a blend1 or 2
				fileName, fileExtension = os.path.splitext(fName)
				lowExtension = fileExtension.lower()
				
				# Make sure it's an image
				if lowExtension == '.blend1' or lowExtension == '.blend2':
					os.remove(fName)
					cnt += 1
					
	if cnt:
		print '	- removed',cnt,'files'
	
removeAll('.\\')

# Pause the system
print ' -- DONE --'
print ''
os.system('pause')