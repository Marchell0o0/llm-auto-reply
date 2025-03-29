#!/usr/bin/env python3

import os
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from gmail_service import GmailService
from label_manager import GmailLabelManager
from llm import DeepSeekLLM
from config import SYSTEM_PROMPT, EMAIL_TEMPLATE


class EmailBot:
    """Main email bot that processes and responds to emails."""

    def __init__(self):
        """Initialize the email bot components."""
        try:
            # Set up Gmail service
            gmail_service_obj = GmailService()
            self.gmail_service = gmail_service_obj.service

            # Set up label manager
            self.label_manager = GmailLabelManager(self.gmail_service)

            # Set up LLM
            api_key = os.environ.get("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError(
                    "DEEPSEEK_API_KEY environment variable is not set")

            self.llm = DeepSeekLLM(
                system_prompt=SYSTEM_PROMPT,
                api_key=api_key
            )

            print("Email bot initialized successfully")

        except Exception as e:
            print(f"Failed to initialize email bot: {str(e)}")
            raise

    def process_emails(self):
        """Process unread emails in the inbox."""
        try:
            print("Starting to process unread emails")

            # Query for unread messages that don't have the Bot Read label
            results = self.gmail_service.users().messages().list(
                userId='me',
                q='in:inbox is:unread -label:"Bot Read"',
                maxResults=10  # Limit to 10 messages per run to avoid quota issues
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                print("No unread messages found to process")
                return

            print(f"Found {len(messages)} unread message(s) to process")

            # Process each message
            for message_info in messages:
                message_id = message_info['id']

                # Get the full message
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
            print(f"Error processing emails: {str(e)}")

    def _process_single_message(self, message):
        """Process a single email message."""
        message_id = message['id']
        thread_id = message['threadId']

        # Skip if already read by a human
        if self.label_manager.is_read_by_human(message):
            print(
                f"Message {message_id} has already been read by a human. Skipping.")
            return

        # Mark message as read by the bot
        self.label_manager.mark_as_bot_read(message_id)
        print(f"Marked message {message_id} as read by bot")

        # Check if this is the first message in the thread
        thread = self.gmail_service.users().threads().get(
            userId='me',
            id=thread_id
        ).execute()

        # If there's more than one message in the thread, mark for human attention and skip
        if len(thread.get('messages', [])) > 1:
            print(f"Message {message_id} is a follow-up in a thread")
            self.label_manager.mark_as_needs_human_attention(message_id)
            print(
                f"Marked message {message_id} as needing human attention and UNREAD")
            return

        # Extract email details for the response
        headers = {h['name']: h['value']
                   for h in message['payload']['headers']}
        sender_email = headers.get('From', '').split('<')[-1].split('>')[0]
        subject = headers.get('Subject', '')

        # Extract email content
        email_content = self._extract_email_content(message['payload'])

        # TODO: Add logic to determine if the bot should answer or dismiss
        # For now, always answer
        should_answer = True

        # If the bot decides not to answer, mark as dismissed and needs human attention
        if not should_answer:
            self.label_manager.mark_as_bot_dismissed(message_id)
            self.label_manager.mark_as_needs_human_attention(message_id)
            print(
                f"Bot decided to dismiss message {message_id} and marked for human attention")
            return

        # Generate AI response
        ai_response = self.llm.generate_response(email_content)
        print(f"Generated AI response: {ai_response}")

        # Send the response
        self._send_response(message_id, thread_id,
                            sender_email, subject, headers, ai_response)

    def _extract_email_content(self, payload):
        """Extract plain text content from the email payload."""
        content = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    content = base64.urlsafe_b64decode(
                        part['body']['data']).decode('utf-8')
                    break
                elif 'parts' in part:
                    # Recursive extraction for multipart messages
                    nested_content = self._extract_email_content(part)
                    if nested_content:
                        content = nested_content
                        break
        elif 'body' in payload and 'data' in payload['body']:
            content = base64.urlsafe_b64decode(
                payload['body']['data']).decode('utf-8')

        return content

    def _send_response(self, message_id, thread_id, to_email, subject, headers, ai_response):
        """Send an email response."""
        try:
            # Create HTML content using the template
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
            result = self.gmail_service.users().messages().send(
                userId='me',
                body={
                    'raw': encoded_message,
                    'threadId': thread_id
                }
            ).execute()

            print(f"Auto-response sent to {to_email} for email: {message_id}")

            # Mark as answered by the bot
            self.label_manager.mark_as_bot_answered(message_id)
            print(f"Marked message {message_id} as answered by bot")

            return True

        except Exception as e:
            print(f"Error sending response to {message_id}: {str(e)}")

            # Mark as needing human attention since sending failed
            self.label_manager.mark_as_needs_human_attention(message_id)
            print(
                f"Sending failed, marked message {message_id} for human attention")

            return False
