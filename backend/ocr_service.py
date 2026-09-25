import pytesseract
import pymupdf
from PIL import Image
import io

# Tell Python exactly where Tesseract is installed
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_pdf(file_path: str) -> str:
    document = pymupdf.open(file_path)

    all_text = []

    for page_number, page in enumerate(document):
        print(f"Processing page {page_number + 1}...")

        # Convert PDF page to image
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))

        image_bytes = pix.tobytes("png")

        image = Image.open(io.BytesIO(image_bytes))

        # OCR
        text = pytesseract.image_to_string(image)

        all_text.append(text)

    document.close()

    return "\n".join(all_text)


def extract_text_from_image(file_path: str) -> str:
    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return text