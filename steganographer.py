byteLen = 8

# Expects a bytearray of length 8 and a character value. Will return a bytearray with the character's bits 
# hidden in the least significant bit.
def hideByte(cleanData, val):
	hiddenData = bytearray(len(cleanData))
	mask = 1 << (byteLen - 1)
	
	for i in range(len(hiddenData)):
		maskedBit = (val & (mask >> i)) >> (byteLen - 1 - i)
		hiddenData[i] = cleanData[i] | maskedBit
	
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


# Reads the file fname and returns bytes for all it's data.
def openCleanFile(fname):
	fimage = open(fname, 'rb')
	imagebytes = fimage.read()
	
	return imagebytes


# Create a file fname and writes the passed in data to it.
def writeDirtyFile(fname, data):
	fdirty = open(fname, 'wb')
	fdirty.write(data)


# Takes in a clean image file name, a dirty image file name and text that will be hidden. 
# Hides the text in cleanImageFile and outputs it to dirtyImageFile.
def steganographerHide(cleanImageFile, dirtyImageFile, text=''):
	cleanData = openCleanFile(cleanImageFile)
	dirtyData = hideString(cleanData, text)
	writeDirtyFile(dirtyImageFile, dirtyData)


# Reveals whatever string is hidden in the fimage.
def steganographerReveal(fimage):
	dirtyData = openCleanFile(fimage)
	revealedString = revealString(dirtyData)
	return revealedString


# Testing class
import unittest
import time

class TestSteganographer(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()
	
	
	def tearDown(self):
		t = time.time() - self.startTime
		#print("Ran in %.3fs " % (t))
	
	
	# Testing that the hideByte function does hide a byte and returns the testData with that byte hidden.
	def test_hideByte(self):
		testData = bytearray(b'\x01' * byteLen)
		dataToHide = bytearray('A', 'utf-8')
		solutionData = bytearray(byteLen)
		solutionData[1] = 1
		solutionData[7] = 1
		
		self.assertEqual(hideByte(testData, dataToHide[0]), solutionData)
	
	
	# Testing that the revealByte function returns a bytearray of the hidden byte. 
	def test_revealByte(self):
		testData = bytearray(b'\x01' * byteLen)
		testData[1] = 1
		testData[7] = 1
		solutionData = bytearray('A', 'utf-8')
		
		self.assertEqual(revealByte(testData), solutionData)
	
	
	# Testing that hideString takes in a string and bytearray and hides the string in that bytearray.
	def test_hideString(self):
		testData = bytearray(b'\x01' * byteLen * 3)
		solutionData = bytearray(byteLen * 3)
		solutionData[1] = 1
		solutionData[7] = 1
		solutionData[9] = 1
		solutionData[14] = 1
		solutionData[17] = 1
		solutionData[22] = 1
		solutionData[23] = 1
		
		self.assertEqual(hideString(testData, 'ABC'), solutionData)
	
	
	# Testing that revealString returns a string of the data that was hidden in testData.
	def test_revealString(self):
		testData = bytearray(b'\x01' * byteLen * 4)
		testData[1] = 1
		testData[7] = 1
		testData[9] = 1
		testData[14] = 1
		testData[17] = 1
		testData[22] = 1
		testData[23] = 1
		
		self.assertEqual(revealString(testData), 'ABC')
	
	
	# Testing that hideData will hide one bytearray inside another.
	def test_hideData(self):
		testData = bytearray(b'\x01' * byteLen * 4)
		dataToHide = bytearray('ABC', 'utf-8')
		solutionData = bytearray(byteLen * 4)
		solutionData[1] = 1
		solutionData[7] = 1
		solutionData[9] = 1
		solutionData[14] = 1
		solutionData[17] = 1
		solutionData[22] = 1
		solutionData[23] = 1
		
		self.assertEqual(hideData(testData, dataToHide), solutionData)
	
	
	# Testing that hideData will work correctly when given a testData bytearray that is too short to contain the data given.
	def test_hideDataPartial(self):
		testData = bytearray(b'\x01' * byteLen * 3)
		dataToHide = bytearray('ABC', 'utf-8')
		solutionData = bytearray(byteLen * 3)
		solutionData[1] = 1
		solutionData[7] = 1
		solutionData[9] = 1
		solutionData[14] = 1
		solutionData[17] = 1
		solutionData[22] = 1
		solutionData[23] = 1
		
		# Testing when only half a byte is passed in for the data that contains the hidden text.
		self.assertEqual(hideData(testData[:4], dataToHide), solutionData[:4])
	
	
	# Testing that revealData will return the correct data that is hidden inside the testData.
	def test_revealData(self):
		testData = bytearray(b'\x01' * byteLen * 3)
		testData[1] = 1
		testData[7] = 1
		testData[9] = 1
		testData[14] = 1
		testData[17] = 1
		testData[22] = 1
		testData[23] = 1
		solutionData = bytearray('ABC', 'utf-8')
		
		self.assertEqual(revealData(testData), solutionData)
	
	
	# Testing that reveal data will return as much data as possible when the testData passed in is too small for the data to be hidden.
	def test_revealDataPartial(self):
		testData = bytearray(b'\x01' * byteLen * 3)	#Will contain 'ABC' but will be truncated when passed to revealData
		testData[1] = 1
		testData[7] = 1
		testData[9] = 1
		testData[14] = 1
		testData[17] = 1
		testData[22] = 1
		testData[23] = 1
		solutionData = bytearray('AB@', 'utf-8')
		
		self.assertEqual(revealData(testData[:-byteLen // 2]), solutionData)
	
	
	# Testing that opening the file works.
	def test_openCleanFile(self):
		cleanFile = "testImageClean.png"
		fileData = openCleanFile(cleanFile)
		
		self.assertEqual(fileData, open(cleanFile, 'rb').read())
	
	
	# Testing that writing the file works as expected.
	def test_writeDirtyFile(self):
		cleanFile = "testImageClean.png"
		dirtyFile = "testImageDirty.png"
		data = hideString(openCleanFile("testImageClean.png"), "Text that should be hidden.")
		writeDirtyFile(dirtyFile, data)
		
		self.assertFalse(open(cleanFile, 'rb').read() == open(dirtyFile, 'rb').read())
	
	
	# Testing that a string will correctly be hidden in a new image.
	def test_steganographerHide(self):
		cleanImage = "testImageClean.png"
		dirtyImage = "testImageDirty.png"
		steganographerHide(cleanImage, dirtyImage, "Text that should be hidden.")
		
		self.assertFalse(open(cleanImage, 'rb').read() == open(dirtyImage, 'rb').read())
	
	
	# Testing that a string is found in the dirty image.
	def test_steganographerReveal(self):
		cleanImage = "testImageClean.png"
		dirtyImage = "testImageDirty.png"
		hiddenMessage = "Text that should be hidden."
		steganographerHide(cleanImage, dirtyImage, hiddenMessage)
		
		print(steganographerReveal(dirtyImage))
		self.assertEqual(steganographerReveal(dirtyImage), hiddenMessage)
		
	
	# Testing that the string entered is the string returned. The data it is stored in is the exact length needed.
	def test_steganographerNullData(self):
		testString = "This is a test String"
		testData = bytearray(testString, 'utf-8')
		blankData = bytearray(b'\x01' * len(testString) * byteLen)
		
		hiddenString = hideString(blankData, testString)
		revealedString = revealString(hiddenString)
		
		hiddenData = hideData(blankData, testData)
		revealedData = revealData(hiddenData)
		
		self.assertEqual(testString, revealedString)
		self.assertEqual(testData, revealedData)
	
	
	# Testing that when the data is too small, by a full byte, that everything that can be returned is returned.
	def test_steganographerShortData(self):
		testString = "This is a test String"
		testData = bytearray(testString, 'utf-8')
		blankData = bytearray(b'\x01' * (len(testString) * byteLen - byteLen))
		
		hiddenString = hideString(blankData, testString)
		revealedString = revealString(hiddenString)
		
		hiddenData = hideData(blankData, testData)
		revealedData = revealData(hiddenData)
		
		self.assertEqual(testString[:-1], revealedString)
		self.assertEqual(testData[:-1], revealedData)
	
	
	# Testing that when the data is too small, by a half byte, that everything that can be returned is returned.
	def test_steganographerShortPartialData(self):
		testString = "This is a test String"
		solutionString = testString[:-1] + chr(ord(testString[-1]) >> byteLen // 2 << byteLen // 2)
		testData = bytearray(testString, 'utf-8')
		solutionData = testData
		solutionData[-1] = solutionData[-1] >> byteLen // 2 << byteLen // 2
		blankData = bytearray(b'\x01' * (len(testString) * byteLen - byteLen // 2))
		
		hiddenString = hideString(blankData, testString)
		revealedString = revealString(hiddenString)
		
		hiddenData = hideData(blankData, testData)
		revealedData = revealData(hiddenData)
		
		self.assertEqual(solutionString, revealedString)
		self.assertEqual(solutionData, revealedData)
	
	
if __name__ == '__main__':
	print("Preparing tests...")
	runner = unittest.TextTestRunner(verbosity = 2)
	unittest.main(testRunner = runner)
