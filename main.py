#!/usr/bin/env python3
import os
import base64
import json
import requests
import pickle
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from openai import OpenAI
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


# System prompt from email_bot_v1.1.py
SYSTEM_PROMPT = """You are Krysten Trade's AI assistant. Generate ONLY the essential content - no greetings, no signatures, no formatting.

CORE RULES:
1. Match input language exactly
2. Keep responses short and direct
3. Never calculate total prices
4. Never add greetings or signatures
5. Never reject requests outright
6. Always encourage human contact
7. For locations outside Czech Republic, Ukraine, Germany, Slovakia, Austria: explain service area limits politely

FIXED PRICES (quote ONLY for facade work):
- Complete facade package with polystyrene: 700 CZK/m²
- Final layer: 200 CZK/m²
- Mesh, plaster, penetration: 250 CZK/m²
- Polystyrene installation with anchoring: 250 CZK/m²
* Materials included

CORE SERVICES:

1. Construction
- Turnkey family houses
- Facade production
- Fence installation
- Pavement laying
- Complete apartment renovations
- Quality control of construction materials

2. Landscape Design
- Outdoor space transformation
- Flower bed care
- Tree and shrub pruning
- Plant installation
- General landscaping improvements

3. Event Services
- Festival venue maintenance
- Concert stage maintenance
- Restroom facilities
- Parking areas
- Technical support for events
- Commercial space maintenance

4. Cleaning Services
- Lawn mowing
- Garden cleaning
- Garden waste removal
- Outdoor area cleaning
- Post-construction cleanup
- Leaf collection

5. Washing Services
- Professional facade cleaning
- Pavement cleaning
- House and yard cleaning
- Dirt and moss removal
- Gentle pressure washing
- Surface protection

RESPONSE TEMPLATES:

FOR CONSTRUCTION/FACADE:
[service description in one line]

Standardní ceny:
[ONLY if facade work, list relevant prices]

Pro realizaci potřebujeme:
1. Fotografie
2. Prohlídku
3. Konzultaci

Odpovězte pro domluvení detailů.

FOR OTHER SERVICES:
[service description in one line]

Nabízíme:
[2-3 most relevant points from service list]

Potřebujeme:
1. Detaily projektu
2. Fotografie
3. Prohlídku

Odpovězte pro domluvení konzultace.

FOR NON-CORE/COMPLEX:
[acknowledge request in one line]

Náš tým vám rád pomůže s posouzením vašeho požadavku.

Odpovězte pro konzultaci s naším specialistou.

FOR OUT-OF-REGION:
We currently operate in:
- Czech Republic
- Ukraine
- Germany
- Slovakia
- Austria

Unfortunately, we cannot provide direct services in [location].

Please contact local providers for immediate assistance.

REMEMBER:
- Maximum 4-5 lines per section
- No greetings or signatures
- No additional formatting
- No extra sections
- Match input language exactly
- Keep it minimal but helpful"""


# Email template from email_bot_v1.1.py
EMAIL_TEMPLATE = '''<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="color-scheme" content="light only" />
    <title>KrystenTrade Response</title>
  </head>
  <body style="margin: 0; padding: 0; background-color: #222222 !important; font-family: Arial, Helvetica, sans-serif; line-height: 1.6; color-scheme: light only; -webkit-font-smoothing: antialiased;">
    <div style="width: 100%; max-width: 800px; margin: 0 auto; padding: 20px; box-sizing: border-box;">
      <!-- Main Container -->
      <div style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <!-- Header -->
        <div style="padding: 25px 0; border-bottom: 3px solid #ffd301; background-color: #222222; text-align: center;">
          <img
            src="https://drive.google.com/thumbnail?id=1V1955hJSdhcfdQivMUl20g7ACwOVns2E"
            alt="KrystenTrade Logo"
            style="max-width: 200px; height: auto; display: inline-block"
          />
        </div>

        <!-- Content -->
        <div style="padding: 25px 20px; color: #333333 !important; background-color: #ffffff;">
          {CONTENT}
        </div>

        <!-- Footer -->
        <div style="background-color: #222222; padding: 25px 20px; text-align: center;">
          <p style="margin: 0 0 15px 0; color: #ffffff; font-size: 13px">
            © 2024 KrystenTrade. Všechna práva vyhrazena.
          </p>
          <div style="font-size: 13px; line-height: 2">
            <a href="tel:+420777629585" style="color: #ffd301; text-decoration: none; display: block">
              +420 777 629 585
            </a>
            <a href="https://www.krystentrade.com" style="color: #ffd301; text-decoration: none; display: block">
              www.krystentrade.com
            </a>
            <a href="mailto:info@krystentrade.com" style="color: #ffd301; text-decoration: none; display: block">
              info@krystentrade.com
            </a>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>'''


class DeepSeekLLM:
    """A simplified LLM client for generating responses."""

    def __init__(self, system_prompt, api_key=None, model="deepseek-reasoner"):
        """
        Initialize the LLM client.

        Args:
            system_prompt: The system prompt to use
            api_key: API key (if None, will try to get from environment)
            model: Model to use
        """
        self.system_prompt = system_prompt
        self.model = model

        # Use provided API key or try to get from environment
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No DeepSeek API key provided in environment variables")

        # Initialize the client
        self.client = OpenAI(api_key=self.api_key,
                             base_url="https://api.deepseek.com/")

    def generate_response(self, user_input):
        """
        Generate a response for the given user input.

        Args:
            user_input: The user's message/query

        Returns:
            Generated text response
        """
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Generate response for: {user_input}"}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating LLM response: {str(e)}")
            return f"Error: {str(e)}"


class GmailService:
    """Handles Gmail API authentication and operations."""

    def __init__(self):
        """Initialize the Gmail service with OAuth2 authentication."""
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

        # Try to load existing token
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)

        # If no valid credentials available, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # If running in GitHub Actions, try to use stored credentials
                token_json = os.environ.get("GMAIL_TOKEN_JSON")
                if token_json:
                    # Create credentials from the JSON string in environment
                    token_data = json.loads(token_json)
                    self.creds = Credentials.from_authorized_user_info(
                        token_data, SCOPES)

                    # Refresh if needed
                    if self.creds.expired:
                        self.creds.refresh(Request())
                else:
                    # For local development, use the standard flow
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            # Only save locally, not in GitHub Actions
            if not os.environ.get("GITHUB_ACTIONS"):
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)

                # Also save as JSON for GitHub Actions setup
                with open('token.json', 'w') as f:
                    f.write(self.creds.to_json())
                print("Credentials saved to token.pickle and token.json")
                print(
                    "Add the contents of token.json to your GitHub repository secrets as GMAIL_TOKEN_JSON")

        # Create the Gmail service
        self.service = build('gmail', 'v1', credentials=self.creds)
        print("Gmail service initialized successfully")


class GmailLabelManager:
    """Manages Gmail labels for the email bot."""

    def __init__(self, gmail_service):
        """
        Initialize the label manager.

        Args:
            gmail_service: Authenticated Gmail service
        """
        self.service = gmail_service
        self.api_base = "https://gmail.googleapis.com/gmail/v1"
        self.label_ids = self._get_or_create_labels()

    def _get_or_create_labels(self):
        """Get or create the required labels for the email bot."""
        # Define the labels we need - using spaces instead of underscores
        required_labels = [
            {"name": "Bot Read", "labelListVisibility": "labelShow",
                "messageListVisibility": "show"},
            {"name": "Bot Answered", "labelListVisibility": "labelShow",
                "messageListVisibility": "show"},
            {"name": "Bot Dismissed", "labelListVisibility": "labelShow",
                "messageListVisibility": "show"},
            {"name": "Needs Human Attention", "labelListVisibility": "labelShow",
                "messageListVisibility": "show"}
        ]

        # Get existing labels
        existing_labels = self.service.users().labels().list(
            userId='me').execute().get('labels', [])

        # Map of label names to IDs
        label_ids = {}
        existing_label_names = [label["name"] for label in existing_labels]

        # Create or get IDs for required labels
        for label_info in required_labels:
            label_name = label_info["name"]

            if label_name in existing_label_names:
                # Label exists, get its ID
                for label in existing_labels:
                    if label["name"] == label_name:
                        label_ids[label_name] = label["id"]
                        break
            else:
                # Label doesn't exist, create it
                created_label = self.service.users().labels().create(
                    userId='me',
                    body=label_info
                ).execute()
                label_ids[label_name] = created_label["id"]
                print(f"Created label: {label_name}")

        return label_ids

    def is_read_by_human(self, message):
        """Check if the message has been read by a human."""
        # If it's not UNREAD and doesn't have the Bot Read label, assume a human read it
        label_ids = message.get("labelIds", [])
        return "UNREAD" not in label_ids and self.label_ids.get("Bot Read") not in label_ids

    def mark_as_bot_read(self, message_id):
        """Mark a message as read by the bot."""
        return self._modify_labels(message_id,
                                   add_labels=[self.label_ids["Bot Read"]],
                                   remove_labels=["UNREAD"])

    def mark_as_bot_answered(self, message_id):
        """Mark a message as answered by the bot."""
        return self._modify_labels(message_id,
                                   add_labels=[self.label_ids["Bot Answered"]])

    def mark_as_bot_dismissed(self, message_id):
        """Mark a message as dismissed by the bot."""
        return self._modify_labels(message_id,
                                   add_labels=[self.label_ids["Bot Dismissed"]])

    def mark_as_needs_human_attention(self, message_id):
        """
        Mark a message as needing human attention.
        Ensures the message is also marked as UNREAD.
        """
        return self._modify_labels(message_id,
                                   add_labels=[self.label_ids["Needs Human Attention"], "UNREAD"])

    def _modify_labels(self, message_id, add_labels=None, remove_labels=None):
        """Modify the labels of a message."""
        if not add_labels and not remove_labels:
            return True

        body = {}
        if add_labels:
            body["addLabelIds"] = add_labels
        if remove_labels:
            body["removeLabelIds"] = remove_labels

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            ).execute()
            return True
        except Exception as e:
            print(
                f"Failed to modify labels for message {message_id}: {str(e)}")
            return False


class EmailBot:
    """Main email bot that processes and responds to emails."""

    def __init__(self):
        """Initialize the email bot components."""
        # Set up Gmail service
        self.gmail_service = GmailService().service

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


def main():
    """Main function to run the email bot."""
    try:
        print("Starting email bot")
        bot = EmailBot()
        bot.process_emails()
        print("Email processing complete")
    except Exception as e:
        print(f"Error in main function: {str(e)}")


if __name__ == "__main__":
    main()
