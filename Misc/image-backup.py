import math, os, glob, PIL, shutil
from PIL import Image

print '\nStarting resize!\n'

targetDir = '\\\\BUFFALO\\share\\pictures\\'
checkDir = 'C:\\Users\\Macouno\\Pictures\\'
bigDir = 'high-res\\'
smallDir = 'low-res\\'


# CREATE A NEW COPY ON THE SERVER
def backupAll(dir, depth, targetDir, originDir):

	thisDir = dir+'/*'

	imageFiles = glob.glob(thisDir) #('*.png')

	print '\n',depth,'- found',str(len(imageFiles)),'items in', thisDir, '\n'
	
	# Loop through all items
	for c, fName in enumerate(imageFiles):
	
		#Go into directories to resize in there
		if os.path.isdir(fName):
		
			backupAll(fName, depth+'  ', targetDir, originDir)
			
		else:
		
			fileName, fileExtension = os.path.splitext(fName)
			baseName = os.path.basename(fName)
			
			lowExtension = fileExtension.lower()
			
			# Make sure it's an image
			if lowExtension == '.jpg' or lowExtension == '.png':
				
				# No need to continue if the file exists
				outfile = fName.replace('.\\', targetDir)
				
				if not os.path.exists(outfile):
				
					outfile = outfile.replace('\\'+baseName,'')
					print(depth,'copy',baseName,' to',outfile)
					if not os.path.isdir(outfile):
						os.makedirs(outfile) # create all directories, raise an error if it already exists
					shutil.copy(fName, outfile)
					
# SEE IF A FILE EXISTS AND CAN BE REMOVED IF IT DOESN"T!!!!
def checkAll(targetDir, originalTarget, checkDir,depth):
	
	thisDir = targetDir+'/*'
	
	imageFiles = glob.glob(thisDir) #('*.png')
	# Loop through all items
	print '\n',depth,'- found',str(len(imageFiles)),'items in', thisDir, '\n'
	
	for c, fName in enumerate(imageFiles):
		#Go into directories to resize in there
		if os.path.isdir(fName):
			
			checkAll(fName, originalTarget, checkDir,depth+' ')
			
		else:
		
			fileName, fileExtension = os.path.splitext(fName)
			lowExtension = fileExtension.lower()
			
			# Make sure it's an image
			if lowExtension == '.jpg' or lowExtension == '.png':
			
				checkFile = fName.replace(originalTarget, checkDir)
				
				if not os.path.exists(checkFile):
					print(depth,checkFile,'does not exist.. REMOVING')
					os.remove(fName)				
					
	
checkAll(targetDir, targetDir, checkDir, '')

backupAll('.\\'+bigDir, '  ', targetDir, bigDir)
backupAll('.\\'+smallDir, '  ', targetDir, smallDir)



	
	
# Pause the system
print ' -- DONE --'
print ''
os.system('pause')