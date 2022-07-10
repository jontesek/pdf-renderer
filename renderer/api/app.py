import io

import sentry_sdk
import structlog
from flask import Flask, Response, request, send_file
from flask_swagger_ui import get_swaggerui_blueprint
from sentry_sdk.integrations.flask import FlaskIntegration

from .. import settings
from ..clients.s3 import S3FileNotFoundError
from ..database.repositories import DocumentNotFoundError, DocumentStatus
from ..worker import process_document
from .dependencies import get_core

if not settings.local:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[
            FlaskIntegration(),
        ],
        traces_sample_rate=1.0,
    )
    from ddtrace import patch_all

    patch_all()

app = Flask(__name__)
logger = structlog.get_logger(__name__)
core = get_core()

swaggerui_blueprint = get_swaggerui_blueprint(
    "/api/docs", "/static/openapi_specification.yml"
)
app.register_blueprint(swaggerui_blueprint)


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


@app.get("/image/<int:document_id>/<int:page_number>")
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
    except S3FileNotFoundError:
        return Response("couldn't find desired image", status=404)

    return send_file(io.BytesIO(img), mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
