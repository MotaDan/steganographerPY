def hide(cleanData, val):
	return ''

def reveal(hiddenData):
	hiddenText = bytearray(1)
	
	for i in range(len(hiddenData)):
		leastSigBit = hiddenData[i] & 1
		hiddenText[0] = hiddenText[0] | (leastSigBit << (7 - i))
	
	return str(hiddenText)

# Testing class
import unittest
import time

class TestSteganographer(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()
	
	def tearDown(self):
		t = time.time() - self.startTime
		print "Ran in %.3fs " % (t),
	
	def test_hide(self):
		testBuffer = bytearray(8)
		solutionBuff = bytearray(8)
		solutionBuff[1] = chr(1)
		solutionBuff[7] = chr(1)
		self.assertEqual(hide(testBuffer, 'A'), solutionBuff)
		
	def test_reveal(self):
		testBuffer = bytearray(8)
		testBuffer[1] = chr(1)
		testBuffer[7] = chr(1)
		self.assertEqual(reveal(testBuffer), 'A')
	
if __name__ == '__main__':
	print "Preparing tests..."
	runner = unittest.TextTestRunner(verbosity = 2)
	unittest.main(testRunner = runner)