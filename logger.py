import logging
from settings import settings

logging.basicConfig(
                    level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
                    )
logger = logging.getLogger()

#logger.setLevel(logging.DEBUG)
