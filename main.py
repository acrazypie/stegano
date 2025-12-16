import argparse
import sys
import getpass

from api.lsb import decode_image_to_file, encode_file_into_image


def main():
    parser = argparse.ArgumentParser(
        description="Steganography tool - encode/decode files in images using LSB"
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Encode subcommand
    encode_parser = subparsers.add_parser("encode", help="Encode a file into an image")
    encode_parser.add_argument("input_file", help="File to hide")
    encode_parser.add_argument("cover_image", help="Cover image file")
    encode_parser.add_argument("output_image", help="Output image with hidden data")
    encode_parser.add_argument("-p", "--password", help="Optional password for encryption")

    # Decode subcommand
    decode_parser = subparsers.add_parser("decode", help="Decode a file from an image")
    decode_parser.add_argument("input_image", help="Image containing hidden data")
    decode_parser.add_argument(
        "output_path", help="Output path or directory for extracted file"
    )
    decode_parser.add_argument("-p", "--password", help="Optional password for decryption")

    args = parser.parse_args()

    try:
        if args.command == "encode":
            print(f"Encoding '{args.input_file}' into '{args.cover_image}'...")
            encode_file_into_image(args.input_file, args.cover_image, args.output_image, args.password)
            encryption_status = " (encrypted)" if args.password else ""
            print(f"Successfully encoded to '{args.output_image}'{encryption_status}")

        elif args.command == "decode":
            print(f"Decoding from '{args.input_image}'...")
            output_path = decode_image_to_file(args.input_image, args.output_path, args.password)
            decryption_status = " (decrypted)" if args.password else ""
            print(f"Successfully decoded to '{output_path}'{decryption_status}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
