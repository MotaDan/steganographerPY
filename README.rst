==============
steganographer
==============
.. image:: https://travis-ci.org/MotaDan/steganographerPY.svg?branch=master
   :target: https://travis-ci.org/MotaDan/steganographerPY
.. image:: https://coveralls.io/repos/github/MotaDan/steganographerPY/badge.svg?branch=master
   :target: https://coveralls.io/github/MotaDan/steganographerPY?branch=master
.. image:: https://landscape.io/github/MotaDan/steganographerPY/master/landscape.svg?style=flat
   :target: https://landscape.io/github/MotaDan/steganographerPY/master
   :alt: Code Health
.. image:: https://readthedocs.org/projects/steganographer/badge/?version=latest
   :target: http://steganographer.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


Hide messages and files inside an image. 

https://pypi.python.org/pypi/steganographer


Description
-----------

Given an image and a message or a file, steganographer will hide the message or file in the bits of the image. Works best when PNGs are passed in. Will convert JPGs to PNGs because of compression. Only tested with png and jpg.

Compatiable with python 3 and up.

Install:
--------
pip install steganographer

Usage:
------
Hide a message in an image.

- steganographer inputImage.png -m "Message to hide."
- steganographer inputImage.png -m "Message to hide." -o outputImage.png

Reveal a hidden message.

- steganographer inputImage.png
- steganographer inputImage.png -o revealedMessage.txt

Hide a file in an image.

- steganographer inputImage.png -f fileToHide.zip
- steganographer inputImage.png -f fileToHide.zip -o fileHiddenImage.png

Reveal a file in an image.

- steganographer inputImage.png -r
- steganographer inputImage.png -r -o revealedFile.zip


Development Notes:
------------------
After cloning have pip-tools installed and run this command to get the correct requirements.

- pip-sync dev-requirements.txt requirements.txt test-requirements.txt

Adding project site
