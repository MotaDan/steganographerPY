def hide(buffer, data)
	return 'A'

def reveal(buffer)
	return 'A'

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
		testBuffer = [1, 2, 3]
		self.assertEqual(hide(testBuffer, "A"), [[1, 2, 3], [2, 3, 1], [3, 1, 2]])
		
	def test_reveal(self):
		testBuffer = [1, 2, 3]
		self.assertEqual(reveal(testBuffer), 'A')
	
if __name__ == '__main__':
	print "Preparing tests..."
	runner = unittest.TextTestRunner(verbosity = 2)
	unittest.main(testRunner = runner)