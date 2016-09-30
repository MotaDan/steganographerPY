"""The main routine."""
import argparse
from steganographer.steganographer import steganographer_hide, steganographer_reveal


def main():
    """The main routine."""
    parser = argparse.ArgumentParser(description="hides a message in a file or returns a message hidden in a file")
    parser.add_argument("input", help="file to hide a message in or file to reveal a message from")
    parser.add_argument("-m", "--message", help="message to be hidden in the input file")
    parser.add_argument("-o", "--output",
                        help="name of output file to hide message in or to write revealed message.")
    args = parser.parse_args()

    if args.input:
        if args.message:
            if args.output:
                hidden_fname = steganographer_hide(args.input, args.message, args.output)
            else:
                hidden_fname = steganographer_hide(args.input, args.message)
            print("The message has been hidden in " + hidden_fname)
        else:
            hidden_message = steganographer_reveal(args.input)

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
