"""Given an image and a message steganographer will hide the message in the bits of the image."""
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except DistributionNotFound:
    __version__ = 'unknown'
