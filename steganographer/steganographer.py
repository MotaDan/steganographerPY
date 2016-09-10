import argparse
from PIL import Image

byteLen = 8

# Expects a bytearray of length 8 and a character value. Will return a bytearray with the character's bits 
# hidden in the least significant bit.
def hideByte(cleanData, val):
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
	
	return hiddenData


# Expects a bytearray of length 8. Will pull out the least significant bit from each byte and return them.
def revealByte(hiddenData):
	revealedData = bytearray(1)
	
	for i in range(len(hiddenData)):
		leastSigBit = hiddenData[i] & 1
		revealedData[0] = revealedData[0] | (leastSigBit << (byteLen - 1 - i))
	
	return revealedData


# Expects a bytearray of any length and a string value. Will return a bytearray with the string's bits 
# hidden in the least significant bits. Adds null terminator to the end of the string.
def hideString(cleanData, val):
	val += '\0'
	return hideData(cleanData, bytearray(val, 'utf-8'))


# Expects a bytearray of any length. Will pull out the least significant bits from each byte and 
# return them as a string.
def revealString(hiddenData):
	revealedData = revealData(hiddenData)
	nullPos = 0
	
	for i in range(len(revealedData)):
		if revealedData[i] != 0:
			nullPos += 1
		else:
			break
	
	revealedData = revealedData[:nullPos]
	
	return revealedData.decode()


# Expects a bytearray cleanData of any length and another bytearray val. Will return a bytearray with the val's bits 
# hidden in the least significant bits of cleanData.
def hideData(cleanData, val):
	hiddenData = bytearray()
	
	for dataIndex, strIndex in zip(range(0, len(cleanData), byteLen), range(len(val))):
		hiddenByte = hideByte(cleanData[dataIndex:dataIndex + byteLen], val[strIndex])
		hiddenData.extend(hiddenByte)
	
	hiddenData = hiddenData + cleanData[len(hiddenData):]
	
	return hiddenData


# Expects a bytearray hiddenData of any length. Will pull out the least significant bits from each byte and 
# return them as a byteArray.
def revealData(hiddenData):
	revealedDataLen = len(hiddenData) // byteLen
	revealedData = bytearray()
	
	for i in range(0, revealedDataLen * byteLen, byteLen):
		revealedData.extend(revealByte(hiddenData[i:i + byteLen]))
	
	revealedDataLenRemainder = len(hiddenData) % byteLen
	
	if revealedDataLenRemainder > 0:
		revealedData.extend(revealByte(hiddenData[-1 * revealedDataLenRemainder:]))
	
	return revealedData


def unpackImage(pixels):
	unpackedPixels = []
	
	for pix in (pixels):
		for val in pix:
			unpackedPixels.append(val)
			
	return bytes(unpackedPixels)


def packImage(pixels):
	packedPixels = []
	pixelLength = 4
	
	for i in range(0, len(pixels), pixelLength):
		packedPixels.append(tuple(pixels[i:i+pixelLength]))
	
	return packedPixels


# Reads the file fname and returns bytes for all it's data.
def openBinFile(fname):
	fimage = open(fname, 'rb')
	imagebytes = fimage.read()
	
	return imagebytes


# Create a file fname and writes the passed in data to it.
def writeBinFile(fname, data):
	fdirty = open(fname, 'wb')
	fdirty.write(data)


# Reads the file fname and returns bytes for all it's data.
def openImageFile(fname):
	im = Image.open(fname)
	pixels = im.getdata()
	
	return unpackImage(pixels)


# Create a image fname and writes the passed in data to it. Gets image properties from ogFname.
def writeImageFile(fname, ogFname, data):
	ogim = Image.open(ogFname)
	im = Image.new(ogim.mode, ogim.size)
	im.putdata(packImage(data))
	im.save(fname)


# Takes in a clean image file name, a dirty image file name and text that will be hidden. 
# Hides the text in cleanImageFile and outputs it to dirtyImageFile.
def steganographerHide(cleanImageFile, text, dirtyImageFile=''):
	cleanData = openImageFile(cleanImageFile)
	dirtyData = hideString(cleanData, text)
	
	if dirtyImageFile == '':
		cleanName = cleanImageFile.split('.')[0]
		cleanExtension = cleanImageFile.split('.')[1]
		dirtyImageFile = cleanName + "Steganogrified." + cleanExtension
		
	writeImageFile(dirtyImageFile, cleanImageFile, dirtyData)


# Reveals whatever string is hidden in the fimage.
def steganographerReveal(fimage):
	dirtyData = openImageFile(fimage)
	revealedString = revealString(dirtyData)
	return revealedString

def main(args):
	args = parse_args(args)
	parser = argparse.ArgumentParser(description="hides a message in a file or returns a message hidden in a file")
	parser.add_argument("input", help="file to hide a message in or file to reveal a message from")
	parser.add_argument("-m", "--message", help="message to be hidden in the input file")
	parser.add_argument("-o", "--output", help="name of output file to hide message in. If not given will append Steganogrified to input name.")
	args = parser.parse_args()
	
	if args.input:
		if args.message:
			if args.output:
				steganographerHide(args.input, args.message, args.output)
			else:
				steganographerHide(args.input, args.message)
			print("The message has been hidden.")
		else:
			print("The hidden message was...")
			print(steganographerReveal(args.input))


def run():
	main(sys.argv[1:])


if __name__ == '__main__':
	run()
