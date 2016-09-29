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
					help="name of output file to hide message in or to write revealed message.")
	args = parser.parse_args()
	
	if args.input:
		if args.message:
			hiddenFname = ''
			if args.output:
				hiddenFname = steganographerHide(args.input, args.message, args.output)
			else:
				hiddenFname = steganographerHide(args.input, args.message)
			print("The message has been hidden in " + hiddenFname)
		else:
			hiddenMessage = steganographerReveal(args.input)
			
			if args.output:
				open(args.output, 'w', encoding='utf-8').write(hiddenMessage)
				print("The hidden message was written to " + args.output)
			else:
				try:
					print("The hidden message was...\n" + hiddenMessage)
				except UnicodeEncodeError: # pragma: no cover
					ofName = args.input.split('.')[0] + 'Message.txt'
					
					print("The hidden message contains unsupported unicode characters and cannot be fully displayed " +
							"here. The correct message has been written to", ofName)
					print(hiddenMessage.encode('utf-8'))
					open(ofName, 'w', encoding='utf-8').write(hiddenMessage)

if __name__ == "__main__":
	main()
