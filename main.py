#!/usr/bin/env python3

import os
import time
import logging
import argparse
from email_bot import EmailBot

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()


def setup_logging(log_level):
    """Set up logging with a clean, minimal format."""
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicate logs
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    # Create custom formatters based on log level
    if log_level == logging.DEBUG:
        # More detailed but still clean format for debug mode
        formatter = logging.Formatter('%(levelname)-8s %(message)s')
    else:
        # Minimal format for normal operation
        formatter = logging.Formatter('%(levelname)-8s %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Reduce verbosity of httpcore logs
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    # Use DEBUG logging only for our app modules, not dependencies
    for logger_name in ['googleapiclient', 'google', 'openai']:
        logging.getLogger(logger_name).setLevel(logging.INFO)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Email auto-reply bot')
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    return parser.parse_args()


def main():
    """Main function to run the email bot."""
    args = parse_args()

    # Map string log level to logging constant
    log_level = getattr(logging, args.log_level)

    # Configure logging before starting the bot
    setup_logging(log_level)

    try:
        logging.info("Starting email bot with log level: %s", args.log_level)
        logging.info("GMAIL_TOKEN_JSON: %s", os.environ["GMAIL_TOKEN_JSON"])
        bot = EmailBot()
        bot.process_emails()
        logging.info("Email processing complete")
    except Exception as e:
        logging.error("Error in main function: %s", str(e),
                      exc_info=log_level == logging.DEBUG)


if __name__ == "__main__":
    main()
