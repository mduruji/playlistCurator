import os
import typer
import json
from openai import OpenAI
from dotenv import load_dotenv
import SpotifyApp

load_dotenv()

class ChatApp:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

        self.app = typer.Typer()

        self.app.command()(self.interactive_chat)

    def run(self):
        """Run the Typer app."""
        self.app()

    def interactive_chat(self):
        """Interactive CLI tool to interact with chatGPT."""
        typer.echo("Starting interactive chat with chatGPT. Type exit to end the session")

        try:
            prompt = input("You: ")
            plus_prompt = """return a json with the songs in the format {name:" " , artist: "only the main artist(s)"} using , as a delimiter between songs"""

            if prompt.lower() == "exit":
                typer.echo("ChatGPT: Goodbye!")
                return

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"{prompt}{plus_prompt}"}]
            )

            if 'choices' not in response or not response['choices']:
                raise ValueError("Invalid response from OpenAI API")

            json_dict = response.choices[0].message.content
            typer.echo(f'ChatGPT: {json_dict}')

            content_as_json = json.loads(json_dict)

            songs = content_as_json.get('songs', [])
            self.curate(songs)

        except Exception as e:
            typer.echo(f"Error during interactive chat: {str(e)}")

    def curate(self, songs):
        """Curate songs and create a Spotify playlist if requested."""
        while True:
            try:
                choice = input("Would you like to create a playlist with these songs? ")
                if choice.lower() == "yes":
                    secret_key = input("Enter a secret key: ")
                    spotify_app = SpotifyApp.spotifyApp(secret_key, songs)
                    spotify_app.go()
                    break 
                elif choice.lower() == "no":
                    typer.echo("Exiting interactive chat.")
                    break 
                else:
                    typer.echo("Invalid choice. Please enter 'yes' or 'no'.")
            except Exception as e:
                typer.echo(f"Error during playlist creation: {str(e)}")

if __name__ == "__main__":
    chatty = ChatApp()
    chatty.run()