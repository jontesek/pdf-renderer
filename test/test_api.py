import os
import pathlib
from unittest import mock

import pytest

from renderer.api.app import app, core
from renderer.database.repositories import DocumentRepository, DocumentNotFoundError
from renderer.database.models import Document, DocumentStatus
from renderer.clients.s3 import S3Client


@pytest.fixture()
def client():
    return app.test_client()


def get_test_file(file_name: str) -> bytes:
    dir_path = pathlib.Path(__file__).resolve().parent
    file_path = os.path.join(dir_path, "test_files", file_name)
    with open(file_path, "rb") as f:
        return f.read()


def test_ping(client):
    response = client.get("/ping")
    assert response.text == "pong"


def test_upload(client):
    pdf_file = get_test_file("test.pdf")
    repository_mock = mock.Mock(spec=DocumentRepository)
    repository_mock.add.return_value = 1
    core.document_repository = repository_mock
    response = client.post("/upload", data=pdf_file).json
    assert response["document_id"] == 1
    assert response["status"] == "processing"
    assert response["page_count"] == 2
    assert response["input_hash"] == "d4d3c03c152e3672b58779f4932f07215d5eabcd"


def test_upload_415(client):
    image_file = get_test_file("page_2.png")
    response = client.post("/upload", data=image_file)
    assert response.status_code == 415


def test_get_document(client):
    repository_mock = mock.Mock(spec=DocumentRepository)
    repository_mock.get_by_id.return_value = Document(
        id=1, status=DocumentStatus.success, page_count=2
    )
    core.document_repository = repository_mock
    response = client.get("/document/1").json
    assert response["status"] == DocumentStatus.success.name
    assert response["page_count"] == 2


def test_get_document_404(client):
    repository_mock = mock.Mock(spec=DocumentRepository)
    repository_mock.get_by_id.side_effect = DocumentNotFoundError(1)
    core.document_repository = repository_mock
    response = client.get("/document/1")
    assert response.status_code == 404


def test_get_image(client):
    repository_mock = mock.Mock(spec=DocumentRepository)
    repository_mock.get_by_id.return_value = Document(
        id=1, status=DocumentStatus.success, page_count=2
    )
    core.document_repository = repository_mock

    image_file = get_test_file("page_2.png")
    s3_mock = mock.Mock(spec=S3Client)
    s3_mock.get_file.return_value = image_file
    core.s3_client = s3_mock

    response = client.get("/image/1/2")
    assert response.data == image_file


def test_get_image_404(client):
    repository_mock = mock.Mock(spec=DocumentRepository)
    repository_mock.get_by_id.side_effect = DocumentNotFoundError(1)
    core.document_repository = repository_mock
    response = client.get("/image/1/2")
    assert "document doesn't exist" in response.text


def test_get_image_422(client):
    repository_mock = mock.Mock(spec=DocumentRepository)
    repository_mock.get_by_id.return_value = Document(
        status=DocumentStatus.processing,
    )
    core.document_repository = repository_mock
    response = client.get("/image/1/2")
    assert response.status_code == 422


def test_get_image_400(client):
    repository_mock = mock.Mock(spec=DocumentRepository)
    repository_mock.get_by_id.return_value = Document(
        id=1, page_count=2,
    )
    core.document_repository = repository_mock
    response = client.get("/image/1/20")
    assert "page number is larger" in response.text
