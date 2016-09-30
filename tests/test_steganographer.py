"""Testing script"""
import pytest
from PIL import ImageChops
import sys
import os
import os.path
from hypothesis import given
from hypothesis.strategies import text, binary, characters

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from steganographer.steganographer import *

cleanPNGLocation = "tests/cleanImage.png"


def test_hide_byte():
    """Testing that the hide_byte function does hide a byte and returns the testData with that byte hidden."""
    testData = bytes(b'\x01' * byteLen)
    dataToHide = bytes('A', 'utf-8')
    solutionData = bytearray(byteLen)
    solutionData[1] = 1
    solutionData[7] = 1

    assert hide_byte(testData, dataToHide[0]) == solutionData


def test_reveal_byte():
    """Testing that the reveal_byte function returns a bytes of the hidden byte."""
    testData = bytearray(byteLen)
    testData[1] = 1
    testData[7] = 1
    solutionData = bytes('A', 'utf-8')

    assert reveal_byte(testData) == solutionData


@given(dataToHide=binary(min_size=1, max_size=1))
def test_hide_reveal_byte_inverse(dataToHide):
    """Testing that anything hidden by hide_byte is revealed by reveal_byte."""
    cleanData = bytes(b'\x01' * 8)

    revealedByte = reveal_byte(hide_byte(cleanData, dataToHide[0]))
    assert revealedByte == dataToHide


def test_hide_string():
    """Testing that hide_string takes in a string and bytes and hides the string in that bytes."""
    testData = bytes(b'\x01' * byteLen * 3)
    solutionData = bytearray(byteLen * 3)
    solutionData[1] = 1
    solutionData[7] = 1
    solutionData[9] = 1
    solutionData[14] = 1
    solutionData[17] = 1
    solutionData[22] = 1
    solutionData[23] = 1

    assert hide_string(testData, 'ABC') == solutionData


def test_reveal_string():
    """Testing that reveal_string returns a string of the data that was hidden in testData."""
    testData = bytearray(byteLen * 4)
    testData[1] = 1
    testData[7] = 1
    testData[9] = 1
    testData[14] = 1
    testData[17] = 1
    testData[22] = 1
    testData[23] = 1

    assert reveal_string(testData) == 'ABC'


@given(stringToHide=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_hide_reveal_string_inverse(stringToHide):
    """Testing that anything hidden by hide_string is revealed by reveal_string."""
    cleanData = bytes(b'\x01' * 5000)

    revealedString = reveal_string(hide_string(cleanData, stringToHide))
    assert revealedString == stringToHide


def test_hide_data():
    """Testing that hide_data will hide one bytes inside another."""
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

    assert hide_data(testData, dataToHide) == solutionData


def test_hide_data_partial():
    """Testing that hide_data will work when given a testData bytes that is too short to hold the data"""
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
    assert hide_data(testData[:4], dataToHide) == solutionData[:4]


def test_reveal_data():
    """Testing that reveal_data will return the correct data that is hidden inside the testData."""
    testData = bytearray(byteLen * 3)
    testData[1] = 1
    testData[7] = 1
    testData[9] = 1
    testData[14] = 1
    testData[17] = 1
    testData[22] = 1
    testData[23] = 1
    solutionData = bytes('ABC', 'utf-8')

    assert reveal_data(testData) == solutionData


def test_reveal_data_partial():
    """
    Testing that reveal data will return as much data as possible.

    When the testData passed in is too small for the data to be hidden.
    """
    testData = bytearray(byteLen * 3)  # Will contain 'ABC' but will be truncated when passed to reveal_data
    testData[1] = 1
    testData[7] = 1
    testData[9] = 1
    testData[14] = 1
    testData[17] = 1
    testData[22] = 1
    testData[23] = 1
    solutionData = bytes('AB@', 'utf-8')

    assert reveal_data(testData[:-byteLen // 2]) == solutionData


@pytest.mark.xfail(strict=True, reason="Issue #50 need to change how data is hidden and revealed.", run=True)
@given(stringToHide=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_hide_reveal_data_inverse(stringToHide):
    """Testing that anything hidden by hide_data is revealed by reveal_data."""
    cleanData = bytes(b'\x01' * 5000)
    dataToHide = bytes(stringToHide, 'utf-8')

    revealedData = reveal_data(hide_data(cleanData, dataToHide))
    assert revealedData == dataToHide


def test_unpack_image():
    """Testing that unpacking returns a bytes full of all the pixels flattened."""
    pixel = 1, 2, 3, 4
    solutionPixels = bytes(list(pixel * 4))
    testPixels = []

    for _ in range(4):
        testPixels.append(pixel)

    unpacked = unpack_image(testPixels)

    assert unpacked == solutionPixels


def test_pack_image():
    """Testing that packing returns a list with tuples of length 4."""
    pixel = 1, 2, 3, 4
    testPixels = list(pixel * 4)
    solutionPixels = []

    for _ in range(4):
        solutionPixels.append(pixel)

    packed = pack_image(testPixels)

    assert packed == solutionPixels


def test_unpack_pack_inverse():
    """Testing that pixels unpacked by unpack_image are correctly packed by pack_image."""
    pixel = 1, 2, 3, 4
    testPixels = []

    for _ in range(4):
        testPixels.append(pixel)

    assert pack_image(unpack_image(testPixels)) == testPixels


def test_open_bin_file():
    """Testing that opening the file works."""
    cleanFile = cleanPNGLocation
    fileData = open_bin_file(cleanFile)

    assert fileData == open(cleanFile, 'rb').read()

    with pytest.raises(SystemExit):
        fileData = open_bin_file("OpenBinFileThatDoesNotExist.nope")


def test_write_bin_file_diff_content():
    """Testing that the file written is different from the one read, after hiding a message."""
    cleanFile = cleanPNGLocation
    dirtyFile = "tests/dirtyImage.png"
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirtyFile):
        os.remove(dirtyFile)

    data = hide_string(open_bin_file(cleanFile), "Hidden text from test_writeBinFileDiffContent.")
    write_bin_file(dirtyFile, data)

    assert open(cleanFile, 'rb').read() != open(dirtyFile, 'rb').read()


def test_write_bin_file_size_same():
    """Testing that the file written is the same size as the one read, after hiding a message."""
    cleanFile = cleanPNGLocation
    dirtyFile = "tests/dirtyImage.png"
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirtyFile):
        os.remove(dirtyFile)

    data = hide_string(open_bin_file(cleanFile), "Hidden text from test_writeBinFileSizeSame.")
    write_bin_file(dirtyFile, data)

    # Getting the file sizes for the clean and dirty files.
    cf = open(cleanFile, 'rb')
    cf.seek(0, 2)
    cleanFileSize = cf.tell()

    df = open(dirtyFile, 'rb')
    df.seek(0, 2)
    dirtyFileSize = df.tell()

    assert cleanFileSize == dirtyFileSize


def test_open_image_file():
    """Testing that opening an image file returns the data in the file."""
    cleanFile = cleanPNGLocation
    imageData = open_image_file(cleanFile)

    im = Image.open(cleanFile)
    pixels = im.getdata()

    assert imageData == unpack_image(pixels)

    with pytest.raises(SystemExit):
        open_image_file("OpenImageFileThatDoesNotExist.nope")


def test_write_image_file_valid_image():
    """Testing that the image created is not corrupt."""
    cleanFile = cleanPNGLocation
    dirtyFile = "tests/dirtyImage.png"
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirtyFile):
        os.remove(dirtyFile)

    dirtyData = hide_string(open_image_file(cleanFile), "Hidden text from test_writeImageFileValidImage.")
    write_image_file(dirtyFile, cleanFile, dirtyData)

    try:
        Image.open(dirtyFile)
    except OSError:
        pytest.fail("Image is corrupt " + dirtyFile)


def test_write_image_file_diff_content():
    """Testing that writing out an image creates a different image at the bit level."""
    cleanFile = cleanPNGLocation
    dirtyFile = "tests/dirtyImage.png"
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirtyFile):
        os.remove(dirtyFile)

    dirtyData = hide_string(open_image_file(cleanFile), "Hidden text from test_writeImageFileDiffContent.")
    write_image_file(dirtyFile, cleanFile, dirtyData)

    assert open(cleanFile, 'rb').read() != open(dirtyFile, 'rb').read()


def test_write_image_file_same_image():
    """Testing that writing out an image creates the same image when viewed generally."""
    cleanFile = cleanPNGLocation
    dirtyFile = "tests/dirtyImage.png"
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirtyFile):
        os.remove(dirtyFile)

    dirtyData = hide_string(open_image_file(cleanFile), "Hidden text from test_writeImageFileSameImage.")
    write_image_file(dirtyFile, cleanFile, dirtyData)

    assert compare_images(cleanFile, dirtyFile) < 500


def test_write_image_file_diff_size():
    """Testing that writing out an image creates a file of a different size, if the file was not generated by PIL."""
    cleanFile = cleanPNGLocation
    dirtyFile = "tests/dirtyImage.png"
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirtyFile):
        os.remove(dirtyFile)

    dirtyData = hide_string(open_image_file(cleanFile), "Hidden text from test_writeImageFileDiffSize.")
    write_image_file(dirtyFile, cleanFile, dirtyData)

    # Getting the file sizes for the clean and dirty files.
    cf = open(cleanFile, 'rb')
    cf.seek(0, 2)
    cleanFileSize = cf.tell()

    df = open(dirtyFile, 'rb')
    df.seek(0, 2)
    dirtyFileSize = df.tell()

    assert cleanFileSize != dirtyFileSize


def test_write_image_file_diff_size_pil():
    """Testing that writing out an image creates a file of a different size, if the file was generated by PIL."""
    cleanFile = cleanPNGLocation
    dirtyFile = "tests/dirtyImage.png"
    PILImage = Image.open(cleanFile)
    cleanFilePIL = "tests/cleanImagePIL.png"
    PILImage.save(cleanFilePIL)
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirtyFile):
        os.remove(dirtyFile)

    dirtyData = hide_string(open_image_file(cleanFilePIL), "Hidden text from test_writeImageFileSameImage.")
    write_image_file(dirtyFile, cleanFilePIL, dirtyData)

    # Getting the file sizes for the clean and dirty files.
    cf = open(cleanFilePIL, 'rb')
    cf.seek(0, 2)
    cleanFileSize = cf.tell()

    df = open(dirtyFile, 'rb')
    df.seek(0, 2)
    dirtyFileSize = df.tell()

    assert cleanFileSize != dirtyFileSize


def test_write_image_file_exit_on_fail():
    """Testing that when failing to write an image there is a system exit."""
    cleanFile = cleanPNGLocation
    dirtyFile = "WriteImageFileThatDoesNotExist.nope"
    dirtyData = bytes(8)

    with pytest.raises(SystemExit):
        write_image_file(cleanFile, dirtyFile, dirtyData)


def test_steganographer_hide_string():
    """Testing that a string will correctly be hidden in a new image."""
    cleanImage = cleanPNGLocation
    dirtyImage = "tests/dirtyImage.png"
    hiddenMessage = "Hidden text from test_steganographerHideString."

    hiddenFname = steganographer_hide(cleanImage, hiddenMessage, dirtyImage)

    assert open(cleanImage, 'rb').read() != open(hiddenFname, 'rb').read()
    assert compare_images(cleanImage, hiddenFname) < 500
    try:
        Image.open(hiddenFname)
    except OSError:
        pytest.fail("Image is corrupt " + hiddenFname)


def test_steganographer_hide_string_correct_name():
    """Testing that the image a string is hidden in is the correct one."""
    cleanImage = cleanPNGLocation
    dirtyImage = "tests/dirtyImage.png"
    hiddenMessage = "Hidden text from test_steganographerHide."

    hiddenFname = steganographer_hide(cleanImage, hiddenMessage, dirtyImage)

    assert hiddenFname == dirtyImage


def test_steganographer_hide_string_steganogrified():
    """Testing that a string will correctly be hidden in a new image, that no name was provided for."""
    cleanImage = cleanPNGLocation
    hiddenMessage = "Hidden text from test_steganographerHideStringSteganogrified."

    hiddenFname = steganographer_hide(cleanImage, hiddenMessage)

    assert open(cleanImage, 'rb').read() != open(hiddenFname, 'rb').read()
    assert compare_images(cleanImage, hiddenFname) < 500
    try:
        Image.open(hiddenFname)
    except OSError:
        pytest.fail("Image is corrupt " + hiddenFname)


def test_steganographer_hide_string_steganogrified_correct_name():
    """Testing that the image a string is hidden in is the correct one."""
    cleanImage = cleanPNGLocation
    hiddenMessage = "Hidden text from test_steganographerHideStringSteganogrified."

    hiddenFname = steganographer_hide(cleanImage, hiddenMessage)
    steganogrifiedFname = cleanPNGLocation[:-4] + "Steganogrified.png"

    assert hiddenFname == steganogrifiedFname
    assert os.path.isfile(steganogrifiedFname)


@given(hiddenMessage=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_steganographer_hide_steganographer_reveal_inverse(hiddenMessage):
    """Testing that steganographer_reveal reveals what was hidden by steganographer_hide."""
    cleanImage = cleanPNGLocation
    dirtyImage = "tests/dirtyImage.png"

    revealedMessage = steganographer_reveal(steganographer_hide(cleanImage, hiddenMessage, dirtyImage))
    assert revealedMessage == hiddenMessage


def test_steganographer_null_data():
    """Testing that the string entered is the string returned. The data is the exact length needed."""
    testString = "This is a test String"
    testData = bytes(testString, 'utf-8')
    blankData = bytes(b'\x01' * len(testString) * byteLen)

    hiddenString = hide_string(blankData, testString)
    revealedString = reveal_string(hiddenString)

    hiddenData = hide_data(blankData, testData)
    revealedData = reveal_data(hiddenData)

    assert testString == revealedString
    assert testData == revealedData


def test_steganographer_short_data():
    """Testing that when the data is too small, by a full byte, that everything that can be returned is returned."""
    testString = "This is a test String"
    testData = bytes(testString, 'utf-8')
    blankData = bytes(b'\x01' * (len(testString) * byteLen - byteLen))

    hiddenString = hide_string(blankData, testString)
    revealedString = reveal_string(hiddenString)

    hiddenData = hide_data(blankData, testData)
    revealedData = reveal_data(hiddenData)

    assert testString[:-1] == revealedString
    assert testData[:-1] == revealedData


def test_steganographer_short_partial_data():
    """Testing that when the data is too small, by a half byte, that everything that can be returned is returned."""
    testString = "This is a test String"
    solutionString = testString[:-1] + chr(ord(testString[-1]) >> byteLen // 2 << byteLen // 2)
    testData = bytes(testString, 'utf-8')
    solutionData = bytearray(testData)
    solutionData[-1] = solutionData[-1] >> byteLen // 2 << byteLen // 2
    blankData = bytes(b'\x01' * (len(testString) * byteLen - byteLen // 2))

    hiddenString = hide_string(blankData, testString)
    revealedString = reveal_string(hiddenString)

    hiddenData = hide_data(blankData, testData)
    revealedData = reveal_data(hiddenData)

    assert solutionString == revealedString
    assert solutionData == revealedData


def compare_images(img1, img2):
    """Expects strings of the locations of two images. Will return an integer representing their difference"""
    img1 = Image.open(img1)
    img2 = Image.open(img2)

    # calculate the difference and its norms
    diff = ImageChops.difference(img1, img2)
    m_norm = sum(unpack_image(diff.getdata()))  # Manhattan norm

    return m_norm


def normalize(arr):
    """Normalizes a list of pixels."""
    rng = arr.max() - arr.min()
    amin = arr.min()

    return (arr - amin) * 255 / rng


def test_main_hide_msg_with_output(capfd):
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


def test_main_hide_msg_no_output(capfd):
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


def test_main_reveal_msg_no_output(capfd):
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


def test_main_reveal_msg_no_output_unicode(capfd):
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


def test_main_reveal_msg_with_output(capfd):
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

    assert message == steganographer_reveal(steganographer_hide(cleanPNGLocation, message, "tests/dirtyImage.png"))
