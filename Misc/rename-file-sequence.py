import os

folder = 'timelapse-box'

for i, filename in enumerate(os.listdir(folder)):

	print i,filename
	newName = str(i)+'.jpg'
	os.rename(folder+'\\'+filename, folder+'\\'+newName)