import fitz
import easyocr
import numpy as np

reader = easyocr.Reader(['en'])


def extract_pdf_text(pdf_path):

    text = ""

    pdf = fitz.open(pdf_path)

    for page in pdf:

        pix = page.get_pixmap(dpi=300)

        img = np.frombuffer(pix.samples, dtype=np.uint8)

        img = img.reshape(pix.height, pix.width, pix.n)

        result = reader.readtext(img, detail=0)

        text += "\n".join(result)
        text += "\n"

    pdf.close()

    return text