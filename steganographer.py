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
# hidden in the least significant bits.
def hideString(cleanData, val):
	return hideData(cleanData, bytearray(val))

# Expects a bytearray of any length. Will pull out the least significant bits from each byte and 
# return them as a string.
def revealString(hiddenData):
	return str(revealData(hiddenData))
	
# Expects a bytearray cleanData of any length and another bytearray val. Will return a bytearray with the val's bits 
# hidden in the least significant bits of cleanData.
def hideData(cleanData, val):
	hiddenData = bytearray()
	
	for dataIndex, strIndex in zip(range(0, len(cleanData), byteLen), range(len(val))):
		hiddenByte = hideByte(cleanData[dataIndex:dataIndex + byteLen], val[strIndex])
		hiddenData.extend(hiddenByte)
	
	return hiddenData

# Expects a bytearray hiddenData of any length. Will pull out the least significant bits from each byte and 
# return them as a byteArray.
def revealData(hiddenData):
	revealedDataLen = len(hiddenData) / byteLen
	revealedData = bytearray()
	
	for i in range(0, revealedDataLen * byteLen, byteLen):
		revealedData.extend(revealByte(hiddenData[i:i + byteLen]))
	
	revealedDataLenRemainder = len(hiddenData) % byteLen
	
	if revealedDataLenRemainder > 0:
		revealedData.extend(revealByte(hiddenData[-1 * revealedDataLenRemainder:]))
	
	return revealedData

# Testing class
import unittest
import time

class TestSteganographer(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()
	
	def tearDown(self):
		t = time.time() - self.startTime
		print "Ran in %.3fs " % (t),
	
	def test_hideByte(self):
		testData = bytearray(byteLen)
		dataToHide = bytearray('A')
		solutionData = bytearray(byteLen)
		solutionData[1] = chr(1)
		solutionData[7] = chr(1)
		self.assertEqual(hideByte(testData, dataToHide[0]), solutionData)
		
	def test_revealByte(self):
		testData = bytearray(byteLen)
		testData[1] = chr(1)
		testData[7] = chr(1)
		self.assertEqual(revealByte(testData), 'A')
	
	def test_hideString(self):
		testData = bytearray(byteLen * 3)
		solutionData = bytearray(byteLen * 3)
		solutionData[1] = chr(1)
		solutionData[7] = chr(1)
		solutionData[9] = chr(1)
		solutionData[14] = chr(1)
		solutionData[17] = chr(1)
		solutionData[22] = chr(1)
		solutionData[23] = chr(1)
		self.assertEqual(hideString(testData, 'ABC'), solutionData)
		
	def test_revealString(self):
		testData = bytearray(byteLen * 3)
		testData[1] = chr(1)
		testData[7] = chr(1)
		testData[9] = chr(1)
		testData[14] = chr(1)
		testData[17] = chr(1)
		testData[22] = chr(1)
		testData[23] = chr(1)
		self.assertEqual(revealString(testData), 'ABC')
	
	def test_hideData(self):
		testData = bytearray(byteLen * 3)
		dataToHide = bytearray('ABC')
		solutionData = bytearray(byteLen * 3)
		solutionData[1] = chr(1)
		solutionData[7] = chr(1)
		solutionData[9] = chr(1)
		solutionData[14] = chr(1)
		solutionData[17] = chr(1)
		solutionData[22] = chr(1)
		solutionData[23] = chr(1)
		self.assertEqual(hideData(testData, dataToHide), solutionData)
		self.assertEqual(hideData(testData[:4], dataToHide), solutionData[:4])
	
	def test_revealData(self):
		solutionData = bytearray('ABC')
		testData = bytearray(byteLen * 3)
		testData[1] = chr(1)
		testData[7] = chr(1)
		testData[9] = chr(1)
		testData[14] = chr(1)
		testData[17] = chr(1)
		testData[22] = chr(1)
		testData[23] = chr(1)
		self.assertEqual(revealData(testData), solutionData)
		
	def test_revealDataPartial(self):
		solutionData = bytearray('AB@')
		testData = bytearray(byteLen * 3)	#Will contain 'ABC' but will be truncated when passed to revealData
		testData[1] = chr(1)
		testData[7] = chr(1)
		testData[9] = chr(1)
		testData[14] = chr(1)
		testData[17] = chr(1)
		testData[22] = chr(1)
		testData[23] = chr(1)
		self.assertEqual(revealData(testData[:len(testData) - byteLen/2]), solutionData)

	# Testing that the string entered is the string returned. The data it is stored in is the exact length needed.
	def test_steganographerNullData(self):
		testString = "This is a test String"
		blankData = bytearray(len(testString) * byteLen)
		
		hiddenData = hideString(blankData, testString)
		revealedString = revealString(hiddenData)
		
		self.assertEqual(testString, revealedString)
		
	# Testing that when the data is too small, by a full byte, that everything that can be returned is.
	def test_steganographerShortData(self):
		testString = "This is a test String"
		blankData = bytearray(len(testString) * byteLen - byteLen)
		
		hiddenData = hideString(blankData, testString)
		revealedString = revealString(hiddenData)
		
		self.assertEqual(testString[:len(testString) - 1], revealedString)
		
	# Testing that when the data is too small, by a half byte, that everything that can be returned is.
	def test_steganographerShortPartialData(self):
		testString = "This is a test String"
		blankData = bytearray(len(testString) * byteLen - byteLen / 2)
		
		hiddenData = hideString(blankData, testString)
		revealedString = revealString(hiddenData)
		
		self.assertEqual(testString[:len(testString) - 1] + chr(ord(testString[-1]) >> (byteLen/2) << (byteLen/2)), revealedString)
	
if __name__ == '__main__':
	print "Preparing tests..."
	runner = unittest.TextTestRunner(verbosity = 2)
	unittest.main(testRunner = runner)