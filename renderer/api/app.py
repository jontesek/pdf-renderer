import io
from flask import Flask, request, Response, send_file
import structlog

from .dependencies import get_core
from ..database.repositories import DocumentNotFoundError, DocumentStatus
from ..clients.s3 import FileNotFoundError
from ..worker import process_document

app = Flask(__name__)
logger = structlog.get_logger(__name__)
core = get_core()


@app.get("/ping")
def ping() -> str:
    return "pong"


@app.post("/upload")
def upload_pdf() -> dict:
    raw_data = request.get_data()

    try:
        document = core.processor.load_pdf(raw_data)
    except ValueError as e:
        return Response(str(e), status=415)

    result = core.handle_input_data(raw_data, document)
    process_document.send(result["document_id"])

    return {
        "document_id": result["document_id"],
        "status": result["status"],
        "page_count": result["page_count"],
        "input_hash": result["input_hash"],
    }


@app.get("/document/<int:document_id>")
def get_document(document_id: int) -> dict:

    try:
        document = core.document_repository.get_by_id(document_id)
    except DocumentNotFoundError:
        return Response("document doesn't exist", status=404)

    return {
        "status": document.status.name,
        "page_count": document.page_count,
    }


@app.get("/image/document_id=<int:document_id>&page_number=<int:page_number>")
def get_image(document_id: int, page_number: int) -> bytes:

    try:
        document = core.document_repository.get_by_id(document_id)
    except DocumentNotFoundError:
        return Response("document doesn't exist", status=404)

    if document.status == DocumentStatus.processing:
        return Response("document is still beging processed", status=422)

    if page_number < 1:
        return Response("page number must be larger than 0", status=400)

    if page_number > document.page_count:
        return Response("page number is larger than document's page count", status=400)

    try:
        img = core.get_image(document_id, page_number)
    except FileNotFoundError:
        return Response("couldn't find desired image", status=404)

    # f = open("/Users/kiwi/my-repos/pdf-renderer/test/test.png", "rb").read()

    return send_file(io.BytesIO(img), mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
