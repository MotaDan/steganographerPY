byteLen = 8

def hideByte(cleanData, val):
	hiddenData = bytearray(len(cleanData))
	mask = 1 << (byteLen - 1)
	
	for i in range(byteLen):
		maskedBit = (ord(val) & (mask >> i)) >> (byteLen - 1 - i)
		hiddenData[i] = cleanData[i] | maskedBit
	
	return hiddenData

def revealByte(hiddenData):
	revealedData = bytearray(1)
	
	for i in range(len(hiddenData)):
		leastSigBit = hiddenData[i] & 1
		revealedData[0] = revealedData[0] | (leastSigBit << (byteLen - 1 - i))
	
	return revealedData

def hideString(cleanData, val):
	hiddenData = bytearray(1)
	
	return hiddenData

def revealString(hiddenData):
	revealedStrLen = len(hiddenData) / byteLen
	revealedData = ''
	
	for i in range(0, revealedStrLen * byteLen, byteLen):
		revealedData += revealByte(hiddenData[i:i + byteLen])
	
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
		solutionData = bytearray(byteLen)
		solutionData[1] = chr(1)
		solutionData[7] = chr(1)
		self.assertEqual(hideByte(testData, 'A'), solutionData)
		
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
	
if __name__ == '__main__':
	print "Preparing tests..."
	runner = unittest.TextTestRunner(verbosity = 2)
	unittest.main(testRunner = runner)