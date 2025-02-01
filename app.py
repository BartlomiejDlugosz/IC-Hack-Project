from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Securely load the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-analogy', methods=['POST'])
def generate_analogy():
    data = request.json
    interest = data.get('interest')
    concept = data.get('concept')

    prompt = f"Explain {concept} using an analogy related to {interest}. Make it simple and engaging."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use GPT-4 if available: "gpt-4"
            messages=[
                {"role": "system", "content": "You are an expert teacher specializing in making complex concepts easy to understand using real-life analogies."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7  # Controls creativity
        )

        analogy = response['choices'][0]['message']['content'].strip()
        return jsonify({'analogy': analogy})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
