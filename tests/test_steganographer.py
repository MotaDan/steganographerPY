"""Testing script"""
import pytest
from PIL import ImageChops
import sys
import os
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from steganographer.steganographer import *
from hypothesis import given
from hypothesis.strategies import text, binary, characters


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

@given(dataToHide=binary(min_size=1, max_size=1))
def test_hideRevealByteInverse(dataToHide):
	"""Testing that anything hidden by hideByte is revealed by revealByte."""
	cleanData = bytes(b'\x01' * 8)
	
	revealedByte = revealByte(hideByte(cleanData, dataToHide[0]))
	assert revealedByte == dataToHide
	
	
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


@given(stringToHide=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_hideRevealStringInverse(stringToHide):
	"""Testing that anything hidden by hideString is revealed by revealString."""
	cleanData = bytes(b'\x01' * 5000)
	
	revealedString = revealString(hideString(cleanData, stringToHide))
	assert revealedString == stringToHide
	
	
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


@pytest.mark.xfail(strict=True, reason="Issue #50 need to change how data is hidden and revealed.", run=True)
@given(stringToHide=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_hideRevealDataInverse(stringToHide):
	"""Testing that anything hidden by hideData is revealed by revealData."""
	cleanData = bytes(b'\x01' * 5000)
	dataToHide = bytes(stringToHide, 'utf-8')
	
	revealedData = revealData(hideData(cleanData, dataToHide))
	assert revealedData == dataToHide
	
	
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


def test_unpackPackInverse():
	"""Testing that pixels unpacked by unpackImage are correctly packed by packImage."""
	pixel = 1, 2, 3, 4
	testPixels = []
	
	for _ in range(4):
		testPixels.append(pixel)
	
	assert packImage(unpackImage(testPixels)) == testPixels
	
	
def test_openBinFile():
	"""Testing that opening the file works."""
	cleanFile = cleanPNGLocation
	fileData = openBinFile(cleanFile)
	
	assert fileData == open(cleanFile, 'rb').read()
	
	with pytest.raises(SystemExit):
		fileData = openBinFile("OpenBinFileThatDoesNotExist.nope")


def test_writeBinFileDiffContent():
	"""Testing that the file written is different from the one read, after hiding a message."""
	cleanFile = cleanPNGLocation
	dirtyFile = "tests/dirtyImage.png"
	# Removing dirty file if it is there from another test.
	if os.path.isfile(dirtyFile):
		os.remove(dirtyFile)
	
	data = hideString(openBinFile(cleanFile), "Hidden text from test_writeBinFileDiffContent.")
	writeBinFile(dirtyFile, data)
	
	assert open(cleanFile, 'rb').read() != open(dirtyFile, 'rb').read()
	
	
def test_writeBinFileSizeSame():
	"""Testing that the file written is the same size as the one read, after hiding a message."""
	cleanFile = cleanPNGLocation
	dirtyFile = "tests/dirtyImage.png"
	# Removing dirty file if it is there from another test.
	if os.path.isfile(dirtyFile):
		os.remove(dirtyFile)
	
	data = hideString(openBinFile(cleanFile), "Hidden text from test_writeBinFileSizeSame.")
	writeBinFile(dirtyFile, data)
	
	# Getting the file sizes for the clean and dirty files.
	cf = open(cleanFile, 'rb')
	cf.seek(0,2)
	cleanFileSize = cf.tell()

	df = open(dirtyFile, 'rb')
	df.seek(0,2)
	dirtyFileSize = df.tell()
	
	assert cleanFileSize == dirtyFileSize


def test_openImageFile():
	"""Testing that opening an image file returns the data in the file."""
	cleanFile = cleanPNGLocation
	imageData = openImageFile(cleanFile)
	
	im = Image.open(cleanFile)
	pixels = im.getdata()
	
	assert imageData == unpackImage(pixels)
	
	with pytest.raises(SystemExit):
		openImageFile("OpenImageFileThatDoesNotExist.nope")
	

def test_writeImageFileValidImage():
	"""Testing that the image created is not corrupt."""
	cleanFile = cleanPNGLocation
	dirtyFile = "tests/dirtyImage.png"
	# Removing dirty file if it is there from another test.
	if os.path.isfile(dirtyFile):
		os.remove(dirtyFile)
	
	dirtyData = hideString(openImageFile(cleanFile), "Hidden text from test_writeImageFileValidImage.")
	writeImageFile(dirtyFile, cleanFile, dirtyData)
	
	try:
		Image.open(dirtyFile)
	except OSError:
		pytest.fail("Image is corrupt " + dirtyFile)
		
		
def test_writeImageFileDiffContent():
	"""Testing that writing out an image creates a different image at the bit level."""
	cleanFile = cleanPNGLocation
	dirtyFile = "tests/dirtyImage.png"
	# Removing dirty file if it is there from another test.
	if os.path.isfile(dirtyFile):
		os.remove(dirtyFile)
	
	dirtyData = hideString(openImageFile(cleanFile), "Hidden text from test_writeImageFileDiffContent.")
	writeImageFile(dirtyFile, cleanFile, dirtyData)
	
	assert open(cleanFile, 'rb').read() != open(dirtyFile, 'rb').read()
	
	
def test_writeImageFileSameImage():
	"""Testing that writing out an image creates the same image when viewed generally."""
	cleanFile = cleanPNGLocation
	dirtyFile = "tests/dirtyImage.png"
	# Removing dirty file if it is there from another test.
	if os.path.isfile(dirtyFile):
		os.remove(dirtyFile)
	
	dirtyData = hideString(openImageFile(cleanFile), "Hidden text from test_writeImageFileSameImage.")
	writeImageFile(dirtyFile, cleanFile, dirtyData)
	
	assert compare_images(cleanFile, dirtyFile) < 500
	
	
def test_writeImageFileDiffSize():
	"""Testing that writing out an image creates a file of a different size, if the file was not generated by PIL."""
	cleanFile = cleanPNGLocation
	dirtyFile = "tests/dirtyImage.png"
	# Removing dirty file if it is there from another test.
	if os.path.isfile(dirtyFile):
		os.remove(dirtyFile)
	
	dirtyData = hideString(openImageFile(cleanFile), "Hidden text from test_writeImageFileDiffSize.")
	writeImageFile(dirtyFile, cleanFile, dirtyData)
	
	# Getting the file sizes for the clean and dirty files.
	cf = open(cleanFile, 'rb')
	cf.seek(0,2)
	cleanFileSize = cf.tell()

	df = open(dirtyFile, 'rb')
	df.seek(0,2)
	dirtyFileSize = df.tell()
	
	assert cleanFileSize != dirtyFileSize
	
	
def test_writeImageFileDiffSizePIL():
	"""Testing that writing out an image creates a file of a different size, if the file was generated by PIL."""
	cleanFile = cleanPNGLocation
	dirtyFile = "tests/dirtyImage.png"
	PILImage = Image.open(cleanFile)
	cleanFilePIL = "tests/cleanImagePIL.png"
	PILImage.save(cleanFilePIL)
	# Removing dirty file if it is there from another test.
	if os.path.isfile(dirtyFile):
		os.remove(dirtyFile)
	
	dirtyData = hideString(openImageFile(cleanFilePIL), "Hidden text from test_writeImageFileSameImage.")
	writeImageFile(dirtyFile, cleanFilePIL, dirtyData)
	
	# Getting the file sizes for the clean and dirty files.
	cf = open(cleanFilePIL, 'rb')
	cf.seek(0,2)
	cleanFileSize = cf.tell()

	df = open(dirtyFile, 'rb')
	df.seek(0,2)
	dirtyFileSize = df.tell()
	
	assert cleanFileSize != dirtyFileSize
	
	
def test_writeImageFileExitOnFail():
	"""Testing that when failing to write an image there is a system exit."""
	cleanFile = cleanPNGLocation
	dirtyFile = "WriteImageFileThatDoesNotExist.nope"
	dirtyData = bytes(8)
	
	with pytest.raises(SystemExit):
		writeImageFile(cleanFile, dirtyFile, dirtyData)


def test_steganographerHideString():
	"""Testing that a string will correctly be hidden in a new image."""
	cleanImage = cleanPNGLocation
	dirtyImage = "tests/dirtyImage.png"
	hiddenMessage = "Hidden text from test_steganographerHideString."
	
	hiddenFname = steganographerHide(cleanImage, hiddenMessage, dirtyImage)
	
	assert open(cleanImage, 'rb').read() != open(hiddenFname, 'rb').read()
	assert compare_images(cleanImage, hiddenFname) < 500
	try:
		Image.open(hiddenFname)
	except OSError:
		pytest.fail("Image is corrupt " + hiddenFname)
	
	
def test_steganographerHideStringCorrectName():
	"""Testing that the image a string is hidden in is the correct one."""
	cleanImage = cleanPNGLocation
	dirtyImage = "tests/dirtyImage.png"
	hiddenMessage = "Hidden text from test_steganographerHide."
	
	hiddenFname = steganographerHide(cleanImage, hiddenMessage, dirtyImage)
	
	assert hiddenFname == dirtyImage
	
	
def test_steganographerHideStringSteganogrified():
	"""Testing that a string will correctly be hidden in a new image, that no name was provided for."""
	cleanImage = cleanPNGLocation
	hiddenMessage = "Hidden text from test_steganographerHideStringSteganogrified."
	
	hiddenFname = steganographerHide(cleanImage, hiddenMessage)
	
	assert open(cleanImage, 'rb').read() != open(hiddenFname, 'rb').read()
	assert compare_images(cleanImage, hiddenFname) < 500
	try:
		Image.open(hiddenFname)
	except OSError:
		pytest.fail("Image is corrupt " + hiddenFname)

	
def test_steganographerHideStringSteganogrifiedCorrectName():
	"""Testing that the image a string is hidden in is the correct one."""
	cleanImage = cleanPNGLocation
	hiddenMessage = "Hidden text from test_steganographerHideStringSteganogrified."
	
	hiddenFname = steganographerHide(cleanImage, hiddenMessage)
	steganogrifiedFname = cleanPNGLocation[:-4] + "Steganogrified.png"
	
	assert hiddenFname == steganogrifiedFname
	assert os.path.isfile(steganogrifiedFname)
	

@given(hiddenMessage=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_steganographerHideSteganographerRevealInverse(hiddenMessage):
	"""Testing that steganographerReveal reveals what was hidden by steganographerHide."""
	cleanImage = cleanPNGLocation
	dirtyImage = "tests/dirtyImage.png"
	
	revealedMessage = steganographerReveal(steganographerHide(cleanImage, hiddenMessage, dirtyImage))
	assert revealedMessage == hiddenMessage
	

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


def test_mainHideMsgWithOutput(capfd):
	"""Testing that main works when given input, message, and output."""
	lineEnd = '\n'
	if sys.platform == 'win32':
		lineEnd = '\r\n'
	hiddenMessage = 'test_mainHideMsgWithOutput hidden message'
	dirtyFname = "tests/dirtyImage.png"
	
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
	
	
def test_mainHideMsgNoOutput(capfd):
	"""Testing that main works when given input, message, and no output."""
	lineEnd = '\n'
	if sys.platform == 'win32':
		lineEnd = '\r\n'
	hiddenMessage = 'test_mainHideMsgNoOutput hidden message'
	steganogrifiedFname = cleanPNGLocation[:-4] + "Steganogrified.png"
	
	result = os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hiddenMessage + '"')
	out, _ = capfd.readouterr()
	
	assert result == 0
	assert out == "The message has been hidden in " + steganogrifiedFname + lineEnd
	assert compare_images(cleanPNGLocation, steganogrifiedFname) < 500
	try:
		Image.open(steganogrifiedFname)
	except OSError:
		pytest.fail("Image is corrupt " + steganogrifiedFname)
	
	
def test_mainRevealMsgNoOutput(capfd):
	"""Testing that main works when given input, message, and no output."""
	lineEnd = '\n'
	if sys.platform == 'win32':
		lineEnd = '\r\n'
	hiddenMessage = 'test_mainRevealMsgNoOutput hidden message'
	dirtyFname = "tests/dirtyImage.png"
	
	result = os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hiddenMessage + 
						'" -o ' + dirtyFname)
	_, _ = capfd.readouterr()
	
	result = os.system("python -m steganographer " + dirtyFname)
	out, _ = capfd.readouterr()
	
	assert result == 0
	assert out == ("The hidden message was..." + lineEnd + hiddenMessage + lineEnd)
	
	
def test_mainRevealMsgNoOutputUnicode(capfd):
	"""Testing that main works when given input, message, and no output."""
	lineEnd = '\n'
	if sys.platform == 'win32':
		lineEnd = '\r\n'
	hiddenMessage = 'test_mainRevealMsgNoOutputUnicode hidden message, Unicode characters: 𓁈 ᾨ ԅ Թ ػ ޗ ߚ ङ ლ ጩ Ꮬ'
	dirtyFname = "tests/dirtyImage.png"
	outputFname = "tests/dirtyImageMessage.txt"
	
	result = os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hiddenMessage + 
						'" -o ' + dirtyFname)
	_, _ = capfd.readouterr()
	
	result = os.system("python -m steganographer " + dirtyFname)
	out, _ = capfd.readouterr()
	
	assert result == 0
	assert open(outputFname, 'r', encoding='utf-8').read() == hiddenMessage
	if sys.platform == 'win32':
		assert out == ("The hidden message contains unsupported unicode characters and cannot be fully displayed " + 
						"here. The correct message has been written to " + outputFname + lineEnd + 
						str(hiddenMessage.encode('utf-8')) + lineEnd)
	else:
		assert out == ("The hidden message was..." + lineEnd + hiddenMessage + lineEnd)
	
	
def test_mainRevealMsgWithOutput(capfd):
	"""Testing that main works when given input, message, and no output."""
	lineEnd = '\n'
	if sys.platform == 'win32':
		lineEnd = '\r\n'
	hiddenMessage = 'test_mainRevealMsgWithOutput hidden message'
	dirtyFname = "tests/dirtyImage.png"
	outputFname = "tests/outputMessage.txt"
	
	result = os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hiddenMessage + 
						'" -o ' + dirtyFname)
	_, _ = capfd.readouterr()
	
	result = os.system("python -m steganographer " + dirtyFname + " -o " + outputFname)
	out, _ = capfd.readouterr()
	
	assert result == 0
	assert open(outputFname, 'r').read() == hiddenMessage
	assert out == ("The hidden message was written to " + outputFname + lineEnd)

	
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
