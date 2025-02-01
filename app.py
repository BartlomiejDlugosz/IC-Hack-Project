from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Securely load the API key from environment variables
client = OpenAI(
    api_key=os.environ.get("OPENAI_KEY"),  # This is the default and can be omitted
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-analogy', methods=['POST'])
def generate_analogy():
    data = request.json
    interest = data.get('interest')
    concept = data.get('concept')

    prompt = f"Explain {concept} using an analogy related to {interest}. Make it simple and engaging. Use HTML tags to format your response."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Use GPT-4 if available: "gpt-4"
            messages=[
                {"role": "system", "content": "You are an expert teacher specializing in making complex concepts easy to understand using real-life analogies."},
                {"role": "user", "content": prompt}
            ],
            # max_tokens=150,
            temperature=0.7  # Controls creativity
        )

        analogy = response.choices[0].message.content.strip()

        return jsonify({'analogy': analogy})

    except Exception as e:
        print("ERROR: ", e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
