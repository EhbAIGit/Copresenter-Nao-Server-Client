import time
from openai import OpenAI

class WhisperHandler:
    def __init__(self, api_key):
        # Initialize the OpenAI client with the provided API key
        self.client = OpenAI(api_key=api_key)

    def transcribe_audio(self, audio_file_path):
        """
        Transcribe the given audio file to text using OpenAI's Whisper model.
        Args:
            audio_file_path (str): Path to the audio file to be transcribed.
        Returns:
            str: The transcribed text from the audio file, or None if an error occurred.
        """
        try:
            start_time_transcription = time.perf_counter()

            # Open the audio file and send it to OpenAI for transcription
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )

            # Extract the text from the response
            user_input_text = response.text
            end_time_transcription = time.perf_counter()
            total_time_transcription = end_time_transcription - start_time_transcription

            print(f"Total transcription time: {total_time_transcription}, transcription: {user_input_text}")

            return user_input_text

        except Exception as e:
            print(f"Whisper connection error: {e}")
            return None
