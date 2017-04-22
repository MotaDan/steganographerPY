"""Given an image and a message or file steganographer will hide the message or file in the bits of the image."""
from PIL import Image
import sys
import os.path


def _unpack_image(pixels):
    """Flatten out pixels and returns a tuple. The first entry is the size of each pixel."""
    unpacked_pixels = []

    try:
        for pix in pixels:
            for val in pix:
                unpacked_pixels.append(val)

        return len(pixels[0]), bytes(unpacked_pixels)
    except TypeError:
        return 1, bytes(pixels)


def _pack_image(pixels):
    """Do create 2d list of pixels and return the list."""
    packed_pixels = []
    pixel_length = pixels[0]

    for i in range(0, len(pixels[1]), pixel_length):
        packed_pixels.append(tuple(pixels[1][i:i + pixel_length]))

    return packed_pixels


def _open_bin_file(fname):
    """Reads the file fname and returns bytes for all of its data."""
    try:
        with open(fname, 'rb') as fimage:
            image_bytes = fimage.read()

        return image_bytes

    except FileNotFoundError:
        print("Could not find file", fname)
        sys.exit()


def _write_bin_file(fname, data):
    """Create a file fname and writes the passed in data to it."""
    try:
        with open(fname, 'wb') as fdirty:
            fdirty.write(data)

    except IOError:  # pragma: no cover
        print("Could not create file", fname)
        sys.exit()


def _open_image_file(fname):
    """Reads the file fname and returns bytes for all it's data."""
    try:
        with Image.open(fname) as img:
            pixels = list(img.getdata())
            return _unpack_image(pixels)

    except FileNotFoundError:
        print("Could not read file", fname)
        sys.exit()


def _write_image_file(fname, og_fname, data):
    """Create a image fname and writes the passed in data to it. Returns name of image created."""
    try:
        with Image.open(og_fname) as ogim:
            img = Image.new(ogim.mode, ogim.size)
            img.putdata(_pack_image(data))
            fname_no_ext, _ = os.path.splitext(fname)
            img.save(fname_no_ext + '.png', 'png')
            return fname_no_ext + '.png'

    except FileNotFoundError:
        print("Could not read file", og_fname)
        sys.exit()


class Header:

    """The header that is stored at the beginning of steganogrified images."""

    _HEADER_TITLE = "STEGS"
    _HEADER_DATA_SIZE = 10  # The size of the data segment in the header.
    _HEADER_BITS_SIZE = 1  # The size of the header segment for storing the number of bits from a byte used.
    _HEADER_FILE_LENGTH_SIZE = 2  # The size of the header segment for storing the file length.

    def __init__(self, data_len=0, bits_used=1, file_name=""):
        self.title = self._HEADER_TITLE
        self.data_len = data_len
        self.bits_used = bits_used
        self.file_name_len = len(file_name)
        self.file_name = file_name

    @property
    def header_length(self):
        """Returns the length of the header data."""
        length = len(self._HEADER_TITLE) + self._HEADER_DATA_SIZE + self._HEADER_BITS_SIZE + \
            self._HEADER_FILE_LENGTH_SIZE + self.file_name_len

        return length

    @property
    def header_as_bytes(self):
        """Converts the header into a bytes object."""
        header = bytes(self._HEADER_TITLE, 'utf-8') + \
            bytes(self.data_len.to_bytes(self._HEADER_DATA_SIZE, "little")) + \
            bytes(self.bits_used.to_bytes(self._HEADER_BITS_SIZE, "little")) + \
            bytes(self.file_name_len.to_bytes(self._HEADER_FILE_LENGTH_SIZE, "little")) + \
            bytes(self.file_name, 'utf-8')

        return header

    def retrieve_header(self, potential_header):
        """
        Retrieves the header from the data passed in and sets the appropriate attributes.

        Returns if there is a valid header or not.
        """
        header_title = potential_header[:len(self.title)]
        self.data_len = int.from_bytes(
            potential_header[len(self.title):len(self.title) + self._HEADER_DATA_SIZE], "little")
        self.bits_used = int.from_bytes(
            potential_header[len(self.title) + self._HEADER_DATA_SIZE:
                             len(self.title) + self._HEADER_DATA_SIZE + self._HEADER_BITS_SIZE], "little")
        self.file_name_len = int.from_bytes(
            potential_header[len(self.title) + self._HEADER_DATA_SIZE + self._HEADER_BITS_SIZE:
                             len(self.title) + self._HEADER_DATA_SIZE + self._HEADER_BITS_SIZE +
                             self._HEADER_FILE_LENGTH_SIZE], "little")
        self.file_name = potential_header[len(self.title) + self._HEADER_DATA_SIZE + self._HEADER_BITS_SIZE +
                                          self._HEADER_FILE_LENGTH_SIZE:
                                          len(self.title) + self._HEADER_DATA_SIZE + self._HEADER_BITS_SIZE +
                                          self._HEADER_FILE_LENGTH_SIZE + self.file_name_len]

        return header_title == self.title.encode('utf-8')


class Steganographer:

    """Takes care of hiding and revealing messages and files in an image."""

    _BYTELEN = 8
    _header = Header()

    def __init__(self):
        """Setting header data_len, so retrieving the header knows how much data to grab."""
        self._header.data_len = self._header.header_length  # The only data is the header.
        self._header.bits_used = 1

    def _generate_header(self, data_size, bits_to_use, file_name):
        """
        Generates the header that will be placed at the beginning of the image.

        Returns header as bytes.
        """
        self._header = Header(data_size, bits_to_use, file_name)

        return self._header.header_as_bytes

    def _retrieve_header(self, data):
        """
        Retrieves the header from the data passed in and sets the appropriate attributes.

        Returns if there is a valid header or not.
        """
        bytes_to_hide_header = self._header.header_length * self._BYTELEN
        self._header.data_len = bytes_to_hide_header  # The only data is the header.
        header_as_bytes = self._reveal_data(data[:bytes_to_hide_header])
        is_header_valid = self._header.retrieve_header(header_as_bytes)

        # Getting the file name if one exist and updating the header.
        if self._header.file_name_len > 0:
            bytes_to_hide_header = self._header.header_length * self._BYTELEN
            self._header.data_len = bytes_to_hide_header  # The only data is the header.
            header_as_bytes = self._reveal_data(data[:bytes_to_hide_header])
            is_header_valid = self._header.retrieve_header(header_as_bytes)

        return is_header_valid

    def _hide_byte(self, clean_data, val):
        """
        Hides a byte val in clean_data. Returns bytes.

        Expects a bytes of length 8 and a character value. Will return a bytes with the character's bits hidden
        in the least significant bits of clean_data.
        """
        hidden_data = bytearray(len(clean_data))
        mask = 1 << (self._BYTELEN - 1)

        for i in range(len(hidden_data)):
            masked_bit = val & (mask >> i)

            if masked_bit > 0:
                masked_bit >>= self._BYTELEN - 1 - i
                hidden_data[i] = clean_data[i] | masked_bit
            else:
                masked_bit = ~(mask >> (self._BYTELEN - 1))
                hidden_data[i] = clean_data[i] & masked_bit

        return bytes(hidden_data)

    def _reveal_byte(self, hidden_data):
        """Expects a bytes of length 8. Will pull out the least significant bit from each byte and return them."""
        if len(hidden_data) == 0:
            return bytes()

        revealed_data = bytearray(1)

        for i in range(len(hidden_data)):
            least_sig_bit = hidden_data[i] & 1
            revealed_data[0] |= least_sig_bit << (self._BYTELEN - 1 - i)

        return bytes(revealed_data)

    def _hide_string(self, clean_data, val):
        """
        Hides a string val in clean_data. Returns a bytes.

        Expects a bytes of any length and a string value. Will return a bytes with the string's bits hidden
        in the least significant bits.
        """
        return self._hide_data(clean_data, bytes(val, 'utf-8'))

    def _reveal_string(self, hidden_data):
        """
        Returns a string hidden in hidden_data.

        Expects a bytes of any length. Will pull out the least significant bits from each byte and return them as
        a string.
        """
        revealed_data = self._reveal_data(hidden_data)

        try:
            revealed_string = revealed_data.decode('utf-8')
        except UnicodeDecodeError:  # pragma: no cover
            print("The hidden message could not be decoded.")
            sys.exit()

        return revealed_string

    def _hide_data(self, clean_data, val):
        """
        Hides val inside clean_data. Returns a bytes.

        Expects a bytes clean_data of any length and another bytes val. Will return a bytes with the val's
        bits hidden in the least significant bits of clean_data.
        """
        hidden_data = bytearray()

        for data_index, str_index in zip(range(0, len(clean_data), self._BYTELEN), range(len(val))):
            clean_byte = clean_data[data_index:data_index + self._BYTELEN]
            hidden_byte = self._hide_byte(clean_byte, val[str_index])
            hidden_data.extend(hidden_byte)

        hidden_data = hidden_data + clean_data[len(hidden_data):]

        return bytes(hidden_data)

    def _reveal_data(self, hidden_data):
        """
        Returns the data hidden in hidden_data.

        Expects a bytes hidden_data of any length. Will pull out the least significant bits from each byte and
        return them as a bytes.
        """
        revealed_data_len = self._header.data_len
        revealed_data = bytearray()

        for i in range(0, revealed_data_len * self._BYTELEN, self._BYTELEN):
            revealed_data.extend(self._reveal_byte(hidden_data[i:i + self._BYTELEN]))

        return bytes(revealed_data)

    def steganographer_hide(self, clean_image_file, text, dirty_image_file=''):
        """
        Hides text inside clean_image_file and outputs dirty_image_file.

        Takes in a clean image file name, a dirty image file name and text that will be hidden. Hides the text in
        clean_image_file and outputs it to dirty_image_file.
        """
        header = self._generate_header(len(text.encode('utf-8')), 1, "")
        clean_data = _open_image_file(clean_image_file)  # Is a tuple with the size of a pixel and the pixels.
        dirty_data = self._hide_data(clean_data[1][:len(header) * self._BYTELEN], header)
        dirty_data += self._hide_string(clean_data[1][len(header) * self._BYTELEN:], text)
        dirty_image_data = (clean_data[0], dirty_data)

        if dirty_image_file == '':
            clean_name = clean_image_file.split('.')[0]
            clean_extension = clean_image_file.split('.')[1]
            dirty_image_file = clean_name + "Steganogrified." + clean_extension

        output_file = _write_image_file(dirty_image_file, clean_image_file, dirty_image_data)

        return output_file

    def steganographer_hide_file(self, clean_image_file, file_to_hide, dirty_image_file=''):
        """Hides file_to_hide inside clean_image_file and outputs to dirty_image_file."""
        with open(file_to_hide, 'rb') as input_file:
            header = self._generate_header(len(input_file.read()), 1, file_to_hide)
            input_file.seek(0)
            clean_data = _open_image_file(clean_image_file)  # Is a tuple with the size of a pixel and the pixels.
            dirty_data = self._hide_data(clean_data[1][:self._header.header_length * self._BYTELEN], header)
            dirty_data += self._hide_data(clean_data[1][self._header.header_length * self._BYTELEN:], input_file.read())
            dirty_image_data = (clean_data[0], dirty_data)

        if dirty_image_file == '':
            clean_name = clean_image_file.split('.')[0]
            clean_extension = clean_image_file.split('.')[1]
            dirty_image_file = clean_name + "Steganogrified." + clean_extension

        output_file = _write_image_file(dirty_image_file, clean_image_file, dirty_image_data)

        return output_file

    def steganographer_reveal(self, fimage):
        """Reveals whatever data is hidden in the fimage file least significant bits."""
        dirty_data = _open_image_file(fimage)

        if self._retrieve_header(dirty_data[1]) is False:
            print("This file %s has no hidden message." % fimage)
            sys.exit()

        revealed_data = self._reveal_data(dirty_data[1][self._header.header_length * self._BYTELEN:])
        return revealed_data
