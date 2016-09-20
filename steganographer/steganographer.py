"""Given an image and a message steganographer will hide the message in the bits of the image."""
from PIL import Image
import sys

byteLen = 8


def hideByte(cleanData, val):
	"""
	Hides a byte val in data. Returns bytes.
	
	Expects a bytes of length 8 and a character value. Will return a bytes with the character's bits hidden 
	in the least significant bit.
	"""
	hiddenData = bytearray(len(cleanData))
	mask = 1 << (byteLen - 1)
	
	for i in range(len(hiddenData)):
		maskedBit = val & (mask >> i)
		
		if maskedBit > 0:
			maskedBit = maskedBit >> (byteLen - 1 - i)
			hiddenData[i] = cleanData[i] | maskedBit
		else:
			maskedBit = ~(mask >> (byteLen - 1))
			hiddenData[i] = cleanData[i] & maskedBit
	
	return bytes(hiddenData)


def revealByte(hiddenData):
	"""Expects a bytes of length 8. Will pull out the least significant bit from each byte and return them."""
	revealedData = bytearray(1)
	
	for i in range(len(hiddenData)):
		leastSigBit = hiddenData[i] & 1
		revealedData[0] = revealedData[0] | (leastSigBit << (byteLen - 1 - i))
	
	return bytes(revealedData)


def hideString(cleanData, val):
	"""
	Hides a string val in cleanData. Returns a bytes.
	
	Expects a bytes of any length and a string value. Will return a bytes with the string's bits hidden 
	in the least significant bits. Adds null terminator to the end of the string.
	"""
	val += '\0'
	return hideData(cleanData, bytes(val, 'utf-8'))


def revealString(hiddenData):
	"""
	Returns a string hidden in hiddenData.
	
	Expects a bytes of any length. Will pull out the least significant bits from each byte and return them as 
	a string.
	"""
	revealedData = revealData(hiddenData)
	nullPos = 0
	
	for i in range(len(revealedData)):
		if revealedData[i] != 0:
			nullPos += 1
		else:
			break
	
	revealedData = revealedData[:nullPos]
	
	return revealedData.decode()


def hideData(cleanData, val):
	"""
	Hides val inside cleanData. Returns a bytes.
	
	Expects a bytes cleanData of any length and another bytes val. Will return a bytes with the val's 
	bits hidden in the least significant bits of cleanData.
	"""
	hiddenData = bytearray()
	
	for dataIndex, strIndex in zip(range(0, len(cleanData), byteLen), range(len(val))):
		hiddenByte = hideByte(cleanData[dataIndex:dataIndex + byteLen], val[strIndex])
		hiddenData.extend(hiddenByte)
	
	hiddenData = hiddenData + cleanData[len(hiddenData):]
	
	return bytes(hiddenData)


def revealData(hiddenData):
	"""
	Returns the data hidden in hiddenData.
	
	Expects a bytes hiddenData of any length. Will pull out the least significant bits from each byte and 
	return them as a bytes.
	"""
	revealedDataLen = len(hiddenData) // byteLen
	revealedData = bytearray()
	
	for i in range(0, revealedDataLen * byteLen, byteLen):
		revealedData.extend(revealByte(hiddenData[i:i + byteLen]))
	
	revealedDataLenRemainder = len(hiddenData) % byteLen
	
	if revealedDataLenRemainder > 0:
		revealedData.extend(revealByte(hiddenData[-1 * revealedDataLenRemainder:]))
	
	return bytes(revealedData)


def unpackImage(pixels):
	"""Do flatten out 2d pixels and return bytes of list."""
	unpackedPixels = []
	
	for pix in (pixels):
		for val in pix:
			unpackedPixels.append(val)
			
	return bytes(unpackedPixels)


def packImage(pixels):
	"""Do create 2d list of pixels and return the list."""
	packedPixels = []
	pixelLength = 4
	
	for i in range(0, len(pixels), pixelLength):
		packedPixels.append(tuple(pixels[i:i+pixelLength]))
	
	return packedPixels


def openBinFile(fname):
	"""Reads the file fname and returns bytes for all it's data."""
	try:
		fimage = open(fname, 'rb')
		imagebytes = fimage.read()
		
		return imagebytes
	
	except FileNotFoundError:
		print("Could not read file", fname)
		sys.exit()


def writeBinFile(fname, data):
	"""Create a file fname and writes the passed in data to it."""
	try:
		fdirty = open(fname, 'wb')
		fdirty.write(data)
		
	except IOError: # pragma: no cover
		print("Could not create file", fname)
		sys.exit()


def openImageFile(fname):
	"""Reads the file fname and returns bytes for all it's data."""
	try:
		im = Image.open(fname)
		pixels = im.getdata()
		return unpackImage(pixels)
		
	except FileNotFoundError:
		print("Could not read file", fname)
		sys.exit()


def writeImageFile(fname, ogFname, data):
	"""Create a image fname and writes the passed in data to it. Gets image properties from ogFname."""
	try:
		ogim = Image.open(ogFname)
		im = Image.new(ogim.mode, ogim.size)
		im.putdata(packImage(data))
		im.save(fname, ogim.format)
		
	except FileNotFoundError:
		print("Could not read file", ogFname)
		sys.exit()


def steganographerHide(cleanImageFile, text, dirtyImageFile=''):
	"""
	Hides text inside CleanImageFile and outputs dirtyImageFile.
	
	Takes in a clean image file name, a dirty image file name and text that will be hidden. Hides the text in 
	cleanImageFile and outputs it to dirtyImageFile.
	"""
	cleanData = openImageFile(cleanImageFile)
	dirtyData = hideString(cleanData, text)
	
	if dirtyImageFile == '':
		cleanName = cleanImageFile.split('.')[0]
		cleanExtension = cleanImageFile.split('.')[1]
		dirtyImageFile = cleanName + "Steganogrified." + cleanExtension
		
	writeImageFile(dirtyImageFile, cleanImageFile, dirtyData)
	
	return dirtyImageFile


def steganographerReveal(fimage):
	"""Reveals whatever string is hidden in the fimage."""
	dirtyData = openImageFile(fimage)
	revealedString = revealString(dirtyData)
	return revealedString
