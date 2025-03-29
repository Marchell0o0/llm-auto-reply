#!/usr/bin/env python3

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
