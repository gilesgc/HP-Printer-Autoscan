from HPPrinter import HPPrinter
from datetime import datetime

def main():
    printer_ip = input("Please enter the internal IP of your printer: ")
    printer = HPPrinter(printer_ip)
    start_scan(printer)

def start_scan(printer):
    input("\nPress enter to begin scanning")
    image = printer.scan()

    fileformat = get_choice("\nWhich document format would you like?", ["PDF", "JPG", "Both"])

    extension = ".pdf" if fileformat == "PDF" else ".jpg"
    filename = datetime.now().strftime("%Y-%m-%d--%I-%M-%p")

    print(f"Saving as \"{filename}{extension}\" in the script directory")
    image.save(f"{filename}{extension}")

    if fileformat == "Both":
        extension = ".pdf"
        print(f"\nSaving as \"{filename}{extension}\" in the script directory")
        image.save(f"{filename}{extension}")

    again = get_choice("\nWould you like to scan again?", ["Y", "N"])
    if again == "Y":
        start_scan(printer)

def get_choice(question, choices):
    result = None
    while result not in choices:
        result = input(question + " " + str(choices).replace("'", "").strip() + " ")
    return result

if __name__ == "__main__":
    main()