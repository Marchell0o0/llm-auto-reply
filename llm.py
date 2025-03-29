#!/usr/bin/env python3

import os
import logging
import re
from openai import OpenAI


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

        logging.debug(f"Initializing DeepSeekLLM with model: {model}")
        logging.debug(f"System prompt length: {len(system_prompt)} characters")

        # Use provided API key or try to get from environment
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            logging.error(
                "No DeepSeek API key provided in environment variables")
            raise ValueError(
                "No DeepSeek API key provided in environment variables")

        # Initialize the client
        try:
            self.client = OpenAI(api_key=self.api_key,
                                 base_url="https://api.deepseek.com/")
            logging.debug("Successfully initialized DeepSeek API client")
        except Exception as e:
            logging.error(
                f"Failed to initialize DeepSeek API client: {str(e)}")
            raise

    def generate_response(self, user_input):
        """
        Generate a response for the given user input.

        Args:
            user_input: The user's message/query

        Returns:
            Generated text response
        """
        try:
            input_length = len(user_input)
            logging.debug(
                f"Generating response for input of length {input_length} characters")

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Generate response for: {user_input}"}
            ]

            logging.debug(
                f"Sending request to DeepSeek API model: {self.model}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000
            )

            generated_content = response.choices[0].message.content
            logging.debug(
                f"Received response of length {len(generated_content)} characters")

            return generated_content
        except Exception as e:
            logging.error(f"Error generating LLM response: {str(e)}", exc_info=logging.getLogger(
            ).level == logging.DEBUG)
            return f"Error: {str(e)}"

    def parse_response(self, response_text):
        """
        Parse the structured response from the LLM.

        Expected format:
        <Type>: [answer, forward to human, ignore]
        <Response>: [response content]
        <Response email>: [email to send the response to]
        <Reason>: [explanation]

        Args:
            response_text: The raw response from the LLM

        Returns:
            dict: Contains 'type', 'response', 'response_email', and 'reason' keys
        """
        try:
            logging.debug("Parsing structured LLM response")

            # Initialize default values
            parsed = {
                'type': 'forward to human',  # Default to human review if parsing fails
                'response': '',
                'response_email': '',  # New field for recipient email
                'reason': 'Failed to parse LLM response'
            }

            # Extract type
            type_match = re.search(r'<Type>:\s*(.*?)(?:\n|$)', response_text)
            if type_match:
                parsed['type'] = type_match.group(1).strip().lower()
                logging.debug(f"Parsed type: {parsed['type']}")

            # Extract response
            response_match = re.search(
                r'<Response>:\s*(.*?)(?=<Response email>|<Reason>|\Z)', response_text, re.DOTALL)
            if response_match:
                parsed['response'] = response_match.group(1).strip()
                logging.debug(
                    f"Response length: {len(parsed['response'])} characters")

            # Extract response email
            email_match = re.search(
                r'<Response email>:\s*(.*?)(?=<Reason>|\Z)', response_text, re.DOTALL)
            if email_match:
                parsed['response_email'] = email_match.group(1).strip()
                logging.debug(f"Response email: {parsed['response_email']}")

            # Extract reason
            reason_match = re.search(
                r'<Reason>:\s*(.*?)(?=<|\Z)', response_text, re.DOTALL)
            if reason_match:
                parsed['reason'] = reason_match.group(1).strip()
                logging.debug(f"Reason: {parsed['reason']}")

            # Validate parsed type
            valid_types = ['answer', 'forward to human', 'ignore']
            if parsed['type'] not in valid_types:
                logging.warning(
                    f"Invalid response type: {parsed['type']}. Defaulting to 'forward to human'")
                parsed['type'] = 'forward to human'
                parsed['reason'] = f"Invalid response type: {parsed['type']}. {parsed['reason']}"

            return parsed

        except Exception as e:
            logging.error(f"Error parsing LLM response: {str(e)}", exc_info=logging.getLogger(
            ).level == logging.DEBUG)
            return {
                'type': 'forward to human',
                'response': '',
                'response_email': '',
                'reason': f"Error parsing response: {str(e)}"
            }
