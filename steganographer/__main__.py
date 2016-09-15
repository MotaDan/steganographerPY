"""The main routine."""
import sys
import argparse
from steganographer.steganographer import steganographerHide, steganographerReveal

def main(args=None):
	"""The main routine."""
	if args is None:
		args = sys.argv[1:]

	parser = argparse.ArgumentParser(description="hides a message in a file or returns a message hidden in a file")
	parser.add_argument("input", help="file to hide a message in or file to reveal a message from")
	parser.add_argument("-m", "--message", help="message to be hidden in the input file")
	parser.add_argument("-o", "--output", 
						help="name of output file to hide message in. If not given will append Steganogrified to input name.")
	args = parser.parse_args()
	
	if args.input:
		if args.message:
			if args.output:
				steganographerHide(args.input, args.message, args.output)
			else:
				steganographerHide(args.input, args.message)
			print("The message has been hidden.")
		else:
			hiddenMessage = steganographerReveal(args.input)
			print("The hidden message was...")
			print(hiddenMessage)

if __name__ == "__main__":
	main()