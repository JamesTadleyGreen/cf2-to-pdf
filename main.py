from os import path
import os

from cf2 import parse_cf2, CF2, LineType
from pdf import create_pdf


def create_pdf_from_cf2(cf2_file: path, pdf_file: path, verbose: bool = False) -> None:
    with open(cf2_file, "r") as f:
        cf2 = parse_cf2(f.read())
        if verbose:
            print(cf2.parameters)
        create_pdf(pdf_file, cf2)


if __name__ == "__main__":
    cf2s = [file[:-4] for file in os.listdir("./cf2s")]
    for cf2 in cf2s:
        c = parse_cf2(f"./cf2s/{cf2}.cf2")
        c.add_line(5, LineType.CREASE, (300, 300), (1000, 1000), 0, 0)
        create_pdf("./388964@M&S@@Star Shaped Postcard@210@148@Sheetwise.pdf", c)
        c.write(f"./cf2s/{cf2} 1.cf2")
