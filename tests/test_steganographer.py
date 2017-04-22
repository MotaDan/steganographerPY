# pylint: disable=protected-access
"""Testing script"""
import pytest
from PIL import ImageChops, Image
import sys
import os
import os.path
from hypothesis import given
from hypothesis.strategies import text, binary, characters
from shutil import copy2

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# noinspection PyPep8
from steganographer.steganographer import Steganographer
# noinspection PyPep8
from steganographer.steganographer import _unpack_image, _pack_image, _open_bin_file, _write_bin_file, \
    _open_image_file, _write_image_file

CLEAN_PNG_LOCATION = "tests/cleanImage.png"


def test_generate_header():
    """The header is generated as expected"""
    stegs = Steganographer()
    header = bytes(stegs._header._HEADER_TITLE, 'utf-8') + \
        bytes(stegs._header.data_len.to_bytes(stegs._header._HEADER_DATA_SIZE, "little")) + \
        bytes(stegs._header.bits_used.to_bytes(stegs._header._HEADER_BITS_SIZE, "little")) + \
        bytes(stegs._header.file_name_len.to_bytes(stegs._header._HEADER_FILE_LENGTH_SIZE, "little"))

    assert header == stegs._generate_header(stegs._header.data_len, stegs._header.bits_used, "")


def test_retrieve_header():
    """The header is retrieved as expected"""
    stegs = Steganographer()
    test_message = "12345".encode('utf-8')
    test_data_len = len(test_message)
    test_bits_used = 1
    test_file_name = "test_retrieve_header.txt"
    test_file_name_len = len(test_file_name)
    test_data = bytes(b'\x01' * 1000)

    test_header = stegs._generate_header(test_data_len, test_bits_used, test_file_name)
    hidden_data = stegs._hide_data(test_data[:stegs._header.header_length * stegs._BYTELEN], test_header)
    hidden_data += stegs._hide_data(test_data[stegs._header.header_length * stegs._BYTELEN:], test_message)
    header_retrieved = stegs._retrieve_header(hidden_data)

    assert header_retrieved is True
    assert stegs._header.data_len == test_data_len
    assert stegs._header.bits_used == test_bits_used
    assert stegs._header.file_name_len == test_file_name_len
    assert stegs._header.file_name.decode('utf-8') == test_file_name


def test_hide_byte():
    """The _hide_byte function does hide a byte and returns the test_data with that byte hidden."""
    stegs = Steganographer()
    test_data = bytes(b'\x01' * stegs._BYTELEN)
    data_to_hide = bytes('A', 'utf-8')
    solution_data = bytearray(stegs._BYTELEN)
    solution_data[1] = 1
    solution_data[7] = 1

    assert stegs._hide_byte(test_data, data_to_hide[0]) == solution_data


def test_reveal_byte():
    """The _reveal_byte function returns a bytes object of the hidden byte."""
    stegs = Steganographer()
    test_data = bytearray(stegs._BYTELEN)
    test_data[1] = 1
    test_data[7] = 1
    solution_data = bytes('A', 'utf-8')

    assert stegs._reveal_byte(test_data) == solution_data


@given(data_to_hide=binary(min_size=1, max_size=1))
def test_hide_reveal_byte_inverse(data_to_hide):
    """Anything hidden by _hide_byte is revealed by _reveal_byte."""
    clean_data = bytes(b'\x01' * 8)

    stegs = Steganographer()
    revealed_byte = stegs._reveal_byte(stegs._hide_byte(clean_data, data_to_hide[0]))
    assert revealed_byte == data_to_hide


def test_hide_string():
    """Takes in a string and a bytes object and hides the string in that bytes object."""
    stegs = Steganographer()
    test_data = bytes(b'\x01' * stegs._BYTELEN * 3)
    solution_data = bytearray(stegs._BYTELEN * 3)
    solution_data[1] = 1
    solution_data[7] = 1
    solution_data[9] = 1
    solution_data[14] = 1
    solution_data[17] = 1
    solution_data[22] = 1
    solution_data[23] = 1

    assert stegs._hide_string(test_data, 'ABC') == solution_data


def test_reveal_string():
    """Returns a string representation of the data that was hidden in the test_data."""
    solution = 'ABC'
    stegs = Steganographer()
    stegs._header.data_len = len(solution)
    test_data = bytearray(stegs._BYTELEN * 4)
    test_data[1] = 1
    test_data[7] = 1
    test_data[9] = 1
    test_data[14] = 1
    test_data[17] = 1
    test_data[22] = 1
    test_data[23] = 1

    assert stegs._reveal_string(test_data) == solution


@given(string_to_hide=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_hide_reveal_string_inverse(string_to_hide):
    """Anything hidden by _hide_string is revealed by _reveal_string."""
    clean_data = bytes(b'\x01' * 5000)
    stegs = Steganographer()
    stegs._header.data_len = len(string_to_hide.encode('utf-8'))
    revealed_string = stegs._reveal_string(stegs._hide_string(clean_data, string_to_hide))
    assert revealed_string == string_to_hide


def test_hide_data():
    """Will hide one bytes object inside another."""
    stegs = Steganographer()
    test_data = bytes(b'\x01' * stegs._BYTELEN * 4)
    data_to_hide = bytes('ABC', 'utf-8')
    stegs._header.data_len = len(data_to_hide)
    solution_data = bytearray(stegs._BYTELEN * 4)
    solution_data[1] = 1
    solution_data[7] = 1
    solution_data[9] = 1
    solution_data[14] = 1
    solution_data[17] = 1
    solution_data[22] = 1
    solution_data[23] = 1
    solution_data[24:] = b'\x01' * stegs._BYTELEN

    assert stegs._hide_data(test_data, data_to_hide) == solution_data


def test_hide_data_partial():
    """Will work when given a bytes object that is too short to contain the full data to be hidden."""
    stegs = Steganographer()
    test_data = bytes(b'\x01' * stegs._BYTELEN * 3)
    data_to_hide = bytes('ABC', 'utf-8')
    stegs._header.data_len = len(data_to_hide)
    solution_data = bytearray(stegs._BYTELEN * 3)
    solution_data[1] = 1
    solution_data[7] = 1
    solution_data[9] = 1
    solution_data[14] = 1
    solution_data[17] = 1
    solution_data[22] = 1
    solution_data[23] = 1

    # Testing when only half a byte is passed in for the data that contains the hidden text.
    assert stegs._hide_data(test_data[:4], data_to_hide) == solution_data[:4]


def test_reveal_data():
    """Will return the correct data that is hidden inside the test_data."""
    solution_data = bytes('ABC', 'utf-8')
    stegs = Steganographer()
    stegs._header.data_len = len(solution_data)
    test_data = bytearray(stegs._BYTELEN * 3)
    test_data[1] = 1
    test_data[7] = 1
    test_data[9] = 1
    test_data[14] = 1
    test_data[17] = 1
    test_data[22] = 1
    test_data[23] = 1

    assert stegs._reveal_data(test_data) == solution_data


def test_reveal_data_partial():
    """
    Will return as much data as possible.

    When the container bytes object passed in is too small for all the data to be hidden.
    """
    stegs = Steganographer()
    solution_data = bytes('AB@', 'utf-8')
    test_data = bytearray(stegs._BYTELEN * 3)  # Will contain 'ABC' but will be truncated when passed to _reveal_data
    test_data[1] = 1
    test_data[7] = 1
    test_data[9] = 1
    test_data[14] = 1
    test_data[17] = 1
    test_data[22] = 1
    test_data[23] = 1
    stegs._data_len = len('ABC')

    assert stegs._reveal_data(test_data[:-stegs._BYTELEN // 2]) == solution_data


@given(string_to_hide=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_hide_reveal_data_inverse(string_to_hide):
    """Anything hidden by _hide_data is revealed by _reveal_data."""
    clean_data = bytes(b'\x01' * 5000)
    data_to_hide = bytes(string_to_hide, 'utf-8')

    stegs = Steganographer()
    stegs._header.data_len = len(string_to_hide.encode('utf-8'))
    revealed_data = stegs._reveal_data(stegs._hide_data(clean_data, data_to_hide))

    assert revealed_data == data_to_hide


def test_exact_data_with_string_inverse():
    """The string entered is the string returned. The storing data is the exact length needed."""
    test_string = "This is a test String"
    stegs = Steganographer()
    stegs._header.data_len = len(test_string)
    blank_data = bytes(b'\x01' * len(test_string) * stegs._BYTELEN)

    revealed_string = stegs._reveal_string(stegs._hide_string(blank_data, test_string))

    assert test_string == revealed_string


def test_exact_data_with_data_inverse():
    """The data entered is the data returned. The storing data is the exact length needed."""
    test_string = "This is a test String"
    test_data = bytes(test_string, 'utf-8')
    stegs = Steganographer()
    stegs._header.data_len = len(test_string)
    blank_data = bytes(b'\x01' * len(test_string) * stegs._BYTELEN)

    revealed_data = stegs._reveal_data(stegs._hide_data(blank_data, test_data))

    assert test_data == revealed_data


def test_short_data_with_string_inverse():
    """When the data is too small, by a full byte, everything that can be returned is returned."""
    test_string = "This is a test String"
    stegs = Steganographer()
    stegs._header.data_len = len(test_string)
    blank_data = bytes(b'\x01' * (len(test_string) * stegs._BYTELEN - stegs._BYTELEN))

    revealed_string = stegs._reveal_string(stegs._hide_string(blank_data, test_string))

    assert test_string[:-1] == revealed_string


def test_short_data_with_data_inverse():
    """When the data is too small, by a full byte, everything that can be returned is returned."""
    test_string = "This is a test String"
    test_data = bytes(test_string, 'utf-8')
    stegs = Steganographer()
    stegs._header.data_len = len(test_string)
    blank_data = bytes(b'\x01' * (len(test_string) * stegs._BYTELEN - stegs._BYTELEN))

    revealed_data = stegs._reveal_data(stegs._hide_data(blank_data, test_data))

    assert test_data[:-1] == revealed_data


def test_short_partial_data_string_inverse():
    """When the data is too small, by a half byte, everything that can be returned is returned."""
    test_string = "This is a test String"
    stegs = Steganographer()
    stegs._header.data_len = len(test_string)
    solution_string = test_string[:-1] + chr(ord(test_string[-1]) >> stegs._BYTELEN // 2 << stegs._BYTELEN // 2)
    blank_data = bytes(b'\x01' * (len(test_string) * stegs._BYTELEN - stegs._BYTELEN // 2))

    revealed_string = stegs._reveal_string(stegs._hide_string(blank_data, test_string))

    assert solution_string == revealed_string


def test_short_partial_data_w_data_inverse():
    """When the data is too small, by a half byte, everything that can be returned is returned."""
    test_string = "This is a test String"
    test_data = bytes(test_string, 'utf-8')
    solution_data = bytearray(test_data)
    stegs = Steganographer()
    stegs._header.data_len = len(test_string)
    solution_data[-1] = solution_data[-1] >> stegs._BYTELEN // 2 << stegs._BYTELEN // 2
    blank_data = bytes(b'\x01' * (len(test_string) * stegs._BYTELEN - stegs._BYTELEN // 2))

    revealed_data = stegs._reveal_data(stegs._hide_data(blank_data, test_data))

    assert solution_data == revealed_data


def test_unpack_image():
    """Unpacking returns a bytes object full of all the pixels flattened in one dimension."""
    pixel = 1, 2, 3, 4
    pixel_length = len(pixel)
    solution_pixels = bytes(list(pixel * pixel_length))
    test_pixels = []

    for _ in range(pixel_length):
        test_pixels.append(pixel)

    unpacked = _unpack_image(test_pixels)

    assert unpacked[0] == len(pixel)
    assert unpacked[1] == solution_pixels


def test_pack_image():
    """Packing returns a list with tuples of length 4."""
    pixel = 1, 2, 3, 4
    pixel_length = len(pixel)
    test_pixels = pixel_length, list(pixel * pixel_length)
    solution_pixels = []

    for _ in range(pixel_length):
        solution_pixels.append(pixel)

    packed = _pack_image(test_pixels)

    assert packed == solution_pixels


def test_unpack_pack_inverse():
    """Pixels unpacked by _unpack_image are correctly packed by _pack_image."""
    pixel = 1, 2, 3, 4
    test_pixels = []

    for _ in range(4):
        test_pixels.append(pixel)

    assert _pack_image(_unpack_image(test_pixels)) == test_pixels


def test_open_bin_file():
    """Opening a file works."""
    clean_file = CLEAN_PNG_LOCATION
    file_data = _open_bin_file(clean_file)

    with open(clean_file, 'rb') as file:
        assert file_data == file.read()

    with pytest.raises(SystemExit):
        _open_bin_file("OpenBinFileThatDoesNotExist.nope")


def test_write_bin_diff_content():
    """The file written is different from the one read, after hiding a message."""
    clean_file = CLEAN_PNG_LOCATION
    dirty_file = "tests/dirtyImage_test_write_bin_file_diff_content.png"

    stegs = Steganographer()
    data = stegs._hide_string(_open_bin_file(clean_file), "Hidden text from test_write_bin_diff_content.")
    _write_bin_file(dirty_file, data)

    with open(clean_file, 'rb') as clean, open(dirty_file, 'rb') as dirty:
        assert clean.read() != dirty.read()

    os.remove(dirty_file)


def test_write_bin_file_size_same():
    """The file written is the same size as the one read, after hiding a message."""
    clean_file = CLEAN_PNG_LOCATION
    dirty_file = "tests/dirtyImage_test_write_bin_file_size_same.png"

    stegs = Steganographer()
    data = stegs._hide_string(_open_bin_file(clean_file), "Hidden text from test_write_bin_file_size_same.")
    _write_bin_file(dirty_file, data)

    # Getting the file sizes for the clean and dirty files.
    with open(clean_file, 'rb') as clean:
        clean.seek(0, 2)
        clean_file_size = clean.tell()

    with open(dirty_file, 'rb') as dirty:
        dirty.seek(0, 2)
        dirty_file_size = dirty.tell()

    assert clean_file_size == dirty_file_size

    os.remove(dirty_file)


def test_open_image_file():
    """Opening an image file returns the data in the file in a one dimensional list."""
    clean_file = CLEAN_PNG_LOCATION
    image_data = _open_image_file(clean_file)

    with Image.open(clean_file) as clean:
        pixels = clean.getdata()

    assert image_data[1] == _unpack_image(pixels)[1]

    with pytest.raises(SystemExit):
        _open_image_file("OpenImageFileThatDoesNotExist.nope")


def test_write_image_file_valid():
    """The image created is not corrupt."""
    clean_file = CLEAN_PNG_LOCATION
    dirty_file = "tests/dirtyImage_test_write_image_file_valid_image.png"

    stegs = Steganographer()
    clean_data = _open_image_file(clean_file)
    dirty_data = clean_data[0], stegs._hide_string(clean_data[1], "Hidden text from test_write_image_file_valid.")
    output_file = _write_image_file(dirty_file, clean_file, dirty_data)

    try:
        Image.open(output_file)
    except OSError:
        pytest.fail("Image is corrupt " + output_file)

    os.remove(output_file)


def test_write_image_diff_content():
    """Writing out an image creates a different image at the bit level."""
    clean_file = CLEAN_PNG_LOCATION
    dirty_file = "tests/dirtyImage_test_write_image_file_diff_content.png"

    stegs = Steganographer()
    clean_data = _open_image_file(clean_file)
    dirty_data = clean_data[0], stegs._hide_string(clean_data[1], "Hidden text from test_write_image_diff_content.")
    output_file = _write_image_file(dirty_file, clean_file, dirty_data)

    with open(clean_file, 'rb') as clean, open(output_file, 'rb') as dirty:
        assert clean.read() != dirty.read()

    os.remove(output_file)


def compare_images(img1, img2):
    """Expects strings of the locations of two images. Will return an integer representing their difference"""
    with Image.open(img1) as img1, Image.open(img2) as img2:
        # Calculate a difference image that is the difference between the two images.
        diff = ImageChops.difference(img1, img2)

    return sum(_unpack_image(diff.getdata())[1])


def test_write_image_same_image():
    """Writing out an image creates the same image when viewed generally."""
    clean_file = CLEAN_PNG_LOCATION
    dirty_file = "tests/dirtyImage_test_write_image_file_same_image.png"

    stegs = Steganographer()
    clean_data = _open_image_file(clean_file)
    dirty_data = clean_data[0], stegs._hide_string(clean_data[1], "Hidden text from test_write_image_same_image.")
    output_file = _write_image_file(dirty_file, clean_file, dirty_data)

    assert compare_images(clean_file, output_file) < 500

    os.remove(output_file)


def test_write_image_diff_size():
    """Writing out an image creates a file of a different size, if the file was not generated by PIL originally."""
    clean_file = CLEAN_PNG_LOCATION
    dirty_file = "tests/dirtyImage_test_write_image_file_diff_size.png"

    stegs = Steganographer()
    clean_data = _open_image_file(clean_file)
    dirty_data = clean_data[0], stegs._hide_string(clean_data[1], "Hidden text from test_write_image_diff_size.")
    output_file = _write_image_file(dirty_file, clean_file, dirty_data)

    # Getting the file sizes for the clean and dirty files.
    with open(clean_file, 'rb') as clean:
        clean.seek(0, 2)
        clean_file_size = clean.tell()

    with open(output_file, 'rb') as dirty:
        dirty.seek(0, 2)
        dirty_file_size = dirty.tell()

    assert clean_file_size != dirty_file_size

    os.remove(output_file)


def test_write_image_diff_size_pil():
    """Writing out an image creates a file of a different size, if the file was generated by PIL originally."""
    clean_file = CLEAN_PNG_LOCATION
    dirty_file = "tests/dirtyImage_test_write_image_file_diff_size_pil.png"
    clean_file_pil = "tests/cleanImagePIL.png"
    with Image.open(clean_file) as pil_image:
        pil_image.save(clean_file_pil)

    stegs = Steganographer()
    clean_data = _open_image_file(clean_file_pil)
    dirty_data = clean_data[0], stegs._hide_string(clean_data[1], "Hidden text from test_write_image_diff_size_pil.")
    output_file = _write_image_file(dirty_file, clean_file_pil, dirty_data)

    # Getting the file sizes for the clean and dirty files.
    with open(clean_file_pil, 'rb') as clean:
        clean.seek(0, 2)
        clean_file_size = clean.tell()

    with open(output_file, 'rb') as dirty:
        dirty.seek(0, 2)
        dirty_file_size = dirty.tell()

    assert clean_file_size != dirty_file_size

    os.remove(output_file)


def test_write_image_exit_on_fail():
    """When failing to write an image there is a system exit."""
    clean_file = CLEAN_PNG_LOCATION
    dirty_file = "WriteImageFileThatDoesNotExist.nope"
    dirty_data = bytes(8)

    with pytest.raises(SystemExit):
        _write_image_file(clean_file, dirty_file, dirty_data)


def test_steganographer_hide_string():
    """A string will correctly be hidden in a new image."""
    clean_image = CLEAN_PNG_LOCATION
    dirty_image = "tests/dirtyImage_test_steganographer_hide_string.png"
    hidden_message = "Hidden text from test_steganographer_hide_string."

    stegs = Steganographer()
    hidden_fname = stegs.steganographer_hide(clean_image, hidden_message, dirty_image)

    with open(clean_image, 'rb') as clean, open(hidden_fname, 'rb') as dirty:
        assert clean.read() != dirty.read()
    assert compare_images(clean_image, hidden_fname) < 500
    try:
        Image.open(hidden_fname)
    except OSError:
        pytest.fail("Image is corrupt " + hidden_fname)

    os.remove(dirty_image)


def test_stegs_hide_string_nonsense():
    """A random string, that can cause a decode error, will correctly be hidden in a new image."""
    clean_image = CLEAN_PNG_LOCATION
    dirty_image = "tests/dirtyImage_test_steganographer_hide_string_nonsense.png"
    hidden_message = "Ĝ𐡑ĜĜĜĜĜĜĜĜĜԬĜ\U000fc423ĜĜĜĜԬĜĜĜԬԬĜԬ\U000fc423ĜԬ\U000fc423ԬԬĜ\U000fc423ԬĜԬ𐡕𐡕𐡑𐡕𐡕𐡕𐡑𐡕𐡑𐡕𐡑"

    stegs = Steganographer()
    hidden_fname = stegs.steganographer_hide(clean_image, hidden_message, dirty_image)

    with open(clean_image, 'rb') as clean, open(hidden_fname, 'rb') as dirty:
        assert clean.read() != dirty.read()
    assert compare_images(clean_image, hidden_fname) < 650
    try:
        Image.open(hidden_fname)
    except OSError:
        pytest.fail("Image is corrupt " + hidden_fname)

    os.remove(dirty_image)


def test_steganographer_hide_file():
    """A file can be hidden inside of an image and the image created is not corrupt"""
    clean_image = CLEAN_PNG_LOCATION
    dirty_image = "tests/dirtyImage_test_steganographer_hide_file.png"
    file_to_hide = "tests/FileToHide.zip"

    stegs = Steganographer()
    hidden_fname = stegs.steganographer_hide_file(clean_image, file_to_hide, dirty_image)

    with open(clean_image, 'rb') as clean, open(hidden_fname, 'rb') as dirty:
        assert clean.read() != dirty.read()
    assert compare_images(clean_image, hidden_fname) < 19000
    try:
        Image.open(hidden_fname)
    except OSError:
        pytest.fail("Image is corrupt " + hidden_fname)

    os.remove(hidden_fname)


def test_steganographer_reveal_file():
    """A file that has been hidden can be revealed."""
    original_file = "tests/FileToHide.zip"
    dirty_image = "tests/dirtyImageWFile.png"
    revealed_file_name = "tests/test_steganographer_reveal_file.zip"

    stegs = Steganographer()
    revealed_file_data = stegs.steganographer_reveal(dirty_image)

    with open(revealed_file_name, 'wb') as rev_file:
        rev_file.write(revealed_file_data)

    with open(original_file, 'rb') as original, open(revealed_file_name, 'rb') as revealed:
        assert original.read() == revealed.read()

    os.remove(revealed_file_name)


def test_steganographer_hide_name():
    """The image a string is hidden in is the correct one."""
    clean_image = CLEAN_PNG_LOCATION
    dirty_image = "tests/dirtyImage_test_steganographer_hide_name.png"
    hidden_message = "Hidden text from test_steganographer_hide_name."

    stegs = Steganographer()
    hidden_fname = stegs.steganographer_hide(clean_image, hidden_message, dirty_image)

    assert hidden_fname == dirty_image

    os.remove(dirty_image)


def test_steganogrified_name():
    """Data will be hidden in a file with steganogrified at the end, when no output file name is provided."""
    clean_message_image = copy2(CLEAN_PNG_LOCATION, CLEAN_PNG_LOCATION[:-4] + "_test_message_steganogrified_name.png")
    clean_file_image = copy2(CLEAN_PNG_LOCATION, CLEAN_PNG_LOCATION[:-4] + "_test_file_steganogrified_name.png")
    hidden_message = "Hidden text from test_steganogrified_name."
    file_to_hide = "tests/FileToHide.zip"

    stegs = Steganographer()
    hidden_message_fname = stegs.steganographer_hide(clean_message_image, hidden_message)
    steganogrified_message_fname = clean_message_image[:-4] + "Steganogrified.png"
    hidden_file_fname = stegs.steganographer_hide_file(clean_file_image, file_to_hide)
    steganogrified_file_fname = clean_file_image[:-4] + "Steganogrified.png"

    assert hidden_message_fname == steganogrified_message_fname
    assert os.path.isfile(steganogrified_message_fname)
    assert hidden_file_fname == steganogrified_file_fname
    assert os.path.isfile(steganogrified_file_fname)

    os.remove(clean_message_image)
    os.remove(hidden_message_fname)
    os.remove(clean_file_image)
    os.remove(hidden_file_fname)


@given(hidden_message=text(characters(min_codepoint=1, blacklist_categories=('Cc', 'Cs'))))
def test_steganographer_inverse(hidden_message):
    """Steganographer_reveal reveals what was hidden by steganographer_hide."""
    clean_image = CLEAN_PNG_LOCATION
    dirty_image = "tests/dirtyImage_test_steganographer_inverse.png"

    stegs = Steganographer()
    revealed_message = stegs.steganographer_reveal(stegs.steganographer_hide(
        clean_image, hidden_message, dirty_image)).decode('utf-8')
    assert revealed_message == hidden_message

    os.remove(dirty_image)


def test_unicode_inverse():
    """Unicode characters are hidden and revealed."""
    message = "test_unicode hidden message. Some random unicode characters: 𓁈 ᾨ ԅ Թ ػ ޗ ߚ ङ ლ ጩ Ꮬ"

    stegs = Steganographer()
    assert message == stegs.steganographer_reveal(stegs.steganographer_hide(CLEAN_PNG_LOCATION, message,
                                                                            "tests/dirtyImage.png")).decode('utf-8')


def test_main_hide_msg_with_output(capfd):
    """Command line calls to hide work when given an input image, a message, and an output file."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_main_hide_msg_with_output hidden message'
    dirty_fname = "tests/dirtyImage_test_main_hide_msg_with_output.png"

    result = os.system('python -m steganographer ' + CLEAN_PNG_LOCATION + ' -m "' + hidden_message +
                       '" -o ' + dirty_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == "The message has been hidden in " + dirty_fname + line_end
    assert compare_images(CLEAN_PNG_LOCATION, dirty_fname) < 500
    try:
        Image.open(dirty_fname)
    except OSError:
        pytest.fail("Image is corrupt " + dirty_fname)

    os.remove(dirty_fname)


def test_main_hide_file_with_output(capfd):
    """Command line calls to hide work when given an input image, a file to hide, and an output file."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    file_to_hide = "tests/FileToHide.zip"
    dirty_fname = "tests/dirtyImage_test_main_hide_file_with_output.png"

    result = os.system('python -m steganographer ' + CLEAN_PNG_LOCATION + ' -f "' + file_to_hide +
                       '" -o ' + dirty_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == "The file " + file_to_hide + " has been hidden in " + dirty_fname + line_end
    assert compare_images(CLEAN_PNG_LOCATION, dirty_fname) < 19000
    try:
        Image.open(dirty_fname)
    except OSError:
        pytest.fail("Image is corrupt " + dirty_fname)

    os.remove(dirty_fname)


def test_main_hide_msg_no_output(capfd):
    """Command line calls to hide work when given an input image, a message, and no output file."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_main_hide_msg_no_output hidden message'
    clean_image = copy2(CLEAN_PNG_LOCATION, CLEAN_PNG_LOCATION[:-4] + "test_main_hide_msg_no_output.png")
    steganogrified_fname = clean_image[:-4] + "Steganogrified.png"

    result = os.system('python -m steganographer ' + clean_image + ' -m "' + hidden_message + '"')
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == "The message has been hidden in " + steganogrified_fname + line_end
    assert compare_images(clean_image, steganogrified_fname) < 500
    try:
        Image.open(steganogrified_fname)
    except OSError:
        pytest.fail("Image is corrupt " + steganogrified_fname)

    os.remove(clean_image)
    os.remove(steganogrified_fname)


def test_main_hide_file_no_output(capfd):
    """Command line calls to hide work when given an input image, a file to hide, and no output file."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    file_to_hide = "tests/FileToHide.zip"
    clean_image = copy2(CLEAN_PNG_LOCATION, CLEAN_PNG_LOCATION[:-4] + "test_main_hide_file_no_output.png")
    steganogrified_fname = clean_image[:-4] + "Steganogrified.png"

    result = os.system('python -m steganographer ' + clean_image + ' -f "' + file_to_hide + '"')
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == "The file " + file_to_hide + " has been hidden in " + steganogrified_fname + line_end
    assert compare_images(clean_image, steganogrified_fname) < 19000
    try:
        Image.open(steganogrified_fname)
    except OSError:
        pytest.fail("Image is corrupt " + steganogrified_fname)

    os.remove(clean_image)
    os.remove(steganogrified_fname)


def test_main_reveal_msg_no_output(capfd):
    """Command line calls to reveal work when given an input image, and no output file."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_main_reveal_msg_no_output hidden message'
    dirty_fname = "tests/dirtyImage_test_main_reveal_msg_no_output.png"

    os.system('python -m steganographer ' + CLEAN_PNG_LOCATION + ' -m "' + hidden_message +
              '" -o ' + dirty_fname)
    _, _ = capfd.readouterr()

    result = os.system("python -m steganographer " + dirty_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == ("The hidden message was..." + line_end + hidden_message + line_end)

    os.remove(dirty_fname)


def test_main_reveal_file_no_output(capfd):
    """Command line calls to reveal work when given an input image, the reveal file flag, and no output file."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    file_to_hide = "tests/FileToHide.zip"
    dirty_fname = "tests/dirtyImage_test_main_reveal_file_no_output.png"
    generated_output_file = file_to_hide

    os.system('python -m steganographer ' + CLEAN_PNG_LOCATION + ' -f "' + file_to_hide +
              '" -o ' + dirty_fname)
    _, _ = capfd.readouterr()

    result = os.system("python -m steganographer -r " + dirty_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == ("The hidden file was revealed in " + generated_output_file + line_end)

    os.remove(dirty_fname)


def test_main_reveal_msg_w_output(capfd):
    """Command line calls to reveal work when given an input image, and an output file."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_main_reveal_msg_w_output hidden message'
    dirty_fname = "tests/dirtyImage_test_main_reveal_msg_w_output.png"
    output_fname = "tests/outputMessage.txt"

    os.system('python -m steganographer ' + CLEAN_PNG_LOCATION + ' -m "' + hidden_message +
              '" -o ' + dirty_fname)
    _, _ = capfd.readouterr()

    result = os.system("python -m steganographer " + dirty_fname + " -o " + output_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    with open(output_fname, 'r') as output:
        assert output.read() == hidden_message

    assert out == ("The hidden message was written to " + output_fname + line_end)

    os.remove(dirty_fname)


def test_main_reveal_file_w_output(capfd):
    """Command line calls to reveal work when given an input image, a reveal file flag, and an output image."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    file_to_hide = "tests/FileToHide.zip"
    dirty_fname = "tests/dirtyImage_test_main_reveal_file_w_output.png"
    output_fname = "tests/outputFile.zip"

    os.system('python -m steganographer ' + CLEAN_PNG_LOCATION + ' -f "' + file_to_hide +
              '" -o ' + dirty_fname)
    _, _ = capfd.readouterr()

    result = os.system("python -m steganographer " + dirty_fname + " -r -o " + output_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    with open(output_fname, 'rb') as output, open(file_to_hide, 'rb') as original_file:
        assert output.read() == original_file.read()

    assert out == ("The hidden file was revealed in " + output_fname + line_end)

    os.remove(dirty_fname)


def test_main_reveal_no_msg(capfd):
    """There should be an error returned when there is no message hidden in the image file."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    clean_fname = "tests/cleanImage.jpg"

    result = os.system("python -m steganographer " + clean_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == "This file %s has no hidden message." % clean_fname + line_end


def test_main_reveal_no_op_unicode(capfd):
    """Command line calls to reveal work when the hidden message contains high value unicode."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_main_reveal_no_op_unicode hidden message, Unicode characters: 𓁈 ᾨ ԅ Թ ػ ޗ ߚ ङ ლ ጩ Ꮬ'
    dirty_fname = "tests/dirtyImage_test_main_reveal_no_op_unicode.png"
    output_fname = "tests/dirtyImage_test_main_reveal_no_op_unicode_message.txt"

    os.system('python -m steganographer ' + CLEAN_PNG_LOCATION + ' -m "' + hidden_message +
              '" -o ' + dirty_fname)
    _, _ = capfd.readouterr()

    result = os.system("python -m steganographer " + dirty_fname)
    out, _ = capfd.readouterr()

    assert result == 0
    if os.path.isfile(output_fname):
        with open(output_fname, 'r', encoding='utf-8') as output:
            assert output.read() == hidden_message

    assert (out == ("The hidden message contains unsupported unicode characters and cannot be fully displayed " +
                    "here. The correct message has been written to " + output_fname + line_end +
                    str(hidden_message.encode('utf-8')) + line_end)
            or out == ("The hidden message was..." + line_end + hidden_message + line_end))

    os.remove(dirty_fname)
    if os.path.isfile(output_fname):
        os.remove(output_fname)


def test_jpegs(capfd):
    """Jpegs can have a message hidden and revealed. Note they are converted to png."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_jpeg hidden message'
    dirty_fname = "tests/dirtyImage_test_jpegs"

    result = os.system('python -m steganographer tests/cleanImage.jpg -m "' + hidden_message +
                       '" -o ' + dirty_fname + '.jpg')
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == ("The message has been hidden in " + dirty_fname + '.png' + line_end)

    result = os.system("python -m steganographer " + dirty_fname + '.png')
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == ("The hidden message was..." + line_end + hidden_message + line_end)
    assert compare_images("tests/cleanImage.jpg", dirty_fname + '.png') < 500


@pytest.mark.xfail(strict=True, reason="Issue #59 bmp support is broken.", run=True)
def test_bmps(capfd):
    """Bmps can have a message hidden and revealed."""
    line_end = '\n'
    if sys.platform == 'win32':
        line_end = '\r\n'
    hidden_message = 'test_bmps hidden message'
    dirty_fname = "tests/dirtyImage_test_bmps"

    result = os.system('python -m steganographer tests/cleanImage.bmp -m "' + hidden_message +
                       '" -o ' + dirty_fname + '.bmp')
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == ("The message has been hidden in " + dirty_fname + '.png' + line_end)

    result = os.system("python -m steganographer " + dirty_fname + '.png')
    out, _ = capfd.readouterr()

    assert result == 0
    assert out == ("The hidden message was..." + line_end + hidden_message + line_end)
    assert compare_images("tests/cleanImage.bmp", dirty_fname + '.png') < 500
