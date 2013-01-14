import bpy, mathutils


# Hex to rgb conversion and reverse!
HEX = '0123456789abcdef'

def hex_to_rgb(triplet):
    triplet = triplet.lower()
    return (HEX.index(triplet[0])*16 + HEX.index(triplet[1]),
            HEX.index(triplet[2])*16 + HEX.index(triplet[3]),
            HEX.index(triplet[4])*16 + HEX.index(triplet[5]))

def rgb_to_hex(rgb):
    return hex(rgb[0])[2:] + hex(rgb[1])[2:] + hex(rgb[2])[2:]
	


# Make sure the angle between the two vectors is exactly a certain one (v1, v2, angle in degrees)
def rotate_vector_to_vector(vec1, vec2, deg):
	cross =vec1.cross(vec2)
	vec = float(vec1.angle(vec2) - deg)
	mat = mathutils.Matrix.Rotation(vec, 3, cross)
	return (vec1 * mat)
	


# Get the roman numeral representing an int
def int_to_roman(input):
  
	if type(input) != type(1):
		print("Expected integer, got",type(input))
		return 'error'
	if not 0 < input < 4000:
		print("Argument must be between 1 and 4000"  )
		return 'error'
	ints = (1000,900,500,400,100, 90,50,40,10,9,5,4,1)
	nums = ('M','CM','D','CD','C','XC','L','XL','X','IX','V','IV','I')
	result = ""
	for i in range(len(ints)):
		count = int(input / ints[i])
		result += nums[i] * count
		input -= ints[i] * count
	return result
	
	
	
# Make a number neat 4 long (with zeroes in front
def nr4(number):
	return str(number).rjust(4, '0')
	
	
	
# Get a list with the items that are in both list a and b
def intersection(a, b):
	intersection = [i for i in a if i in b]
	return intersection