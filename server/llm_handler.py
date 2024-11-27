import time
from openai import OpenAI

class LLMHandler:
    def __init__(self, api_key, context_file):
        # Initialize the OpenAI client with the provided API key
        self.client = OpenAI(api_key=api_key)

        # Load initial context from the context file
        with open(f'contexts/{context_file}.txt', 'r', encoding='utf-8') as file:
            self.inhoud = file.read()

        # Set the initial system message with the context
        self.initial_messages = [
            {"role": "system", "content": self.inhoud},
        ]

        # Initialize messages list with the initial system message
        self.messages = self.initial_messages.copy()

    def reset_conversation(self):
        # Reset the conversation messages to initial state
        self.messages = self.initial_messages.copy()
        print("Conversation is reset")

    def add_user_message(self, user_input):
        # Add user input to the message context
        self.messages.append({"role": "user", "content": user_input})

    def generate_response(self):
        # Call the OpenAI API to generate a response
        start_time_llm = time.perf_counter()
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o",   # model = "gpt-3.5-turbo"
                messages=self.messages
                # max_tokens=70
                # temperature=0.7
            )
            end_time_llm = time.perf_counter()
            total_time_llm = end_time_llm - start_time_llm
            print(f"Total LLM time: {total_time_llm} seconds.")

            # Extract and return the generated response
            return completion.choices[0].message.content
        except Exception as e:
            print(f"LLM connection error: {e}")
            return None

    def add_assistant_message(self, assistant_response):
        # Add the assistant's response to maintain context
        self.messages.append({"role": "assistant", "content": assistant_response})


class PromptRefiner:
    # instruction = "Generate a short prompt for creating an image based on this:"  # Class-level default instruction
    instruction = "Generate a pleasant  prompt for creating an image based on the following text for an episode of a children story:"  # For Wetenschapdag

    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def refine_prompt(self, story, instruction=None):
        """
        Refines a given chatbot response into a short and descriptive prompt.
        
        :param instruction: Instruction for refining the prompt.
                            Example: "Generate a short prompt based on this: "
        :param chatbot_response: The chatbot's original response.
        :return: A refined prompt string.
        """
        # Use the provided instruction if given; otherwise, use the class-level instruction
        # effective_instruction = instruction or self.instruction
        
        try:
            instruction = "Generate a pleasant short prompt for creating an image based on this for a children story:"  # For Wetenschapdag
            
            # Construct the refinement request
            messages = [
                {"role": "system", "content": "You are a helpful assistant for creating an image generation prompt based on a story."},
                {"role": "user", "content": f"{story}"}
            ]
            
            # Call the OpenAI API
            completion = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            
            # Extract and return the refined prompt
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Prompt refinement error: {e}")
            return None
        
class Storyfier:
    instruction = "Based on the following text (likely the start of the provided excerpt), create a concise caption for the episode I created. Focus solely on events that have occurred, avoiding any unanswered questions."  # For Wetenschapdag

    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_story(self, chatbot_response, instruction=None, max_tokens=512):
        """
        Convert a text into a narrative based on the given prompt to create an episode of a story.
        
        :param prompt: The prompt for generating the story.
        :param max_tokens: The maximum number of tokens for the generated story.
        :return: The generated story text.
        """

        # Use the provided instruction if given; otherwise, use the class-level instruction
        effective_instruction = instruction or self.instruction
        
        try:
            instruction = "Based on the following text (likely the start of the provided excerpt), create a concise caption for the episode I created. Focus solely on events that have occurred, avoiding any unanswered questions."  # For Wetenschapdag
            
            # Construct the refinement request
            messages = [
                {"role": "system", "content": "You are a helpful assistant for refining text into short but impactful prompts for image generation."},
                {"role": "user", "content": f"{effective_instruction} {chatbot_response}"}
            ]

            # Call the OpenAI API
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=max_tokens
            )
            
            # Extract and return the refined prompt
            return completion.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Story generation error: {e}")
            return None