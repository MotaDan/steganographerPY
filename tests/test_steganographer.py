"""Testing script"""
import pytest
import sys
import os
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from steganographer.steganographer import *


cleanPNGLocation = "tests/testImageClean.png"


def test_hideByte():
	"""Testing that the hideByte function does hide a byte and returns the testData with that byte hidden."""
	testData = bytearray(b'\x01' * byteLen)
	dataToHide = bytearray('A', 'utf-8')
	solutionData = bytearray(byteLen)
	solutionData[1] = 1
	solutionData[7] = 1
	
	assert hideByte(testData, dataToHide[0]) == solutionData


def test_revealByte():
	"""Testing that the revealByte function returns a bytearray of the hidden byte."""
	testData = bytearray(byteLen)
	testData[1] = 1
	testData[7] = 1
	solutionData = bytearray('A', 'utf-8')
	
	assert revealByte(testData) == solutionData


def test_hideString():
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
	
	assert hideString(testData, 'ABC') == solutionData


def test_revealString():
	"""Testing that revealString returns a string of the data that was hidden in testData."""
	testData = bytearray(byteLen * 4)
	testData[1] = 1
	testData[7] = 1
	testData[9] = 1
	testData[14] = 1
	testData[17] = 1
	testData[22] = 1
	testData[23] = 1
	
	assert revealString(testData) == 'ABC'


def test_hideData():
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
	
	assert hideData(testData, dataToHide) == solutionData


def test_hideDataPartial():
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
	assert hideData(testData[:4], dataToHide) == solutionData[:4]


def test_revealData():
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
	
	assert revealData(testData) == solutionData


def test_revealDataPartial():
	"""
	Testing that reveal data will return as much data as possible.
	
	When the testData passed in is too small for the data to be hidden.
	"""
	testData = bytearray(byteLen * 3)	#Will contain 'ABC' but will be truncated when passed to revealData
	testData[1] = 1
	testData[7] = 1
	testData[9] = 1
	testData[14] = 1
	testData[17] = 1
	testData[22] = 1
	testData[23] = 1
	solutionData = bytearray('AB@', 'utf-8')
	
	assert revealData(testData[:-byteLen // 2]) == solutionData


def test_unpackImage():
	"""Testing that unpacking returns a bytes full of all the pixels flattened."""
	pixel = 1, 2, 3, 4
	solutionPixels = bytes(list(pixel * 4))
	testPixels = []
	
	for _ in range(4):
		testPixels.append(pixel)
	
	unpacked = unpackImage(testPixels)
	
	assert unpacked == solutionPixels


def test_packImage():
	"""Testing that packing returns a list with tuples of length 4."""
	pixel = 1, 2, 3, 4
	testPixels = list(pixel * 4)
	solutionPixels = []
	
	for _ in range(4):
		solutionPixels.append(pixel)
	
	packed = packImage(testPixels)
	
	assert packed == solutionPixels


def test_openBinFile():
	"""Testing that opening the file works."""
	cleanFile = cleanPNGLocation
	fileData = openBinFile(cleanFile)
	
	assert fileData == open(cleanFile, 'rb').read()
	
	with pytest.raises(SystemExit):
		fileData = openBinFile("FileThatDoesNotExist.nope")


def test_writeBinFile():
	"""Testing that writing the file works as expected."""
	cleanFile = cleanPNGLocation
	dirtyFile = "tests/testImageDirty.png"
	# Removing dirty file if it is there from another test.
	if os.path.isfile(dirtyFile):
		os.remove(dirtyFile)
	
	data = hideString(openBinFile(cleanFile), "Hidden text from writeBinFile test.")
	writeBinFile(dirtyFile, data)
	
	assert open(cleanFile, 'rb').read() != open(dirtyFile, 'rb').read()
	
	# Asserting that the files are the same size.
	cf = open(cleanFile, 'rb')
	cf.seek(0,2)
	cleanFileSize = cf.tell()

	df = open(dirtyFile, 'rb')
	df.seek(0,2)
	dirtyFileSize = df.tell()
	
	assert cleanFileSize == dirtyFileSize


def test_steganographerHide():
	"""Testing that a string will correctly be hidden in a new image."""
	cleanImage = cleanPNGLocation
	dirtyImage = "tests/testImageDirty.png"
	hiddenMessage = "Hidden text from test_steganographerHide test."
	steganographerHide(cleanImage, hiddenMessage, dirtyImage)
	
	assert open(cleanImage, 'rb').read() != open(dirtyImage, 'rb').read()
	
	steganographerHide(cleanImage, hiddenMessage)
	assert os.path.isfile("tests/testImageCleanSteganogrified.png")


def test_steganographerReveal():
	"""Testing that a string is found in the dirty image."""
	cleanImage = cleanPNGLocation
	dirtyImage = "tests/testImageDirty.png"
	hiddenMessage = "Hidden text from test_steganographerReveal test."
	steganographerHide(cleanImage, hiddenMessage, dirtyImage)
	
	assert steganographerReveal(dirtyImage) == hiddenMessage
	

def test_steganographerNullData():
	"""Testing that the string entered is the string returned. The data is the exact length needed."""
	testString = "This is a test String"
	testData = bytearray(testString, 'utf-8')
	blankData = bytearray(b'\x01' * len(testString) * byteLen)
	
	hiddenString = hideString(blankData, testString)
	revealedString = revealString(hiddenString)
	
	hiddenData = hideData(blankData, testData)
	revealedData = revealData(hiddenData)
	
	assert testString == revealedString
	assert testData == revealedData


def test_steganographerShortData():
	"""Testing that when the data is too small, by a full byte, that everything that can be returned is returned."""
	testString = "This is a test String"
	testData = bytearray(testString, 'utf-8')
	blankData = bytearray(b'\x01' * (len(testString) * byteLen - byteLen))
	
	hiddenString = hideString(blankData, testString)
	revealedString = revealString(hiddenString)
	
	hiddenData = hideData(blankData, testData)
	revealedData = revealData(hiddenData)
	
	assert testString[:-1] == revealedString
	assert testData[:-1] == revealedData


def test_steganographerShortPartialData():
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
	
	assert solutionString == revealedString
	assert solutionData == revealedData


def test_main(capfd):
	"""Testing that arguments passed o the main function work as expected."""
	hiddenMessage = 'test_main hidden message'
	result = os.system('python -m steganographer tests/testImageClean.png -m "' + hiddenMessage + 
						'" -o tests/testImageDirty.png')
	out, _ = capfd.readouterr()
	
	assert result == 0
	assert out == "The message has been hidden.\r\n"
	
	result = os.system('python -m steganographer tests/testImageClean.png -m "' + hiddenMessage + '"')
	out, _ = capfd.readouterr()
	
	assert result == 0
	assert out == "The message has been hidden.\r\n"
	
	result = os.system("python -m steganographer tests/testImageDirty.png")
	out, _ = capfd.readouterr()
	
	assert result == 0
	assert out == ("The hidden message was...\r\n" + hiddenMessage + "\r\n")


# def test_jpegs():
	# """Testing that jpegs can have a message hidden and revealed."""
	# hiddenMessage = '"test_jpeg hidden message"'
	# result = os.system('python steganographer/steganographer.py tests/testImageClean.jpg -m ' + hiddenMessage + 
						# ' -o tests/testImageDirty.jpg')
	# assert result == 0
	
	# result = os.system("python steganographer/steganographer.py tests/testImageDirty.jpg")
	# assert result == 0
	

# def test_bmps():
	# """Testing that jpegs can have a message hidden and revealed."""
	# hiddenMessage = '"test_bmps hidden message"'
	# result = os.system('python steganographer/steganographer.py tests/testImageClean.bmp -m ' + hiddenMessage + 
						# ' -o tests/testImageDirty.bmp')
	# assert result == 0
	
	# result = os.system("python steganographer/steganographer.py tests/testImageDirty.jpg")
	# assert result == 0
