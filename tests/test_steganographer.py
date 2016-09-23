"""Testing script"""
import pytest
from PIL import ImageChops
import sys
import os
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from steganographer.steganographer import *


cleanPNGLocation = "tests/cleanImage.png"


def test_hideByte():
	"""Testing that the hideByte function does hide a byte and returns the testData with that byte hidden."""
	testData = bytes(b'\x01' * byteLen)
	dataToHide = bytes('A', 'utf-8')
	solutionData = bytearray(byteLen)
	solutionData[1] = 1
	solutionData[7] = 1
	
	assert hideByte(testData, dataToHide[0]) == solutionData


def test_revealByte():
	"""Testing that the revealByte function returns a bytes of the hidden byte."""
	testData = bytearray(byteLen)
	testData[1] = 1
	testData[7] = 1
	solutionData = bytes('A', 'utf-8')
	
	assert revealByte(testData) == solutionData


def test_hideString():
	"""Testing that hideString takes in a string and bytes and hides the string in that bytes."""
	testData = bytes(b'\x01' * byteLen * 3)
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
	"""Testing that hideData will hide one bytes inside another."""
	testData = bytes(b'\x01' * byteLen * 4)
	dataToHide = bytes('ABC', 'utf-8')
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
	"""Testing that hideData will work when given a testData bytes that is too short to hold the data"""
	testData = bytes(b'\x01' * byteLen * 3)
	dataToHide = bytes('ABC', 'utf-8')
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
	solutionData = bytes('ABC', 'utf-8')
	
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
	solutionData = bytes('AB@', 'utf-8')
	
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
		fileData = openBinFile("OpenBinFileThatDoesNotExist.nope")


def test_writeBinFile():
	"""Testing that writing the file works as expected."""
	cleanFile = cleanPNGLocation
	dirtyFile = "tests/dirtyImage.png"
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


def test_openImageFile():
	"""Testing that opening an image file works."""
	cleanFile = cleanPNGLocation
	imageData = openImageFile(cleanFile)
	
	im = Image.open(cleanFile)
	pixels = im.getdata()
	
	assert imageData == unpackImage(pixels)
	
	with pytest.raises(SystemExit):
		openImageFile("OpenImageFileThatDoesNotExist.nope")
	

def test_writeImageFile():
	"""Testing that writing out an image works. File sizes will be different if the input was not created by PIL."""
	cleanFile = cleanPNGLocation
	dirtyFile = "tests/dirtyImage.png"
	# Removing dirty file if it is there from another test.
	if os.path.isfile(dirtyFile):
		os.remove(dirtyFile)
	
	dirtyData = hideString(openImageFile(cleanFile), "Hidden text from writeBinFile test.")
	writeImageFile(dirtyFile, cleanFile, dirtyData)
	
	assert open(cleanFile, 'rb').read() != open(dirtyFile, 'rb').read()
	assert compare_images(cleanFile, dirtyFile) < 500
	
	with pytest.raises(SystemExit):
		writeImageFile(cleanFile, "WriteImageFileThatDoesNotExist.nope", dirtyData)


def test_steganographerHide():
	"""Testing that a string will correctly be hidden in a new image."""
	cleanImage = cleanPNGLocation
	dirtyImage = "tests/dirtyImage.png"
	hiddenMessage = "Hidden text from test_steganographerHide test."
	hiddenFname = ''
	
	hiddenFname = steganographerHide(cleanImage, hiddenMessage, dirtyImage)
	assert open(cleanImage, 'rb').read() != open(dirtyImage, 'rb').read()
	assert os.path.isfile(dirtyImage)
	assert hiddenFname == dirtyImage
	assert compare_images(cleanImage, dirtyImage) < 500
	try:
		Image.open(dirtyImage)
	except OSError:
		pytest.fail("Image is corrupt " + dirtyImage)
	
	hiddenFname = steganographerHide(cleanImage, hiddenMessage)
	steganogrifiedFname = "tests/cleanImageSteganogrified.png"
	assert open(cleanImage, 'rb').read() != open(dirtyImage, 'rb').read()
	assert os.path.isfile(steganogrifiedFname)
	assert hiddenFname == steganogrifiedFname
	assert compare_images(cleanImage, steganogrifiedFname) < 500
	try:
		Image.open(steganogrifiedFname)
	except OSError:
		pytest.fail("Image is corrupt " + steganogrifiedFname)


def test_steganographerReveal():
	"""Testing that a string is found in the dirty image."""
	cleanImage = cleanPNGLocation
	dirtyImage = "tests/dirtyImage.png"
	hiddenMessage = "Hidden text from test_steganographerReveal test."
	steganographerHide(cleanImage, hiddenMessage, dirtyImage)
	
	assert steganographerReveal(dirtyImage) == hiddenMessage
	

def test_steganographerNullData():
	"""Testing that the string entered is the string returned. The data is the exact length needed."""
	testString = "This is a test String"
	testData = bytes(testString, 'utf-8')
	blankData = bytes(b'\x01' * len(testString) * byteLen)
	
	hiddenString = hideString(blankData, testString)
	revealedString = revealString(hiddenString)
	
	hiddenData = hideData(blankData, testData)
	revealedData = revealData(hiddenData)
	
	assert testString == revealedString
	assert testData == revealedData


def test_steganographerShortData():
	"""Testing that when the data is too small, by a full byte, that everything that can be returned is returned."""
	testString = "This is a test String"
	testData = bytes(testString, 'utf-8')
	blankData = bytes(b'\x01' * (len(testString) * byteLen - byteLen))
	
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
	testData = bytes(testString, 'utf-8')
	solutionData = bytearray(testData)
	solutionData[-1] = solutionData[-1] >> byteLen // 2 << byteLen // 2
	blankData = bytes(b'\x01' * (len(testString) * byteLen - byteLen // 2))
	
	hiddenString = hideString(blankData, testString)
	revealedString = revealString(hiddenString)
	
	hiddenData = hideData(blankData, testData)
	revealedData = revealData(hiddenData)
	
	assert solutionString == revealedString
	assert solutionData == revealedData


def compare_images(img1, img2):
	"""Expects strings of the locations of two images. Will return an integer representing their difference"""
	img1 = Image.open(img1)
	img2 = Image.open(img2)

	# calculate the difference and its norms
	diff = ImageChops.difference(img1, img2)
	m_norm = sum(unpackImage(diff.getdata()))  # Manhattan norm
	
	return m_norm


def normalize(arr):
	"""Normalizes a list of pixels."""
	rng = arr.max()-arr.min()
	amin = arr.min()
	
	return (arr-amin)*255/rng


def test_main(capfd):
	"""Testing that arguments passed to the main function work as expected."""
	lineEnd = '\n'
	if sys.platform == 'win32':
		lineEnd = '\r\n'
	hiddenMessage = 'test_main hidden message'
	dirtyFname = "tests/dirtyImage.png"
	steganogrifiedFname = "tests/cleanImageSteganogrified.png"
	
	result = os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hiddenMessage + 
						'" -o ' + dirtyFname)
	out, _ = capfd.readouterr()
	
	assert result == 0
	assert out == "The message has been hidden in " + dirtyFname + lineEnd
	assert compare_images(cleanPNGLocation, dirtyFname) < 500
	try:
		Image.open(dirtyFname)
	except OSError:
		pytest.fail("Image is corrupt " + dirtyFname)
	
	result = os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hiddenMessage + '"')
	out, _ = capfd.readouterr()
	
	assert result == 0
	assert out == "The message has been hidden in " + steganogrifiedFname + lineEnd
	assert compare_images(cleanPNGLocation, steganogrifiedFname) < 500
	try:
		Image.open(steganogrifiedFname)
	except OSError:
		pytest.fail("Image is corrupt " + steganogrifiedFname)
	
	result = os.system("python -m steganographer tests/dirtyImage.png")
	out, _ = capfd.readouterr()
	
	assert result == 0
	assert out == ("The hidden message was..." + lineEnd + hiddenMessage + lineEnd)

	
@pytest.mark.xfail(strict=True, reason="Issue #28 jpeg support not added.", run=False)
def test_jpegs():
	"""Testing that jpegs can have a message hidden and revealed."""
	hiddenMessage = '"test_jpeg hidden message"'
	result = os.system('python -m steganographer tests/cleanImage.jpg -m ' + hiddenMessage + 
						' -o tests/dirtyImage.jpg')
	
	assert result == 0
	assert compare_images("tests/cleanImage.jpg", "tests/dirtyImage.jpg") < 500
	
	result = os.system("python -m steganographer tests/dirtyImage.jpg")
	assert result == 0
	

@pytest.mark.xfail(strict=True, reason="Issue #30 bmp support not added.", run=False)
def test_bmps():
	"""Testing that jpegs can have a message hidden and revealed."""
	hiddenMessage = '"test_bmps hidden message"'
	result = os.system('python -m steganographer tests/cleanImage.bmp -m ' + hiddenMessage + 
						' -o tests/dirtyImage.bmp')
						
	assert result == 0
	assert compare_images("tests/cleanImage.bmp", "tests/dirtyImage.bmp") < 500
	
	result = os.system("python -m steganographer tests/dirtyImage.bmp")
	assert result == 0
	
	
def test_unicode():
	"""Testing that unicode characters are hidden and revealed."""
	message = "test_unicode hidden message. Some random unicode characters: 𓁈 ᾨ ԅ Թ ػ ޗ ߚ ङ ლ ጩ Ꮬ"
	
	assert message == steganographerReveal(steganographerHide(cleanPNGLocation, message, "tests/dirtyImage.png"))
