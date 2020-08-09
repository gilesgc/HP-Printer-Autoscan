from requests import Session, get
import logging
from PIL import Image
from io import BytesIO
from threading import Thread
import sys
from time import sleep

class HPPrinter(Session):
    def __init__(self, printer_internal_ip):
        super().__init__()

        self.internal_ip = printer_internal_ip
        self.base_url = f"http://{printer_internal_ip}/"
        self.base_headers = {
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'must-revalidate, no-cache',
            'Accept': 'text/xml',
            'Host': printer_internal_ip,
            'Connection': 'Keep-Alive',
            'User-Agent': None
        }

        logging.basicConfig(level=logging.INFO, format='[%(module)s] %(message)s')
        self.logger = logging.getLogger(__name__)

        try:
            self.printer_request("GET", "eSCL/eSclManifest.xml")
        except:
            raise Exception("Could not connect to printer. The wrong IP may have been used or this printer uses an unsupported API.")

        self.logger.info("Printer initialized.")

    def printer_request(self, method, endpoint, headers=None, data=None):
        return self.request(method, self.base_url + endpoint, headers=headers, data=data)

    def scan(self) -> Image:
        payload = """<?xml version="1.0" encoding="utf-8"?><escl:ScanSettings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm" xmlns:escl="http://schemas.hp.com/imaging/escl/2011/05/03"><pwg:Version>2.63</pwg:Version><escl:Intent>Document</escl:Intent><pwg:ScanRegions pwg:MustHonor="false"><pwg:ScanRegion><pwg:Height>3300</pwg:Height><pwg:ContentRegionUnits>escl:ThreeHundredthsOfInches</pwg:ContentRegionUnits><pwg:Width>2550</pwg:Width><pwg:XOffset>0</pwg:XOffset><pwg:YOffset>0</pwg:YOffset></pwg:ScanRegion></pwg:ScanRegions><escl:DocumentFormatExt>image/jpeg</escl:DocumentFormatExt><pwg:InputSource>Platen</pwg:InputSource><escl:XResolution>600</escl:XResolution><escl:YResolution>600</escl:YResolution><escl:ColorMode>Grayscale8</escl:ColorMode></escl:ScanSettings>"""
        headers = {
            'Content-Length': str(len(payload)),
            'Content-Type': 'text/xml; charset=utf-8'
        }.update(self.base_headers)

        self.logger.info("Checking if printer is busy...")
        scanjobs = self.printer_request("POST", "eSCL/ScanJobs", headers=headers, data=payload)

        if scanjobs.ok and 'Location' in scanjobs.headers:
            self.logger.info("Printer is ready.")
        else:
            raise Exception("The printer is busy.")

        scanurl = scanjobs.headers["Location"] + "/NextDocument"

        sc = ScanningAnimator()
        sc.start()
        result = get(scanurl, headers=headers)
        sc.stop()

        self.logger.info("Scan complete!")
        return Image.open(BytesIO(result.content))

class ScanningAnimator(Thread):
    def __init__(self):
        super().__init__()
        self.running = False

    def stop(self):
        self.running = False
        sleep(0.5)
        print("")

    def _icon_generator(self):
        icons = ["-", "\\", "|", "/"]
        index = 0
        while True:
            yield icons[index % len(icons)]
            index += 1

    def run(self):
        self.running = True
        gen = self._icon_generator()
        print("")
        while self.running:
            sys.stdout.write(f"\r[HPPrinter] Scanning... {next(gen)} ")
            sys.stdout.flush()
            sleep(0.1)