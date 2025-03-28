import logging
import os
import requests

from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


RANDOM_ORG_URL = os.getenv("RANDOM_ORG_URL",
                           "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new")


def get_random() -> float:
    """
    Fetches a random decimal number between 0.00 and 1.00 from random.org.

    Returns:
        float: A decimal number from random.org with 2 decimal places.

    Raises:
        RuntimeError: If the request fails or times out.
        ValueError: If the response is not a valid float.
    """
    logger.info(f"Requesting random number from {RANDOM_ORG_URL}")

    try:
        response = requests.get(RANDOM_ORG_URL, timeout=5)
        response.raise_for_status()
        logger.info("Received successful response from random.org")

        random_number_str = response.text.strip()
        logger.debug(f"Raw response text: '{random_number_str}'")

        try:
            random_number = float(random_number_str)
            logger.info(f"Parsed random number: {random_number}")
            return random_number

        except ValueError:
            logger.error(f"Invalid response from random.org: {random_number_str}")
            raise ValueError(f"Invalid response from random.org: {random_number_str}")

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to random.org failed: {e}")
        raise RuntimeError(f"Request to random.org failed: {e}")
