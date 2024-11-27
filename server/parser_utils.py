import os
import re
import random
import yaml
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize

# Parser Method Globals
speech_controls = True
default_contextual = True
mappings = {}

def load_gestures():
    df = pd.read_csv('gestures_dataset/gestures.csv', usecols=['Category', 'Gesture', 'Weight'])

    global mappings
    mappings = {}

    # Group by the 'Category' and aggregate lists of 'Gesture' and 'Weight'
    for category, group in df.groupby('Category'):
        gestures = group['Gesture'].tolist()
        weights = group['Weight'].tolist()
        mappings[category] = (gestures, weights)   
    return mappings

# Function to tokenize text into sentences
def tokenize_sentences(text):
    # Download the Punkt tokenizer models (only needs to be done once)
    # nltk.download('punkt')

    # Use NLTK's sent_tokenize to split text into sentences
    sentences = sent_tokenize(text)
    return sentences

# Function to parse text and replace bracketed markdowns with gestures and eye led colors
def get_random_choice(gesture):
    global speech_controls, default_contextual
    pause = 1000
    speed = 80  # between 70-80 for an effective communication
    volume = 200 # maximum volume; range 10-100
    
    # We need Nao to hesitate one second after starting each gesture for an effective communication
    pause_marker = f"\\pau={pause}\\"
    
    if speech_controls:   
        # Slow down Nao's speed and boost its volume for an effective communication 
        speech_controls_markers = f"\\rspd={speed}\\ \\vol={volume}\\"

    if not default_contextual:
        mode_marker = "^mode(disabled)"
    else:
        mode_marker = ""
    
    if gesture in mappings:
        choices, weights = mappings[gesture]
        selected_choice = random.choices(choices, weights)[0]

        return f"{speech_controls_markers} ^start(animations/Stand/Gestures/{selected_choice}) {pause_marker} {mode_marker}"
    
    return ""

# Function to replace square and round bracketed markdowns 
# with eye led colors and gestures respectively
def replace_bracket_contents(text):
    # Dictionary mapping the bracketed text to specific values
    sentiments_dic = {
        '[happy]': '\\mrk=4001\\',      # Yellow 
        '[sad]': '\\mrk=4002\\',        # Blue
        '[humor]': '\\mrk=4003\\',      # Orange
        '[excited]': '\\mrk=4003\\',    # Orange
        '[info]': '\\mrk=4004\\',       # Green
        '[ponder]': '\\mrk=4005\\',     # Purple
        '[privacy]': '\\mrk=4006\\',    # Red
        '[warning]': '\\mrk=4006\\',    # Red
        '[learning]': '\\mrk=4007\\',   # Cyan
    }
    
    # Function to replace sentiments based on the dictionary
    def replace_sentiments(match):
        normalized_sentiment = match.group(0).lower()  # making it case insensitive
        return sentiments_dic.get(normalized_sentiment, '')  # removes the bracket and its content if it's not in the dictionary

    # Replace sentiments first
    text = re.sub(r'\[.*?\]', replace_sentiments, text)

    # Function to handle content within braces
    def replace_braces(match):
        gesture = match.group(1)  # Extract the gesture within the braces
        return get_random_choice(gesture)

    # Replace content within braces
    text = re.sub(r'\{([^}]+)\}', replace_braces, text)

    # # Replace newlines with spaces
    # text = text.replace('\n', ' ')

    return text

def save_parsed_text(text, directory='parsed_texts'):
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # List all files in the directory that match the naming pattern
    files = [f for f in os.listdir(directory) if f.startswith('parsed_text') and f.endswith('.txt')]
    
    # Sort files to find the highest numbered file
    files.sort()
    last_file = files[-1] if files else 'parsed_text0.txt'
    
    # Extract the number from the last file and increment it for the new file
    last_number = int(last_file.replace('parsed_text', '').replace('.txt', ''))
    new_file = f'parsed_text{last_number + 1}.txt'
    
    full_path = os.path.join(directory, new_file)
    
    with open(full_path, 'w') as file:
        file.write(text)

    print(f'File saved as {new_file}')

class CustomLoader(yaml.SafeLoader):
    def construct_scalar(self, node):
        value = super(CustomLoader, self).construct_scalar(node)
        return value.replace('\\\\', '\\')

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.load(file, Loader=CustomLoader)
    
# Function for cleaning text form enclosed brackets (gestures, sentiments, languages, etc.)
# This can be used as a clean prompt for another pipelien (e.g. image generation)
def clean_text(input_text):
    # Remove anything inside {}, [], or | |, including the delimiters
    cleaned_text = re.sub(r'\{.*?\}|\[.*?\]|\|.*?\|', '', input_text)
    # Remove escaped characters like \n and \"
    cleaned_text = re.sub(r'\\[n\\"]', '', cleaned_text)
    # Remove extra spaces introduced by the removal
    cleaned_text = ' '.join(cleaned_text.split())
    return cleaned_text

# Load gestures on module import
load_gestures()
