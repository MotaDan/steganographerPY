def hide(buffer, data):
	return ''

def reveal(buffer):
	return ''

# Testing class
import unittest
import time

class TestSoccerSuperstition(unittest.TestCase):
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