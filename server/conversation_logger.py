import json
from datetime import datetime

class ConversationLogger:
    def __init__(self, context_filename):
        self.context_filename = context_filename
        self.thread_count = 0

    def set_thread_count(self, count):
        self.thread_count = count

    def add_to_conversation_log(self, user_input, machine_response, parsed_response):
        """
        Adds a conversation entry to the log file in a proper JSON array format.
        """
        # Create the log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "thread_count": self.thread_count,
            "user_input": user_input,
            "machine_response": machine_response,
            "parsed_response": parsed_response
        }

        # Generate a dynamic file name
        file_name = f"logs/conversation_log_{self.context_filename}.json"

        # Check if the log file exists and has content
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                logs = json.load(file)  # Load existing logs
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []  # Start with an empty list if the file doesn't exist or is corrupted

        # Append the new log entry
        logs.append(entry)

        # Save the updated log back to the file
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(logs, file, indent=4, ensure_ascii=False)


class ImageGenerationLogger:
    def __init__(self, context_filename):
        """
        Initialize the logger with a log file name.
        
        Args:
            log_filename (str): The file path where logs will be saved.
        """
        self.context_filename = context_filename

    def log_image_generation(self, cleaned_response, refined_prompt, image_url, caption):
        """
        Logs an image generation event to the log file.

        Args:
            cleaned_response (str): The cleaned user input.
            refined_prompt (str): The refined prompt for image generation.
            image_url (str): The URL of the generated image.
            caption (str): The caption for the generated image.
        """
        # Create the log entry
        entry = {
            "timestamp": datetime.now().isoformat(),  # Add a timestamp
            "cleaned_response": cleaned_response,
            "refined_prompt": refined_prompt,
            "image_url": image_url,
            "caption": caption
        }

        # Generate a dynamic timestamp for the file name
        file_name = f"logs/image_log_{self.context_filename}.json"

        # Check if the log file exists and has content
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                logs = json.load(file)  # Load existing logs
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []  # Start with an empty list if the file doesn't exist or is corrupted

        # Append the new log entry
        logs.append(entry)

        # Save the updated log back to the file
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(logs, file, indent=4, ensure_ascii=False)

        # print(f"Log entry added: {entry}")