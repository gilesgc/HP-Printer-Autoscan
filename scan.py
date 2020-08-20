from HPPrinter import HPPrinter
from datetime import datetime
from argparse import ArgumentParser

def main():
    args = parse_args()
    printer_ip = args.ip_address if args.ip_address is not None else input("Please enter the internal IP of your printer: ")
    printer = HPPrinter(printer_ip)
    start_scan(printer, args.skip_confirm, args.doc_type.lower(), args.ask_again)

def parse_args():
    parser = ArgumentParser(description='Scan the document in the scanner glass of your HP printer')
    parser.add_argument('--ip-address', '-i', type=str, help="The printer's internal IP address")
    parser.add_argument('--skip-confirm', '-s', type=int, nargs='?', const=1, default=0, help="Skip the 'Press enter to ...' confirmations")
    parser.add_argument('--doc-type', '-d', type=str, default="", help="The document type. Accepted options: [pdf, jpg, both]")
    parser.add_argument('--ask-again', '-a', type=int, nargs='?', const=1, default=0, help="Ask if another document should be scanned after completion.")
    return parser.parse_args()

def start_scan(printer, skip_confirm, doc_type, ask_again):
    if not skip_confirm:
        input("\nPress enter to begin scanning")
    image = printer.scan()

    if doc_type in ["pdf", "jpg", "both"]:
        fileformat = doc_type
    else:
        fileformat = get_choice("\nWhich document format would you like?", ["pdf", "jpg", "both"])

    extension = ".pdf" if fileformat == "pdf" else ".jpg"
    filename = datetime.now().strftime("%Y-%m-%d--%I-%M-%p")

    print(f"Saving as \"{filename}{extension}\" in the script directory")
    image.save(f"{filename}{extension}")

    if fileformat == "both":
        extension = ".pdf"
        print(f"\nSaving as \"{filename}{extension}\" in the script directory")
        image.save(f"{filename}{extension}")

    if ask_again:
        again = get_choice("\nWould you like to scan again?", ["y", "n"])
        if again == "y":
            start_scan(printer, skip_confirm, doc_type, ask_again)

def get_choice(question, choices):
    result = None
    while result not in choices:
        result = input(question + " " + str(choices).replace("'", "").strip() + " ")
    return result

if __name__ == "__main__":
    main()