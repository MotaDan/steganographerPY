"""Testing script"""
import unittest
import time
import sys
import os
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from steganographer.steganographer import *

class TestSteganographer(unittest.TestCase):
	"""The class that contains the tests."""
	cleanPNGLocation = "tests/testImageClean.png"
	
	def setUp(self):
		self.startTime = time.time()
	
	
	def tearDown(self):
		#t = time.time() - self.startTime
		#print("Ran in %.3fs " % (t))
		pass
	
	
	def test_hideByte(self):
		"""Testing that the hideByte function does hide a byte and returns the testData with that byte hidden."""
		testData = bytearray(b'\x01' * byteLen)
		dataToHide = bytearray('A', 'utf-8')
		solutionData = bytearray(byteLen)
		solutionData[1] = 1
		solutionData[7] = 1
		
		self.assertEqual(hideByte(testData, dataToHide[0]), solutionData)
	
	
	def test_revealByte(self):
		"""Testing that the revealByte function returns a bytearray of the hidden byte."""
		testData = bytearray(byteLen)
		testData[1] = 1
		testData[7] = 1
		solutionData = bytearray('A', 'utf-8')
		
		self.assertEqual(revealByte(testData), solutionData)
	
	
	def test_hideString(self):
		"""Testing that hideString takes in a string and bytearray and hides the string in that bytearray."""
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
	
	
	def test_revealString(self):
		"""Testing that revealString returns a string of the data that was hidden in testData."""
		testData = bytearray(byteLen * 4)
		testData[1] = 1
		testData[7] = 1
		testData[9] = 1
		testData[14] = 1
		testData[17] = 1
		testData[22] = 1
		testData[23] = 1
		
		self.assertEqual(revealString(testData), 'ABC')
	
	
	def test_hideData(self):
		"""Testing that hideData will hide one bytearray inside another."""
		testData = bytearray(b'\x01' * byteLen * 4)
		dataToHide = bytearray('ABC', 'utf-8')
		solutionData = bytearray(byteLen * 3) + bytearray(b'\x01' * byteLen)
		solutionData[1] = 1
		solutionData[7] = 1
		solutionData[9] = 1
		solutionData[14] = 1
		solutionData[17] = 1
		solutionData[22] = 1
		solutionData[23] = 1
		
		self.assertEqual(hideData(testData, dataToHide), solutionData)
	
	
	def test_hideDataPartial(self):
		"""Testing that hideData will work when given a testData bytearray that is too short to hold the data"""
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
	
	
	def test_revealData(self):
		"""Testing that revealData will return the correct data that is hidden inside the testData."""
		testData = bytearray(byteLen * 3)
		testData[1] = 1
		testData[7] = 1
		testData[9] = 1
		testData[14] = 1
		testData[17] = 1
		testData[22] = 1
		testData[23] = 1
		solutionData = bytearray('ABC', 'utf-8')
		
		self.assertEqual(revealData(testData), solutionData)
	
	
	def test_revealDataPartial(self):
		"""Testing that reveal data will return as much data as possible when the testData passed in is too small for 
		the data to be hidden."""
		testData = bytearray(byteLen * 3)	#Will contain 'ABC' but will be truncated when passed to revealData
		testData[1] = 1
		testData[7] = 1
		testData[9] = 1
		testData[14] = 1
		testData[17] = 1
		testData[22] = 1
		testData[23] = 1
		solutionData = bytearray('AB@', 'utf-8')
		
		self.assertEqual(revealData(testData[:-byteLen // 2]), solutionData)
	
	
	def test_unpackImage(self):
		"""Testing that unpacking returns a bytes full of all the pixels flattened."""
		pixel = 1, 2, 3, 4
		solutionPixels = bytes(list(pixel * 4))
		testPixels = []
		
		for _ in range(4):
			testPixels.append(pixel)
		
		unpacked = unpackImage(testPixels)
		
		self.assertEqual(unpacked, solutionPixels)
	
	
	def test_packImage(self):
		"""Testing that packing returns a list with tuples of length 4."""
		pixel = 1, 2, 3, 4
		testPixels = list(pixel * 4)
		solutionPixels = []
		
		for _ in range(4):
			solutionPixels.append(pixel)
		
		packed = packImage(testPixels)
		
		self.assertEqual(packed, solutionPixels)
	
	
	def test_openBinFile(self):
		"""Testing that opening the file works."""
		cleanFile = TestSteganographer.cleanPNGLocation
		fileData = openBinFile(cleanFile)
		
		self.assertEqual(fileData, open(cleanFile, 'rb').read())
		
		with self.assertRaises(SystemExit):
			fileData = openBinFile("FileThatDoesNotExist.nope")
	
	
	def test_writeBinFile(self):
		"""Testing that writing the file works as expected."""
		cleanFile = TestSteganographer.cleanPNGLocation
		dirtyFile = "tests/testImageDirty.png"
		# Removing dirty file if it is there from another test.
		if os.path.isfile(dirtyFile):
			os.remove(dirtyFile)
		
		data = hideString(openBinFile(cleanFile), "Hidden text from writeBinFile test.")
		writeBinFile(dirtyFile, data)
		
		self.assertFalse(open(cleanFile, 'rb').read() == open(dirtyFile, 'rb').read())
		
		# Asserting that the files are the same size.
		cf = open(cleanFile, 'rb')
		cf.seek(0,2)
		cleanFileSize = cf.tell()

		df = open(dirtyFile, 'rb')
		df.seek(0,2)
		dirtyFileSize = df.tell()
		
		self.assertEqual(cleanFileSize, dirtyFileSize)
	
	
	def test_steganographerHide(self):
		"""Testing that a string will correctly be hidden in a new image."""
		cleanImage = TestSteganographer.cleanPNGLocation
		dirtyImage = "tests/testImageDirty.png"
		hiddenMessage = "Hidden text from test_steganographerHide test."
		steganographerHide(cleanImage, hiddenMessage, dirtyImage)
		
		self.assertFalse(open(cleanImage, 'rb').read() == open(dirtyImage, 'rb').read())
		
		steganographerHide(cleanImage, hiddenMessage)
		self.assertTrue(os.path.isfile("tests/testImageCleanSteganogrified.png"))
	
	
	def test_steganographerReveal(self):
		"""Testing that a string is found in the dirty image."""
		cleanImage = TestSteganographer.cleanPNGLocation
		dirtyImage = "tests/testImageDirty.png"
		hiddenMessage = "Hidden text from test_steganographerReveal test."
		steganographerHide(cleanImage, hiddenMessage, dirtyImage)
		
		self.assertEqual(steganographerReveal(dirtyImage), hiddenMessage)
		
	
	def test_steganographerNullData(self):
		"""Testing that the string entered is the string returned. The data is the exact length needed."""
		testString = "This is a test String"
		testData = bytearray(testString, 'utf-8')
		blankData = bytearray(b'\x01' * len(testString) * byteLen)
		
		hiddenString = hideString(blankData, testString)
		revealedString = revealString(hiddenString)
		
		hiddenData = hideData(blankData, testData)
		revealedData = revealData(hiddenData)
		
		self.assertEqual(testString, revealedString)
		self.assertEqual(testData, revealedData)
	
	
	def test_steganographerShortData(self):
		"""Testing that when the data is too small, by a full byte, that everything that can be returned is returned."""
		testString = "This is a test String"
		testData = bytearray(testString, 'utf-8')
		blankData = bytearray(b'\x01' * (len(testString) * byteLen - byteLen))
		
		hiddenString = hideString(blankData, testString)
		revealedString = revealString(hiddenString)
		
		hiddenData = hideData(blankData, testData)
		revealedData = revealData(hiddenData)
		
		self.assertEqual(testString[:-1], revealedString)
		self.assertEqual(testData[:-1], revealedData)
	
	
	def test_steganographerShortPartialData(self):
		"""Testing that when the data is too small, by a half byte, that everything that can be returned is returned."""
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
	
	
	def test_main(self):
		"""Testing that arguments passed o the main function work as expected."""
		hiddenMessage = '"test_main hidden message"'
		result = os.system('python steganographer/steganographer.py tests/testImageClean.png -m ' + hiddenMessage + 
							' -o tests/testImageDirty.png')
		#out = sys.stdout.getvalue().strip()
		self.assertEqual(result, 0)
		#self.assertEqual(out, "The message has been hidden.")
		
		result = os.system('python steganographer/steganographer.py tests/testImageClean.png -m ' + hiddenMessage)
		self.assertEqual(result, 0)
		
		result = os.system("python steganographer/steganographer.py tests/testImageDirty.png")
		self.assertEqual(result, 0)
	
	"""
	def test_jpegs(self):
		"""Testing that jpegs can have a message hidden and revealed."""
		hiddenMessage = '"test_jpeg hidden message"'
		result = os.system('python steganographer/steganographer.py tests/testImageClean.jpg -m ' + hiddenMessage + 
							' -o tests/testImageDirty.jpg')
		self.assertEqual(result, 0)
		
		result = os.system("python steganographer/steganographer.py tests/testImageDirty.jpg")
		self.assertEqual(result, 0)
		
	
	def test_bmps(self):
		"""Testing that jpegs can have a message hidden and revealed."""
		hiddenMessage = '"test_bmps hidden message"'
		result = os.system('python steganographer/steganographer.py tests/testImageClean.bmp -m ' + hiddenMessage + 
							' -o tests/testImageDirty.bmp')
		self.assertEqual(result, 0)
		
		result = os.system("python steganographer/steganographer.py tests/testImageDirty.jpg")
		self.assertEqual(result, 0)
	"""
	
	def main(argv):
		"""Running all the tests contained."""
		print("Preparing tests...")
		runner = unittest.TextTestRunner(verbosity = 2)
		unittest.main(testRunner = runner)


if __name__ == '__main__':
	TestSteganographer.main(sys.argv)