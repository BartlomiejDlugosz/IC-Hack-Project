from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from openai_integration import askGPT

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-analogy', methods=['POST'])
def generate_analogy():
    data = request.json
    interest = data.get('interest')
    concept = data.get('concept')


    systemPrompt = "You are an expert teacher specializing in making complex concepts easy to understand using real-life analogies."
    userPrompt = f"Explain {concept} using an analogy related to {interest}. Make it simple and engaging. Use HTML tags to format your response."

    analogy = askGPT(systemPrompt, userPrompt)


    if analogy != None:
        return jsonify({'analogy': analogy})
    else:
        return jsonify({}), 500

if __name__ == '__main__':
    app.run(debug=True)
