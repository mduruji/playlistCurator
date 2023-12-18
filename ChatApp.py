import os
import typer
from openai import OpenAI
from dotenv import load_dotenv
from SpotifyApp import spotifyApp  # Import the spotifyApp class from SpotifyApp module

# Load environment variables from .env file
load_dotenv()

class ChatApp:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

        # Initialize Typer app
        self.app = typer.Typer()

        # Define command for interactive chat
        self.app.command()(self.interactive_chat)

    def run(self):
        """Run the Typer app."""
        self.app()

    def interactive_chat(self):
        """Interactive CLI tool to interact with chatGPT."""
        typer.echo("Starting interactive chat with chatGPT. Type exit to end the session")
        messages = []

        while True:
            prompt = input("You: ")
            plus_prompt = "return a json with the songs in the format {""name"": "", ""artist"":""only the main artist(s)""}"
            messages.append({"role": "user", "content": prompt + plus_prompt})

            if prompt.lower() == "exit":
                typer.echo("ChatGPT: Goodbye!")
                break

            # Get response from chatGPT
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", messages=messages
            )

            # Display chatGPT's response
            typer.echo(f'ChatGPT: {response["choices"][0]["message"]["content"]}')

            # Append chatGPT's response to messages
            messages.append(response["choices"][0]["message"]["content"])

        # Call the curate method with the last output
        self.curate(messages[-1])

    def curate(self, songs):
        """Curate songs and create a Spotify playlist if requested."""
        choice = input("Would you like to create a playlist with these songs? ")
        if choice.lower() == "yes":
            secret_key = input("Enter a secret key: ")
            # Create an instance of the spotifyApp class and run the app
            spotify_app = spotifyApp(secret_key, songs)
            spotify_app.run()
        else:
            return

if __name__ == "__main__":
    # Create an instance of the ChatApp class and run the app
    chatty = ChatApp()
    chatty.run()