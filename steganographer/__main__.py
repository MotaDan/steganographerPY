"""The main routine."""
import argparse
from steganographer.steganographer import Steganographer


def main():
    """The main routine."""
    parser = argparse.ArgumentParser(description="hides a message in a file or returns a message hidden in a file")
    parser.add_argument("input", help="file to hide a message in or file to reveal a message from")
    parser.add_argument("-m", "--message", help="message to be hidden in the input file")
    parser.add_argument("-o", "--output",
                        help="name of output file to hide message in or to write revealed message")
    parser.add_argument("-f", "--file", help="file to be hidden in the input file")
    parser.add_argument("-r", "--reveal", action='store_true', help="a file will be revealed")
    args = parser.parse_args()

    stegs = Steganographer()

    if args.input:
        # There is a message to hide.
        if args.message:
            if args.output:
                hidden_fname = stegs.steganographer_hide(args.input, args.message, args.output)
            else:
                hidden_fname = stegs.steganographer_hide(args.input, args.message)
            print("The message has been hidden in " + hidden_fname)
        # There is a file to hide.
        elif args.file:
            if args.output:
                hidden_fname = stegs.steganographer_hide_file(args.input, args.file, args.output)
            else:
                hidden_fname = stegs.steganographer_hide_file(args.input, args.file)
            print("The file " + args.file + " has been hidden in " + hidden_fname)
        # Revealing a file.
        elif args.reveal:
            if args.output:
                revealed_data = stegs.steganographer_reveal_file(args.input)

                with open(args.output, 'wb') as rFile:
                    rFile.write(revealed_data)
                print("The hidden file was revealed in " + args.output)
            else:
                fileName = "steganographer_revealed_file.txt"
                revealed_data = stegs.steganographer_reveal_file(args.input)

                with open(fileName, 'wb') as rFile:
                    rFile.write(revealed_data)
                print("The hidden file was revealed in " + fileName)
        # Revealing a message.
        else:
            hidden_message = stegs.steganographer_reveal(args.input)

            if args.output:
                open(args.output, 'w', encoding='utf-8').write(hidden_message)
                print("The hidden message was written to " + args.output)
            else:
                try:
                    print("The hidden message was...\n" + hidden_message)
                except UnicodeEncodeError:  # pragma: no cover
                    output_name = args.input.split('.')[0] + '_message.txt'

                    print("The hidden message contains unsupported unicode characters and cannot be fully displayed " +
                          "here. The correct message has been written to", output_name)
                    print(hidden_message.encode('utf-8'))
                    open(output_name, 'w', encoding='utf-8').write(hidden_message)


if __name__ == "__main__":
    main()
