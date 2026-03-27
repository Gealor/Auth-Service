import logging
from core.config import settings


logging.basicConfig(
    level=settings.log.level,
    format=settings.log.LOG_DEFAULT_FORMAT,
    datefmt=settings.log.datefmt,
)

log = logging.getLogger(__name__)