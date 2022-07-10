import hashlib
import time

import fitz
import structlog

from renderer.database.models import DocumentStatus

from .clients.s3 import S3Client
from .database.repositories import DocumentRepository
from .processor import Processor
from .settings import PDF_FILE_NAME, ImageSettings

log = structlog.get_logger(__name__)


class Core:
    def __init__(
        self,
        document_repository: DocumentRepository,
        processor: Processor,
        s3_client: S3Client,
        image_settings: ImageSettings,
    ) -> None:
        self.processor = processor
        self.document_repository = document_repository
        self.s3_client = s3_client
        self.image_settings = image_settings

    def handle_input_data(self, raw_data: bytes, document: fitz.Document):
        status = DocumentStatus.processing
        page_count = self.processor.get_page_count(document)
        input_hash = hashlib.sha1(raw_data).hexdigest()  # nosec
        document_id = self.document_repository.add(status, page_count, input_hash)
        self.save_pdf_file(document_id, raw_data)

        return {
            "document_id": document_id,
            "status": status.name,
            "page_count": page_count,
            "input_hash": input_hash,
        }

    def convert_document_to_images(
        self, raw_data: bytes, document_id: int
    ) -> DocumentStatus:
        document = self.processor.load_pdf(raw_data)
        page_count = document.page_count
        start_time = time.time()
        log.info(
            "core.convert_document_to_images.start",
            document_id=id,
            page_count=page_count,
        )
        for p_n in range(1, page_count + 1):
            try:
                page = document.load_page(p_n - 1)
                self._process_page(page, document_id, p_n)
            except Exception:  # pylint:disable=broad-except
                log.exception(
                    "core.convert_document_to_images.exception",
                    document_id=document_id,
                    page_number=p_n,
                )
                status = DocumentStatus.error
                break
        else:
            status = DocumentStatus.success
        document.close()
        processing_time = round(time.time() - start_time, 6)
        log.info(
            "core.convert_document_to_images.end",
            document_id=document_id,
            processing_time_seconds=processing_time,
        )
        self.document_repository.update_by_id(document_id, status, processing_time)
        return status.name

    def _process_page(self, page: fitz.Page, document_id: int, page_number: int):
        log.info(
            "core.process_page.start", document_id=document_id, page_number=page_number
        )
        img = self.processor.convert_page_to_image(
            page,
            dpi=self.image_settings.dpi,
            width=self.image_settings.width,
            height=self.image_settings.height,
        )
        print(type(img))
        path = f"{document_id}/{page_number}.png"
        self.s3_client.save_file(key=path, raw_data=img)

    def save_pdf_file(self, document_id: int, raw_data: bytes) -> str:
        log.info("core.save_pdf_file", document_id=document_id)
        path = f"{document_id}/{PDF_FILE_NAME}"
        return self.s3_client.save_file(path, raw_data)

    def get_pdf_file(self, document_id: int) -> bytes:
        log.info("core.get_pdf_file", document_id=document_id)
        path = f"{document_id}/{PDF_FILE_NAME}"
        return self.s3_client.get_file(path)

    def get_image(self, document_id: int, page_number: int) -> bytes:
        log.info("core.get_image", document_id=document_id, page_number=page_number)
        path = f"{document_id}/{page_number}.png"
        return self.s3_client.get_file(path)
