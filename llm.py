#!/usr/bin/env python3

import os
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
