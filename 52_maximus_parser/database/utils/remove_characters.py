import logging

logger = logging.getLogger(__name__)


def remove_leading_zeros(last_model_run):
    try:
        logger.info(f"Started removing leading zeroes")
        if last_model_run.isdigit() and len(last_model_run) == 1:
            # Do nothing if it's a single digit
            return last_model_run

        if last_model_run.startswith('00'):
            # Replace only the first '0' with an empty string
            last_model_run = last_model_run.replace('0', '', 1)
        else:
            # Remove all leading zeros
            last_model_run = last_model_run.lstrip('0')
        logger.info(f"Finished removing leading zeroes")
        return last_model_run
    except Exception as e:
        logger.error(f"Error while removing leading zeroes: {e}")
