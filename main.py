#!/usr/bin/env python3

import os
import time
from email_bot import EmailBot

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()


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
