#!/usr/bin/env python3

import os
import json
import pickle
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class GmailService:
    """Handles Gmail API authentication and operations."""

    def __init__(self):
        """
        Initialize the Gmail service with OAuth2 authentication.
        """
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        # Gmail API scopes - modify permission to read, send, and manage emails
        SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

        try:
            # Check if token exists from previous authentication
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)
                logging.info("Loaded credentials from token.pickle")

            # If no valid credentials found, check GitHub Actions environment
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    logging.info("Refreshing expired credentials")
                    self.creds.refresh(Request())
                else:
                    # Check for GitHub Actions environment variable
                    token_json = os.environ.get("GMAIL_TOKEN_JSON")
                    if token_json:
                        logging.info(
                            "Using credentials from GMAIL_TOKEN_JSON environment variable")
                        token_data = json.loads(token_json)
                        self.creds = Credentials.from_authorized_user_info(
                            token_data, SCOPES)
                        logging.debug(
                            "Successfully created credentials from GMAIL_TOKEN_JSON")

                        if self.creds.expired and self.creds.refresh_token:
                            logging.info(
                                "Refreshing expired credentials from environment variable")
                            self.creds.refresh(Request())
                    else:
                        # No credentials available - instruct to use the token generation script
                        logging.error("No valid Gmail credentials found")
                        raise ValueError(
                            "No valid Gmail credentials found. Please run generate_token.py first to "
                            "create valid credentials, then try again."
                        )

                # Save refreshed credentials
                if not os.environ.get("GITHUB_ACTIONS") and self.creds and self.creds.valid:
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(self.creds, token)
                    logging.info("Updated credentials saved to token.pickle")
                    logging.debug(
                        f"Credentials expire at: {self.creds.expiry}")

            # Create the Gmail API service
            logging.debug("Building Gmail API service")
            self.service = build('gmail', 'v1', credentials=self.creds)
            logging.info("Gmail service initialized successfully")

        except Exception as e:
            logging.error(f"Authentication error: {str(e)}", exc_info=logging.getLogger(
            ).level == logging.DEBUG)
            raise
