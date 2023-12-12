import os
import datetime
import openai
import requests
import json
import base64
import typer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
app = typer.Typer()

class ChatGPT_Obj:
    def __init__(self):
        self.openai.api_key = os.getenv("OPENAI_KEY")
        self.message_history = []

    def chat(self, inp, role="user"):
        # Append user input to the message history
        self.message_history.append({"role": role, "content": inp})

        # Call OpenAI's ChatCompletion API
        reply = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.message_history
        )

        # Extract the content of the assistant's reply
        reply_content = reply.choices[0].message.content
        print(reply_content)

        # Append assistant's reply to the message history
        self.message_history.append({"role": "assistant", "content": reply_content})
        return reply_content

    def get_user_input(self):
        while True:
            # Get user input from the console
            user_input = input(">: ")
            print(f"User's input was: {user_input}\n")

            # Continue the conversation until the user inputs "Done"
            if user_input.lower() == "done":
                break

            # Call the chat method to get the assistant's reply
            self.chat(user_input)