class liberty():

	# Initialise the class
	def __init__(self, keytype='pi', key=''):
	
		# Type is one of 'bool', 'int', 'float', 'select'
		self.type = type
		
		# Key can be 'pi', 'e', 'string'
		if keytype == 'pi':
			self.key = list('31415926535897932384626433832795028841971693993751')
			
		elif keytype == 'e':
			self.key = list('27182818284590452353602874713526624977572470936999')
			
		elif keytype == 'now':
			import time
			key = str(time.time())
			self.key = list(key.replace('.',''))
			
		elif keytype == 'random':
			import random
			random.seed(key)
			key = random.random() * 10
			key = str(key)
			self.key = list(key.replace('.',''))
			
		else:
			self.key = list(key)
			
		self.leng = len(key)
		self.pos = 0
	
	
	# Choose from a number of options
	def Choose(self, type='bool', options={}, desk=''):
    
		letter = self.key[self.pos]
		nr = ord(letter)
		
		if type == 'select':
			result =  self.select(nr, options)
			
		elif type == 'float' or type == 'int':
			result = self.minmax(nr, options)
			
			if type == 'int':
				result = int(round(result))
			
		else: #bool
			
			if nr % 2:
				result = True
			else:
				result = False
	
		if desk:
			try:
				print(' ',letter,'-',desk.ljust(22, ' '),'=',result.rna_type.name, result.name)
			except:
				try:
					print(' ',letter,'-',desk.ljust(22, ' '),'=',result.rna_type.name, result.index)
				except:
					print(' ',letter,'-',desk.ljust(22, ' '),'=',result)
			
		self.pos += 1
		if self.pos == self.leng: self.pos = 0
			
		return result
		
	
	
	# Get a value between a minimum and maximum
	def minmax(self,nr,options):
	
		if nr == 32:
			nr = 13

		else:
			# Make upper case into lower case
			if nr > 64 and nr < 91:
				nr += 32

			# Make lower case 0 -> 25
			if nr > 96 and nr < 123:
				nr -= 97

			# Make everything else fit
			while nr > 26:
				nr -= 26

			# Make sure the only neutral one is the space
			if nr > 12:
				nr += 1

		choice = (1.0 / 26.0) * float(nr)
	
		dif = options['max'] - options['min']
		
		result = (dif * choice) + options['min']
		
		if self.type == 'int':
			result = int(round(result))
		
		return result
		
		
		
	# Select one in the dict of options
	def select(self, nr, options):
	
		leng = len(options)
	
		# Make upper case into lower case
		if nr > 64 and nr < 91:
			nr += 32
			
		# Make sure the range is correct
		while nr < 97:
			nr+= leng
			
		topLim = (96 + leng)
		while nr > topLim:
			nr -= leng
			
		return options[chr(nr)]
		
		
		
	def getNumber(self, options):
	
		optLen = len(options)
	
		nrLen = 0
		number = 0
		
		while nrLen < optLen:
		
			letter = self.key[self.pos]
			nr = ord(letter)
			nr = formatNumber(nr)
			number += nr
			nrLen += 27

			self.pos += 1
			if self.pos == self.leng: self.pos = 0
			
		return number
		
		
	# Make sure the number is between 0 and 27
	def formatNumber(self, nr):
	
		if nr == 32:
			nr = 13

		else:
			# Make upper case into lower case
			if nr > 64 and nr < 91:
				nr += 32

			# Make lower case 0 -> 25
			if nr > 96 and nr < 123:
				nr -= 97

			# Make everything else fit
			while nr > 26:
				nr -= 26

			# Make sure the only neutral one is the space
			if nr > 12:
				nr += 1
				
		return nr
		
		
	# Make a compatible dict out of any list
	def makeDict(self, lis):
	
		dct = {}
	
		letter = 97
		dct = {}
		
		for item in lis:
			dct[chr(letter)] = item
			letter += 1
			
		return dct