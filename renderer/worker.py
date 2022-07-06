import dramatiq
import structlog
from dramatiq.brokers.redis import RedisBroker

from .api.dependencies import get_core
from .settings import REDIS_URL

redis_broker = RedisBroker(url=REDIS_URL)
dramatiq.set_broker(redis_broker)
logger = structlog.get_logger(__name__)
core = get_core()

@dramatiq.actor(max_retries=3)
def process_document(document_id: int):
    logger.info("worker.process_document.start", document_id=document_id)
    raw_data = core.get_pdf_file(document_id)
    status = core.convert_document_to_images(raw_data, document_id)
    logger.info("worker.process_document.end", document_id=document_id, status=status)
