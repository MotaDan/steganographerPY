"""Given an image and a message steganographer will hide the message in the bits of the image."""
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
        fimage = open(fname, 'rb')
        image_bytes = fimage.read()

        return image_bytes

    except FileNotFoundError:
        print("Could not read file", fname)
        sys.exit()


def _write_bin_file(fname, data):
    """Create a file fname and writes the passed in data to it."""
    try:
        fdirty = open(fname, 'wb')
        fdirty.write(data)

    except IOError:  # pragma: no cover
        print("Could not create file", fname)
        sys.exit()


def _open_image_file(fname):
    """Reads the file fname and returns bytes for all it's data."""
    try:
        img = Image.open(fname)
        pixels = list(img.getdata())
        return _unpack_image(pixels)

    except FileNotFoundError:
        print("Could not read file", fname)
        sys.exit()


def _write_image_file(fname, og_fname, data):
    """Create a image fname and writes the passed in data to it. Returns name of image created."""
    try:
        ogim = Image.open(og_fname)
        img = Image.new(ogim.mode, ogim.size)
        img.putdata(_pack_image(data))
        fname_no_ext, _ = os.path.splitext(fname)
        img.save(fname_no_ext + '.png', 'png')
        return fname_no_ext + '.png'

    except FileNotFoundError:
        print("Could not read file", og_fname)
        sys.exit()


class Steganographer:

    """Takes care of hiding a revealing messages in images."""

    _BYTELEN = 8
    _HEADER_TITLE = "STEGS"
    _HEADER_DATA_SIZE = 10  # The size of the data segment in the header.
    _HEADER_SIZE = len(_HEADER_TITLE) + _HEADER_DATA_SIZE

    def _generate_header(self, data_size):
        self._HEADER = bytes(self._HEADER_TITLE, 'utf-8') + bytes(data_size.to_bytes(self._HEADER_DATA_SIZE, sys.byteorder))
        self._HEADER_SIZE = len(self._HEADER)

        return self._HEADER

    def _retrieve_header(self, data):
        bytes_to_hide_header = self._HEADER_SIZE * self._BYTELEN
        header = self._reveal_data(data[:bytes_to_hide_header])
        header_title = header[:len(self._HEADER_TITLE)]
        self._DATA_LEN = header[len(self._HEADER_TITLE):len(self._HEADER_TITLE) + self._HEADER_DATA_SIZE]

        return header_title == self._HEADER_TITLE

    def _hide_byte(self, clean_data, val):
        """
        Hides a byte val in data. Returns bytes.

        Expects a bytes of length 8 and a character value. Will return a bytes with the character's bits hidden
        in the least significant bit.
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
        revealed_data = bytearray(1)

        for i in range(len(hidden_data)):
            least_sig_bit = hidden_data[i] & 1
            revealed_data[0] |= least_sig_bit << (self._BYTELEN - 1 - i)

        return bytes(revealed_data)

    def _hide_string(self, clean_data, val):
        """
        Hides a string val in clean_data. Returns a bytes.

        Expects a bytes of any length and a string value. Will return a bytes with the string's bits hidden
        in the least significant bits. Adds null terminator to the end of the string.
        """
        #val += '\0'
        return self._hide_data(clean_data, bytes(val, 'utf-8'))

    def _reveal_string(self, hidden_data):
        """
        Returns a string hidden in hidden_data.

        Expects a bytes of any length. Will pull out the least significant bits from each byte and return them as
        a string.
        """
        revealed_data = self._reveal_data(hidden_data)
        # null_pos = 0
        #
        # for i in range(len(revealed_data)):
        #     if revealed_data[i] != 0:
        #         null_pos += 1
        #     else:
        #         break
        #
        # revealed_data = revealed_data[:null_pos]

        try:
            revealed_string = revealed_data.decode()
        except UnicodeDecodeError:
            print("There was a problem reading the hidden message.")
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
        revealed_data_len = self._DATA_LEN
        #revealed_data_len = len(hidden_data) // self._BYTELEN
        revealed_data = bytearray()

        for i in range(0, revealed_data_len * self._BYTELEN, self._BYTELEN):
            revealed_data.extend(self._reveal_byte(hidden_data[i:i + self._BYTELEN]))

        revealed_data_len_remainder = len(hidden_data) % self._BYTELEN

        if revealed_data_len_remainder > 0:
            revealed_data.extend(self._reveal_byte(hidden_data[-1 * revealed_data_len_remainder:]))

        return bytes(revealed_data)

    def steganographer_hide(self, clean_image_file, text, dirty_image_file=''):
        """
        Hides text inside CleanImageFile and outputs dirty_image_file.

        Takes in a clean image file name, a dirty image file name and text that will be hidden. Hides the text in
        clean_image_file and outputs it to dirty_image_file.
        """
        header = self._generate_header(len(text.encode('utf-8')))
        clean_data = _open_image_file(clean_image_file)  # Is a tuple with he size of pixels and the pixels.
        dirty_data = (clean_data[0], self._hide_string(clean_data[1], header.decode('utf-8') + text))

        if dirty_image_file == '':
            clean_name = clean_image_file.split('.')[0]
            clean_extension = clean_image_file.split('.')[1]
            dirty_image_file = clean_name + "Steganogrified." + clean_extension

        output_file = _write_image_file(dirty_image_file, clean_image_file, dirty_data)

        return output_file

    def steganographer_reveal(self, fimage):
        """Reveals whatever string is hidden in the fimage."""
        dirty_data = _open_image_file(fimage)

        if self._retrieve_header(dirty_data[1]) is False:
            return "This file %s has no hidden message.", fimage

        revealed_string = self._reveal_string(dirty_data[1][self._HEADER_SIZE * self._BYTELEN:])
        return revealed_string
