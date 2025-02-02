from dotenv import load_dotenv
from openai import OpenAI
import os
import re

# Load environment variables from .env file
load_dotenv()

# Securely load the API key from environment variables
client = OpenAI(
    api_key=os.environ.get("OPENAI_KEY"),  # This is the default and can be omitted
)

def askGPT(systemPrompt, userPrompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use GPT-4 if available: "gpt-4"
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": userPrompt}
            ],
            # max_tokens=150,
            temperature=0.7  # Controls creativity
        )

        response = response.choices[0].message.content.strip()
        response = re.sub(r"```(json)?\s*|\s*```", "", response).strip()

        return response

    except Exception as e:
        print("ERROR: ", e)
        return None