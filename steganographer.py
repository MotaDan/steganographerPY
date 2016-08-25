def hideByte(cleanData, val):
	hiddenData = bytearray(len(cleanData))
	mask = 1 << 7
	
	for i in range(8):
		maskedBit = (ord(val) & (mask >> i)) >> (7 - i)
		hiddenData[i] = cleanData[i] | maskedBit
	
	return hiddenData

def revealByte(hiddenData):
	revealedText = bytearray(1)
	
	for i in range(len(hiddenData)):
		leastSigBit = hiddenData[i] & 1
		revealedText[0] = revealedText[0] | (leastSigBit << (7 - i))
	
	return str(revealedText)

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
		testData = bytearray(8)
		solutionData = bytearray(8)
		solutionData[1] = chr(1)
		solutionData[7] = chr(1)
		self.assertEqual(hideByte(testData, 'A'), solutionData)
		
	def test_revealbyte(self):
		testData = bytearray(8)
		testData[1] = chr(1)
		testData[7] = chr(1)
		self.assertEqual(revealByte(testData), 'A')
	
if __name__ == '__main__':
	print "Preparing tests..."
	runner = unittest.TextTestRunner(verbosity = 2)
	unittest.main(testRunner = runner)