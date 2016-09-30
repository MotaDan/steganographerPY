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
    """Testing that the hide_byte function does hide a byte and returns the test_data with that byte hidden."""
    test_data = bytes(b'\x01' * byteLen)
    data_to_hide = bytes('A', 'utf-8')
    solution_data = bytearray(byteLen)
    solution_data[1] = 1
    solution_data[7] = 1

    assert hide_byte(test_data, data_to_hide[0]) == solution_data


def test_reveal_byte():
    """Testing that the reveal_byte function returns a bytes of the hidden byte."""
    test_data = bytearray(byteLen)
    test_data[1] = 1
    test_data[7] = 1
    solution_data = bytes('A', 'utf-8')

    assert reveal_byte(test_data) == solution_data


@given(data_to_hide=binary(min_size=1, max_size=1))
def test_hide_reveal_byte_inverse(data_to_hide):
    """Testing that anything hidden by hide_byte is revealed by reveal_byte."""
    clean_data = bytes(b'\x01' * 8)

    revealed_byte = reveal_byte(hide_byte(clean_data, data_to_hide[0]))
    assert revealed_byte == data_to_hide


def test_hide_string():
    """Testing that hide_string takes in a string and bytes and hides the string in that bytes."""
    test_data = bytes(b'\x01' * byteLen * 3)
    solution_data = bytearray(byteLen * 3)
    solution_data[1] = 1
    solution_data[7] = 1
    solution_data[9] = 1
    solution_data[14] = 1
    solution_data[17] = 1
    solution_data[22] = 1
    solution_data[23] = 1

    assert hide_string(test_data, 'ABC') == solution_data


def test_reveal_string():
    """Testing that reveal_string returns a string of the data that was hidden in test_data."""
    test_data = bytearray(byteLen * 4)
    test_data[1] = 1
    test_data[7] = 1
    test_data[9] = 1
    test_data[14] = 1
    test_data[17] = 1
    test_data[22] = 1
    test_data[23] = 1

    assert reveal_string(test_data) == 'ABC'


@given(string_to_hide=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_hide_reveal_string_inverse(string_to_hide):
    """Testing that anything hidden by hide_string is revealed by reveal_string."""
    clean_data = bytes(b'\x01' * 5000)

    revealed_string = reveal_string(hide_string(clean_data, string_to_hide))
    assert revealed_string == string_to_hide


def test_hide_data():
    """Testing that hide_data will hide one bytes inside another."""
    test_data = bytes(b'\x01' * byteLen * 4)
    data_to_hide = bytes('ABC', 'utf-8')
    solution_data = bytearray(byteLen * 3) + bytearray(b'\x01' * byteLen)
    solution_data[1] = 1
    solution_data[7] = 1
    solution_data[9] = 1
    solution_data[14] = 1
    solution_data[17] = 1
    solution_data[22] = 1
    solution_data[23] = 1

    assert hide_data(test_data, data_to_hide) == solution_data


def test_hide_data_partial():
    """Testing that hide_data will work when given a test_data bytes that is too short to hold the data"""
    test_data = bytes(b'\x01' * byteLen * 3)
    data_to_hide = bytes('ABC', 'utf-8')
    solution_data = bytearray(byteLen * 3)
    solution_data[1] = 1
    solution_data[7] = 1
    solution_data[9] = 1
    solution_data[14] = 1
    solution_data[17] = 1
    solution_data[22] = 1
    solution_data[23] = 1

    # Testing when only half a byte is passed in for the data that contains the hidden text.
    assert hide_data(test_data[:4], data_to_hide) == solution_data[:4]


def test_reveal_data():
    """Testing that reveal_data will return the correct data that is hidden inside the test_data."""
    test_data = bytearray(byteLen * 3)
    test_data[1] = 1
    test_data[7] = 1
    test_data[9] = 1
    test_data[14] = 1
    test_data[17] = 1
    test_data[22] = 1
    test_data[23] = 1
    solution_data = bytes('ABC', 'utf-8')

    assert reveal_data(test_data) == solution_data


def test_reveal_data_partial():
    """
    Testing that reveal data will return as much data as possible.

    When the test_data passed in is too small for the data to be hidden.
    """
    test_data = bytearray(byteLen * 3)  # Will contain 'ABC' but will be truncated when passed to reveal_data
    test_data[1] = 1
    test_data[7] = 1
    test_data[9] = 1
    test_data[14] = 1
    test_data[17] = 1
    test_data[22] = 1
    test_data[23] = 1
    solution_data = bytes('AB@', 'utf-8')

    assert reveal_data(test_data[:-byteLen // 2]) == solution_data


@pytest.mark.xfail(strict=True, reason="Issue #50 need to change how data is hidden and revealed.", run=True)
@given(string_to_hide=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_hide_reveal_data_inverse(string_to_hide):
    """Testing that anything hidden by hide_data is revealed by reveal_data."""
    clean_data = bytes(b'\x01' * 5000)
    data_to_hide = bytes(string_to_hide, 'utf-8')

    revealed_data = reveal_data(hide_data(clean_data, data_to_hide))
    assert revealed_data == data_to_hide


def test_unpack_image():
    """Testing that unpacking returns a bytes full of all the pixels flattened."""
    pixel = 1, 2, 3, 4
    solution_pixels = bytes(list(pixel * 4))
    test_pixels = []

    for _ in range(4):
        test_pixels.append(pixel)

    unpacked = unpack_image(test_pixels)

    assert unpacked == solution_pixels


def test_pack_image():
    """Testing that packing returns a list with tuples of length 4."""
    pixel = 1, 2, 3, 4
    test_pixels = list(pixel * 4)
    solution_pixels = []

    for _ in range(4):
        solution_pixels.append(pixel)

    packed = pack_image(test_pixels)

    assert packed == solution_pixels


def test_unpack_pack_inverse():
    """Testing that pixels unpacked by unpack_image are correctly packed by pack_image."""
    pixel = 1, 2, 3, 4
    test_pixels = []

    for _ in range(4):
        test_pixels.append(pixel)

    assert pack_image(unpack_image(test_pixels)) == test_pixels


def test_open_bin_file():
    """Testing that opening the file works."""
    clean_file = cleanPNGLocation
    file_data = open_bin_file(clean_file)

    with open(clean_file, 'rb') as f:
        assert file_data == f.read()

    with pytest.raises(SystemExit):
        open_bin_file("OpenBinFileThatDoesNotExist.nope")


def test_write_bin_file_diff_content():
    """Testing that the file written is different from the one read, after hiding a message."""
    clean_file = cleanPNGLocation
    dirty_file = "tests/dirtyImage_test_write_bin_file_diff_content.png"
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirty_file):
        os.remove(dirty_file)

    data = hide_string(open_bin_file(clean_file), "Hidden text from test_writeBinFileDiffContent.")
    write_bin_file(dirty_file, data)

    with open(clean_file, 'rb') as cf, open(dirty_file, 'rb') as df:
        assert cf.read() != df.read()

    os.remove(dirty_file)


def test_write_bin_file_size_same():
    """Testing that the file written is the same size as the one read, after hiding a message."""
    clean_file = cleanPNGLocation
    dirty_file = "tests/dirtyImage_test_write_bin_file_size_same.png"

    data = hide_string(open_bin_file(clean_file), "Hidden text from test_writeBinFileSizeSame.")
    write_bin_file(dirty_file, data)

    # Getting the file sizes for the clean and dirty files.
    with open(clean_file, 'rb') as cf:
        cf.seek(0, 2)
        clean_file_size = cf.tell()

    with open(dirty_file, 'rb') as df:
        df.seek(0, 2)
        dirty_file_size = df.tell()

    assert clean_file_size == dirty_file_size

    os.remove(dirty_file)


def test_open_image_file():
    """Testing that opening an image file returns the data in the file."""
    clean_file = cleanPNGLocation
    image_data = open_image_file(clean_file)

    with Image.open(clean_file) as im:
        pixels = im.getdata()

    assert image_data == unpack_image(pixels)

    with pytest.raises(SystemExit):
        open_image_file("OpenImageFileThatDoesNotExist.nope")


def test_write_image_file_valid_image():
    """Testing that the image created is not corrupt."""
    clean_file = cleanPNGLocation
    dirty_file = "tests/dirtyImage_test_write_image_file_valid_image.png"
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirty_file):
        os.remove(dirty_file)

    dirty_data = hide_string(open_image_file(clean_file), "Hidden text from test_writeImageFileValidImage.")
    write_image_file(dirty_file, clean_file, dirty_data)

    try:
        Image.open(dirty_file)
    except OSError:
        pytest.fail("Image is corrupt " + dirty_file)

    os.remove(dirty_file)


def test_write_image_file_diff_content():
    """Testing that writing out an image creates a different image at the bit level."""
    clean_file = cleanPNGLocation
    dirty_file = "tests/dirtyImage_test_write_image_file_diff_content.png"
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirty_file):
        os.remove(dirty_file)

    dirty_data = hide_string(open_image_file(clean_file), "Hidden text from test_writeImageFileDiffContent.")
    write_image_file(dirty_file, clean_file, dirty_data)

    with open(clean_file, 'rb') as cf, open(dirty_file, 'rb') as df:
        assert cf.read() != df.read()

    os.remove(dirty_file)


def test_write_image_file_same_image():
    """Testing that writing out an image creates the same image when viewed generally."""
    clean_file = cleanPNGLocation
    dirty_file = "tests/dirtyImage_test_write_image_file_same_image.png"
    # Removing dirty file if it is there from another test.
    if os.path.isfile(dirty_file):
        os.remove(dirty_file)

    dirty_data = hide_string(open_image_file(clean_file), "Hidden text from test_writeImageFileSameImage.")
    write_image_file(dirty_file, clean_file, dirty_data)

    assert compare_images(clean_file, dirty_file) < 500

    os.remove(dirty_file)


def test_write_image_file_diff_size():
    """Testing that writing out an image creates a file of a different size, if the file was not generated by PIL."""
    clean_file = cleanPNGLocation
    dirty_file = "tests/dirtyImage_test_write_image_file_diff_size.png"

    dirty_data = hide_string(open_image_file(clean_file), "Hidden text from test_writeImageFileDiffSize.")
    write_image_file(dirty_file, clean_file, dirty_data)

    # Getting the file sizes for the clean and dirty files.
    with open(clean_file, 'rb') as cf:
        cf.seek(0, 2)
        clean_file_size = cf.tell()

    with open(dirty_file, 'rb') as df:
        df.seek(0, 2)
        dirty_file_size = df.tell()

    assert clean_file_size != dirty_file_size

    os.remove(dirty_file)


def test_write_image_file_diff_size_pil():
    """Testing that writing out an image creates a file of a different size, if the file was generated by PIL."""
    clean_file = cleanPNGLocation
    dirty_file = "tests/dirtyImage_test_write_image_file_diff_size_pil.png"
    clean_file_pil = "tests/cleanImagePIL.png"
    with Image.open(clean_file) as pil_image:
        pil_image.save(clean_file_pil)

    dirty_data = hide_string(open_image_file(clean_file_pil), "Hidden text from test_writeImageFileSameImage.")
    write_image_file(dirty_file, clean_file_pil, dirty_data)

    # Getting the file sizes for the clean and dirty files.
    with open(clean_file_pil, 'rb') as cf:
        cf.seek(0, 2)
        clean_file_size = cf.tell()

    with open(dirty_file, 'rb') as df:
        df.seek(0, 2)
        dirty_file_size = df.tell()

    assert clean_file_size != dirty_file_size

    os.remove(dirty_file)


def test_write_image_file_exit_on_fail():
    """Testing that when failing to write an image there is a system exit."""
    clean_file = cleanPNGLocation
    dirty_file = "WriteImageFileThatDoesNotExist.nope"
    dirty_data = bytes(8)

    with pytest.raises(SystemExit):
        write_image_file(clean_file, dirty_file, dirty_data)


def test_steganographer_hide_string():
    """Testing that a string will correctly be hidden in a new image."""
    clean_image = cleanPNGLocation
    dirty_image = "tests/dirtyImage_test_steganographer_hide_string.png"
    hidden_message = "Hidden text from test_steganographer_hide_string."

    hidden_fname = steganographer_hide(clean_image, hidden_message, dirty_image)

    with open(clean_image, 'rb') as ci, open(hidden_fname, 'rb') as di:
        assert ci.read() != di.read()
    assert compare_images(clean_image, hidden_fname) < 500
    try:
        Image.open(hidden_fname)
    except OSError:
        pytest.fail("Image is corrupt " + hidden_fname)

    os.remove(dirty_image)


def test_steganographer_hide_string_correct_name():
    """Testing that the image a string is hidden in is the correct one."""
    clean_image = cleanPNGLocation
    dirty_image = "tests/dirtyImage_test_steganographer_hide_string_correct_name.png"
    hidden_message = "Hidden text from test_steganographer_hide_string_correct_name."

    hidden_fname = steganographer_hide(clean_image, hidden_message, dirty_image)

    assert hidden_fname == dirty_image

    os.remove(dirty_image)


def test_steganographer_hide_string_steganogrified():
    """Testing that a string will correctly be hidden in a new image, that no name was provided for."""
    clean_image = cleanPNGLocation
    hidden_message = "Hidden text from test_steganographer_hide_string_steganogrified."

    hidden_fname = steganographer_hide(clean_image, hidden_message)

    with open(clean_image, 'rb') as ci, open(hidden_fname, 'rb') as di:
        assert ci.read() != di.read()
    assert compare_images(clean_image, hidden_fname) < 500
    try:
        Image.open(hidden_fname)
    except OSError:
        pytest.fail("Image is corrupt " + hidden_fname)


def test_steganographer_hide_string_steganogrified_correct_name():
    """Testing that the image a string is hidden in is the correct one."""
    clean_image = cleanPNGLocation
    hidden_message = "Hidden text from test_steganographer_hide_string_steganogrified_correct_name."

    hidden_fname = steganographer_hide(clean_image, hidden_message)
    steganogrified_fname = cleanPNGLocation[:-4] + "Steganogrified.png"

    assert hidden_fname == steganogrified_fname
    assert os.path.isfile(steganogrified_fname)


@given(hidden_message=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_steganographer_hide_steganographer_reveal_inverse(hidden_message):
    """Testing that steganographer_reveal reveals what was hidden by steganographer_hide."""
    clean_image = cleanPNGLocation
    dirty_image = "tests/dirtyImage_test_steganographer_hide_steganographer_reveal_inverse.png"

    revealed_message = steganographer_reveal(steganographer_hide(clean_image, hidden_message, dirty_image))
    assert revealed_message == hidden_message

    os.remove(dirty_image)


def test_steganographer_null_data():
    """Testing that the string entered is the string returned. The data is the exact length needed."""
    test_string = "This is a test String"
    test_data = bytes(test_string, 'utf-8')
    blank_data = bytes(b'\x01' * len(test_string) * byteLen)

    hidden_string = hide_string(blank_data, test_string)
    revealed_string = reveal_string(hidden_string)

    hidden_data = hide_data(blank_data, test_data)
    revealed_data = reveal_data(hidden_data)

    assert test_string == revealed_string
    assert test_data == revealed_data


def test_steganographer_short_data():
    """Testing that when the data is too small, by a full byte, that everything that can be returned is returned."""
    test_string = "This is a test String"
    test_data = bytes(test_string, 'utf-8')
    blank_data = bytes(b'\x01' * (len(test_string) * byteLen - byteLen))

    hidden_string = hide_string(blank_data, test_string)
    revealed_string = reveal_string(hidden_string)

    hidden_data = hide_data(blank_data, test_data)
    revealed_data = reveal_data(hidden_data)

    assert test_string[:-1] == revealed_string
    assert test_data[:-1] == revealed_data


def test_steganographer_short_partial_data():
    """Testing that when the data is too small, by a half byte, that everything that can be returned is returned."""
    test_string = "This is a test String"
    solution_string = test_string[:-1] + chr(ord(test_string[-1]) >> byteLen // 2 << byteLen // 2)
    test_data = bytes(test_string, 'utf-8')
    solution_data = bytearray(test_data)
    solution_data[-1] = solution_data[-1] >> byteLen // 2 << byteLen // 2
    blank_data = bytes(b'\x01' * (len(test_string) * byteLen - byteLen // 2))

    hidden_string = hide_string(blank_data, test_string)
    revealed_string = reveal_string(hidden_string)

    hidden_data = hide_data(blank_data, test_data)
    revealed_data = reveal_data(hidden_data)

    assert solution_string == revealed_string
    assert solution_data == revealed_data


def compare_images(img1, img2):
    """Expects strings of the locations of two images. Will return an integer representing their difference"""
    with Image.open(img1) as img1, Image.open(img2) as img2:
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
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_main_hide_msg_with_output hidden message'
    dirty_fname = "tests/dirtyImage_test_main_hide_msg_with_output.png"

    result = os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hidden_message +
                       '" -o ' + dirty_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == "The message has been hidden in " + dirty_fname + line_end
    assert compare_images(cleanPNGLocation, dirty_fname) < 500
    try:
        Image.open(dirty_fname)
    except OSError:
        pytest.fail("Image is corrupt " + dirty_fname)

    os.remove(dirty_fname)


def test_main_hide_msg_no_output(capfd):
    """Testing that main works when given input, message, and no output."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_main_hide_msg_no_output hidden message'
    steganogrified_fname = cleanPNGLocation[:-4] + "Steganogrified.png"

    result = os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hidden_message + '"')
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == "The message has been hidden in " + steganogrified_fname + line_end
    assert compare_images(cleanPNGLocation, steganogrified_fname) < 500
    try:
        Image.open(steganogrified_fname)
    except OSError:
        pytest.fail("Image is corrupt " + steganogrified_fname)


def test_main_reveal_msg_no_output(capfd):
    """Testing that main works when given input, message, and no output."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_main_reveal_msg_no_output hidden message'
    dirty_fname = "tests/dirtyImage_test_main_reveal_msg_no_output.png"

    os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hidden_message +
              '" -o ' + dirty_fname)
    _, _ = capfd.readouterr()

    result = os.system("python -m steganographer " + dirty_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == ("The hidden message was..." + line_end + hidden_message + line_end)

    os.remove(dirty_fname)


def test_main_reveal_msg_no_output_unicode(capfd):
    """Testing that main works when given input, message, and no output."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_main_reveal_msg_no_output_unicode hidden message, Unicode characters: 𓁈 ᾨ ԅ Թ ػ ޗ ߚ ङ ლ ጩ Ꮬ'
    dirty_fname = "tests/dirtyImage_test_main_reveal_msg_no_output_unicode.png"
    output_fname = "tests/dirtyImage_test_main_reveal_msg_no_output_unicode_message.txt"

    os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hidden_message +
              '" -o ' + dirty_fname)
    _, _ = capfd.readouterr()

    result = os.system("python -m steganographer " + dirty_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    with open(output_fname, 'r', encoding='utf-8') as output:
        assert output.read() == hidden_message

    assert (out == ("The hidden message contains unsupported unicode characters and cannot be fully displayed " +
                    "here. The correct message has been written to " + output_fname + line_end +
                    str(hidden_message.encode('utf-8')) + line_end)
            or out == ("The hidden message was..." + line_end + hidden_message + line_end))

    os.remove(dirty_fname)


def test_main_reveal_msg_with_output(capfd):
    """Testing that main works when given input, message, and no output."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_main_reveal_msg_with_output hidden message'
    dirty_fname = "tests/dirtyImage_test_main_reveal_msg_with_output.png"
    output_fname = "tests/outputMessage.txt"

    os.system('python -m steganographer ' + cleanPNGLocation + ' -m "' + hidden_message +
              '" -o ' + dirty_fname)
    _, _ = capfd.readouterr()

    result = os.system("python -m steganographer " + dirty_fname + " -o " + output_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    with open(output_fname, 'r') as output:
        assert output.read() == hidden_message

    assert out == ("The hidden message was written to " + output_fname + line_end)

    os.remove(dirty_fname)


@pytest.mark.xfail(strict=True, reason="Issue #28 jpeg support not added.", run=False)
def test_jpegs():
    """Testing that jpegs can have a message hidden and revealed."""
    hidden_message = '"test_jpeg hidden message"'
    result = os.system('python -m steganographer tests/cleanImage.jpg -m ' + hidden_message +
                       ' -o tests/dirtyImage.jpg')

    assert result == 0
    assert compare_images("tests/cleanImage.jpg", "tests/dirtyImage.jpg") < 500

    result = os.system("python -m steganographer tests/dirtyImage.jpg")
    assert result == 0


@pytest.mark.xfail(strict=True, reason="Issue #30 bmp support not added.", run=False)
def test_bmps():
    """Testing that jpegs can have a message hidden and revealed."""
    hidden_message = '"test_bmps hidden message"'
    result = os.system('python -m steganographer tests/cleanImage.bmp -m ' + hidden_message +
                       ' -o tests/dirtyImage.bmp')

    assert result == 0
    assert compare_images("tests/cleanImage.bmp", "tests/dirtyImage.bmp") < 500

    result = os.system("python -m steganographer tests/dirtyImage.bmp")
    assert result == 0


def test_unicode():
    """Testing that unicode characters are hidden and revealed."""
    message = "test_unicode hidden message. Some random unicode characters: 𓁈 ᾨ ԅ Թ ػ ޗ ߚ ङ ლ ጩ Ꮬ"

    assert message == steganographer_reveal(steganographer_hide(cleanPNGLocation, message, "tests/dirtyImage.png"))
