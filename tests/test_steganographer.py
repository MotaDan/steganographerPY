# Testing class
import unittest
import time
import sys
import os
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from steganographer.steganographer import *

class TestSteganographer(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()
	
	
	def tearDown(self):
		t = time.time() - self.startTime
		
		if os.path.isfile("tests/testImageDirty.png"):
			os.remove("tests/testImageDirty.png")
		
		if os.path.isfile("tests/testImageCleanSteganogrified.png"):
			os.remove("tests/testImageCleanSteganogrified.png")
			
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
		testData = bytearray(byteLen)
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
		testData = bytearray(byteLen * 4)
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
		solutionData = bytearray(byteLen * 3) + bytearray(b'\x01' * byteLen)
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
	
	
	# Testing that reveal data will return as much data as possible when the testData passed in is too small for the data to be hidden.
	def test_revealDataPartial(self):
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
	
	
	# Testing that unpacking returns a bytes full of all the pixels flattened.
	def test_unpackImage(self):
		pixel = 1, 2, 3, 4
		solutionPixels = bytes(list(pixel * 4))
		testPixels = []
		
		for i in range(4):
			testPixels.append(pixel)
		
		unpacked = unpackImage(testPixels)
		
		self.assertEqual(unpacked, solutionPixels)
	
	
	# Testing that packing returns a list with tuples of length 4.
	def test_packImage(self):
		pixel = 1, 2, 3, 4
		testPixels = list(pixel * 4)
		solutionPixels = []
		
		for i in range(4):
			solutionPixels.append(pixel)
		
		packed = packImage(testPixels)
		
		self.assertEqual(packed, solutionPixels)
	
	
	# Testing that opening the file works.
	def test_openBinFile(self):
		cleanFile = "tests/testImageClean.png"
		fileData = openBinFile(cleanFile)
		
		self.assertEqual(fileData, open(cleanFile, 'rb').read())
	
	
	# Testing that writing the file works as expected.
	def test_writeBinFile(self):
		cleanFile = "tests/testImageClean.png"
		dirtyFile = "tests/testImageDirty.png"
		data = hideString(openBinFile(cleanFile), "Hidden text from writeBinFile test.")
		writeBinFile(dirtyFile, data)
		
		cf = open(cleanFile, 'rb')
		cf.seek(0,2)

		df = open(dirtyFile, 'rb')
		df.seek(0,2)
		
		self.assertFalse(open(cleanFile, 'rb').read() == open(dirtyFile, 'rb').read())
		# Asserting that the files are the same size.
		self.assertEqual(cf.tell(), df.tell())
	
	
	# Testing that a string will correctly be hidden in a new image.
	def test_steganographerHide(self):
		cleanImage = "tests/testImageClean.png"
		dirtyImage = "tests/testImageDirty.png"
		steganographerHide(cleanImage, "Text that should be hidden.", dirtyImage)
		
		self.assertFalse(open(cleanImage, 'rb').read() == open(dirtyImage, 'rb').read())
		
		steganographerHide(cleanImage, "Text that should be hidden.")
		self.assertTrue(os.path.isfile("tests/testImageCleanSteganogrified.png"))
	
	
	# Testing that a string is found in the dirty image.
	def test_steganographerReveal(self):
		cleanImage = "tests/testImageClean.png"
		dirtyImage = "tests/testImageDirty.png"
		hiddenMessage = "Text that should be hidden."
		steganographerHide(cleanImage, hiddenMessage, dirtyImage)
		
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
	
	
	# Testing that arguments passed o the main function work as expected.
	def test_main(self):
		hiddenMessage = '"test_main hidden message"'
		result = os.system('python steganographer/steganographer.py tests/testImageClean.png -m ' + hiddenMessage + ' -o tests/testImageDirty.png')
		#out = sys.stdout.getvalue().strip()
		self.assertEqual(result, 0)
		#self.assertEqual(out, "The message has been hidden.")
		
		result = os.system('python steganographer/steganographer.py tests/testImageClean.png -m ' + hiddenMessage)
		self.assertEqual(result, 0)
		
		result = os.system("python steganographer/steganographer.py tests/testImageDirty.png")
		self.assertEqual(result, 0)
	
	
	def main():
		print("Preparing tests...")
		runner = unittest.TextTestRunner(verbosity = 2)
		unittest.main(testRunner = runner)

if __name__ == '__main__':
	main()