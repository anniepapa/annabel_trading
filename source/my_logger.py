import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s-%(name)s🔱%(module)s-%(levelname)s:\n %(message)s\n-------------------💲",  # noqa
)

logger = logging.getLogger(__name__)
