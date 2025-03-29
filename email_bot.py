#!/usr/bin/env python3

import os
import base64
import time
import datetime
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import parsedate_to_datetime

from gmail_service import GmailService
from label_manager import GmailLabelManager
from llm import DeepSeekLLM
from config import SYSTEM_PROMPT, EMAIL_TEMPLATE


class EmailBot:
    """Main email bot that processes and responds to emails."""

    def __init__(self):
        """
        Initialize the email bot components.
        """
        try:
            # Set up Gmail service
            logging.info("Initializing Gmail service")
            gmail_service_obj = GmailService()
            self.gmail_service = gmail_service_obj.service

            # Set up label manager
            logging.info("Initializing Gmail label manager")
            self.label_manager = GmailLabelManager(self.gmail_service)

            # Set up LLM
            logging.info("Initializing LLM client")
            api_key = os.environ.get("DEEPSEEK_API_KEY")
            if not api_key:
                logging.error(
                    "DEEPSEEK_API_KEY environment variable is not set")
                raise ValueError(
                    "DEEPSEEK_API_KEY environment variable is not set")

            self.llm = DeepSeekLLM(
                system_prompt=SYSTEM_PROMPT,
                api_key=api_key
            )

            logging.info("Email bot initialized successfully")

        except Exception as e:
            logging.error(f"Failed to initialize email bot: {str(e)}")
            raise

    def process_emails(self):
        """Process unread emails in the inbox."""
        try:
            logging.info("Starting to process unread emails")

            # Query for unread messages that don't have the Bot Read label
            logging.debug(
                "Querying for unread messages without Bot Read label")
            results = self.gmail_service.users().messages().list(
                userId='me',
                q='in:inbox is:unread -label:"Bot Read"',
                maxResults=10  # Limit to 10 messages per run to avoid quota issues
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                logging.info("No unread messages found to process")
                return

            logging.info(f"Found {len(messages)} unread message(s) to process")

            # Process each message
            for message_info in messages:
                message_id = message_info['id']
                logging.debug(f"Processing message ID: {message_id}")

                # Get the full message
                logging.debug(
                    f"Fetching full message data for ID: {message_id}")
                full_message = self.gmail_service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='full'
                ).execute()

                # Process the message
                self._process_single_message(full_message)

                # Add a small delay to avoid rate limiting
                time.sleep(1)

        except Exception as e:
            logging.error(f"Error processing emails: {str(e)}", exc_info=logging.getLogger(
            ).level == logging.DEBUG)

    def _process_single_message(self, message):
        """Process a single email message."""
        message_id = message['id']
        thread_id = message['threadId']

        logging.debug(
            f"Processing message ID: {message_id}, Thread ID: {thread_id}")

        # Skip if already read by a human
        if self.label_manager.is_read_by_human(message):
            logging.info(
                f"Message {message_id} has already been read by a human. Skipping.")
            return

        # Check message age
        if self._is_message_too_old(message):
            logging.info(
                f"Message {message_id} is older than 1 day. Skipping.")
            # Mark as read by bot so it won't be processed again
            self.label_manager.mark_as_bot_read(message_id)
            # Mark for human attention
            self.label_manager.mark_as_needs_human_attention(message_id)
            return

        # Mark message as read by the bot
        self.label_manager.mark_as_bot_read(message_id)
        logging.debug(f"Marked message {message_id} as read by bot")

        # Check if this is the first message in the thread
        logging.debug(f"Checking if message {message_id} is first in thread")
        thread = self.gmail_service.users().threads().get(
            userId='me',
            id=thread_id
        ).execute()

        # If there's more than one message in the thread, mark for human attention and skip
        if len(thread.get('messages', [])) > 1:
            logging.info(
                f"Message {message_id} is a follow-up in a thread. Messages in thread: {len(thread.get('messages', []))}")
            self.label_manager.mark_as_needs_human_attention(message_id)
            logging.debug(
                f"Marked message {message_id} as needing human attention and UNREAD")
            return

        # Extract email details for the response
        headers = {h['name']: h['value']
                   for h in message['payload']['headers']}
        sender_email = headers.get('From', '').split('<')[-1].split('>')[0]
        subject = headers.get('Subject', '')
        logging.debug(f"Email from: {sender_email}, Subject: {subject}")

        # Extract email content
        email_content = self._extract_email_content(message['payload'])

        # Log full email content in debug mode
        logging.debug(
            f"Full email content from {message_id}:\n{'='*50}\n{email_content}\n{'='*50}")

        # TODO: Add logic to determine if the bot should answer or dismiss
        # For now, always answer
        should_answer = True

        # If the bot decides not to answer, mark as dismissed and needs human attention
        if not should_answer:
            logging.info(f"Bot decided to dismiss message {message_id}")
            self.label_manager.mark_as_bot_dismissed(message_id)
            self.label_manager.mark_as_needs_human_attention(message_id)
            logging.debug(f"Marked message {message_id} for human attention")
            return

        # Generate AI response
        logging.info(f"Generating AI response for message {message_id}")
        ai_response = self.llm.generate_response(email_content)
        logging.debug(
            f"Generated AI response:\n{'='*50}\n{ai_response}\n{'='*50}")

        # Send the response
        self._send_response(message_id, thread_id,
                            sender_email, subject, headers, ai_response)

    def _extract_email_content(self, payload):
        """Extract plain text content from the email payload."""
        logging.debug("Extracting email content from payload")
        content = ""

        try:
            if 'parts' in payload:
                logging.debug("Multipart message detected")
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        logging.debug("Found text/plain part")
                        content = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
                        break
                    elif 'parts' in part:
                        # Recursive extraction for multipart messages
                        logging.debug("Found nested multipart, recursing")
                        nested_content = self._extract_email_content(part)
                        if nested_content:
                            content = nested_content
                            break
            elif 'body' in payload and 'data' in payload['body']:
                logging.debug("Found single part message")
                content = base64.urlsafe_b64decode(
                    payload['body']['data']).decode('utf-8')

            content_length = len(content)
            logging.debug(
                f"Extracted email content of length: {content_length} characters")

            if not content:
                logging.warning("No email content could be extracted")

            return content

        except Exception as e:
            logging.error(f"Error extracting email content: {str(e)}", exc_info=logging.getLogger(
            ).level == logging.DEBUG)
            return ""

    def _send_response(self, message_id, thread_id, to_email, subject, headers, ai_response):
        """Send an email response."""
        try:
            logging.info(
                f"Preparing response to {to_email}, message ID: {message_id}")

            # Create HTML content using the template
            logging.debug("Creating email with template")
            html_content = EMAIL_TEMPLATE.replace(
                '{CONTENT}', ai_response.replace('\n', '<br>'))

            # Create MIME message
            message = MIMEMultipart('alternative')
            message['to'] = to_email
            message['subject'] = f"Re: {subject}"
            message['References'] = headers.get('Message-ID', '')
            message['In-Reply-To'] = headers.get('Message-ID', '')

            # Add text part
            text_part = MIMEText(ai_response, 'plain')
            message.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Encode the message
            encoded_message = base64.urlsafe_b64encode(
                message.as_bytes()).decode()

            # Send the message via Gmail API
            logging.debug(
                f"Sending response via Gmail API for message ID: {message_id}")
            result = self.gmail_service.users().messages().send(
                userId='me',
                body={
                    'raw': encoded_message,
                    'threadId': thread_id
                }
            ).execute()

            logging.info(
                f"Auto-response sent to {to_email} for email: {message_id}")

            # Mark as answered by the bot
            self.label_manager.mark_as_bot_answered(message_id)
            logging.debug(f"Marked message {message_id} as answered by bot")

            return True

        except Exception as e:
            logging.error(f"Error sending response to {message_id}: {str(e)}", exc_info=logging.getLogger(
            ).level == logging.DEBUG)

            # Mark as needing human attention since sending failed
            self.label_manager.mark_as_needs_human_attention(message_id)
            logging.warning(
                f"Sending failed, marked message {message_id} for human attention")

            return False

    def _is_message_too_old(self, message):
        """
        Check if a message is more than 1 day old.

        Args:
            message: Gmail API message object

        Returns:
            bool: True if message is older than 1 day, False otherwise
        """
        try:
            message_id = message['id']
            logging.debug(f"Checking age of message: {message_id}")

            # Try to get timestamp from internalDate (milliseconds since epoch)
            if 'internalDate' in message:
                # Convert to seconds
                msg_timestamp = int(message['internalDate']) / 1000
                msg_date = datetime.datetime.fromtimestamp(msg_timestamp)
                logging.debug(
                    f"Using internalDate timestamp: {msg_date.isoformat()}")
            else:
                # Fallback to Date header
                headers = {h['name']: h['value']
                           for h in message['payload']['headers']}
                date_str = headers.get('Date')
                if not date_str:
                    logging.warning(f"No date found for message {message_id}")
                    return False  # If we can't determine age, process the message

                msg_date = parsedate_to_datetime(date_str)
                logging.debug(
                    f"Using Date header timestamp: {msg_date.isoformat()}")

            # Calculate message age in days
            now = datetime.datetime.now()
            age_days = (now - msg_date).total_seconds() / \
                (24 * 3600)  # Convert to days

            logging.info(f"Message {message_id} is {age_days:.1f} days old")

            # Return True if message is older than 1 day
            return age_days > 1

        except Exception as e:
            logging.error(f"Error determining message age: {str(e)}", exc_info=logging.getLogger(
            ).level == logging.DEBUG)
            return False  # If we encounter an error, assume message is not too old
