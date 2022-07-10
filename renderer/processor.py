from io import BytesIO

import fitz
from PIL import Image


class Processor:
    @staticmethod
    def load_pdf(raw_data: bytes) -> fitz.Document:
        """Check if the file is PDF and return a document for further processing."""
        if not isinstance(raw_data, bytes):
            raise ValueError("input data is not bytes")

        try:
            doc = fitz.open(stream=raw_data, filetype="pdf")
        except (fitz.fitz.FileDataError, TypeError, fitz.fitz.EmptyFileError) as e:
            raise ValueError("input data is invalid") from e

        if "pdf" not in doc.metadata["format"].lower():
            raise ValueError("input data is not pdf")

        return doc

    @staticmethod
    def get_page_count(document: fitz.Document) -> int:
        return document.page_count

    @staticmethod
    def convert_page_to_image(
        page: fitz.Page, dpi: int, width: int, height: int
    ) -> bytes:
        pix = page.get_pixmap(dpi=dpi)
        pix = pix.tobytes()
        img = Image.open(BytesIO(pix))
        img = img.resize((width, height))

        out_img = BytesIO()
        img.save(out_img, format="png")
        out_img.seek(0)

        return out_img
