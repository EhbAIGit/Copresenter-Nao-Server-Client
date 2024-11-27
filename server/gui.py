import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
from datetime import datetime

class ConversationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversation Logs")

        # Conversation frame with ScrolledText widget for conversation
        conversation_frame = ttk.Frame(root)
        conversation_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # ScrolledText to show conversation history
        self.conversation_log = ScrolledText(conversation_frame, wrap=tk.WORD, width=60, height=20)
        self.conversation_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.conversation_log.tag_configure("user", foreground="blue", justify='right')
        self.conversation_log.tag_configure("assistant", foreground="green", justify='left')

    def add_user_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conversation_log.insert(tk.END, f"[{timestamp}] You: {message}\n", "user")
        self.conversation_log.see(tk.END)  # Auto-scroll to the end

    def add_assistant_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conversation_log.insert(tk.END, f"[{timestamp}] Assistant: {message}\n", "assistant")
        self.conversation_log.see(tk.END)  # Auto-scroll to the end
