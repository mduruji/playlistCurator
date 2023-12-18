import os, typer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key = os.getenv("OPENAI_KEY")
)

app = typer.Typer()

@app.command()
def interactive_chat():
    """Interactive CLI tool to interact with chat_gpt"""
    typer.echo(
        """Starting interactive chat with chatGPT. Type exit to end the session"""
    )
    messages = []

    while True:
        prompt = input("You: ")
        plusPromt =  "return a json with the songs in the format {""name"": "", ""artist"":""only the main artist(s)""}"
        messages.append({"role":"user", "content":prompt + plusPromt})
        if prompt == "exit":
            typer.echo("ChatGPT: Goodbye!")
            break

        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages= messages
        )

        typer.echo(f'ChatGPT: {response["choices"][0]["message"]["content"]}')
        messages.append(response["choices"][0]["message"]["content"])
        
if __name__ == "__main__":
    app()