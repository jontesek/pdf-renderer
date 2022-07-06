from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from .models import Document, DocumentStatus


class DocumentRepository:

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory

    def add(self, status: DocumentStatus, page_count: int, input_hash: str) -> int:
        with self.session_factory() as session:
            document = Document(status=status, page_count=page_count, input_hash=input_hash)
            session.add(document)
            session.commit()
            return document.id

    def get_by_id(self, document_id: int) -> Document:
        with self.session_factory() as session:
            document = session.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise DocumentNotFoundError(document_id)
            return document

    def update_by_id(self, document_id: int, status: DocumentStatus, processing_time: float) -> Document:
        with self.session_factory() as session:
            document = session.query(Document).filter(Document.id == document_id).first()
            if not document:
                raise DocumentNotFoundError(document_id)
            document.status = status
            document.processing_time = processing_time
            session.commit()
            return document
            

class NotFoundError(Exception):

    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class DocumentNotFoundError(NotFoundError):

    entity_name: str = "Document"