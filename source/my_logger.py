import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s🔱%(module)s-%(levelname)s📢 %(message)s 📑",  # noqa
)

logger = logging.getLogger(__name__)
