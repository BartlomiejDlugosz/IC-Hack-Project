from openai_integration import askGPT
from flask import jsonify

section_template = "{title: '', [{content: '', type: ''}]}"

info_template = "{subtitle: '', content: '', type: 'info'}"

question_template = "{question: '', options: ['', '', '', ''], correct_answer: '', type: ''}"

def create_section(interest, concept):    
    try:
        section = askGPT(f"""You are an expert teacher specializing in making complex concepts easy to understand using real-life analogies. Create a plan to explain the concept of {concept} to your students using an analogy related to {interest}, but also sporadically including definitions and interesting facts.
        You will return the analogy based on the concept and interest provided in a JSON format in this style: {section_template}, where the type can be a question and be {question_template}, or an introduction of new content {info_template}. Make sure the new content is engaging and simple to understand and a maximum of a few sentences, and is followed by one or more questions related to it. There should be between 2 and 5 pairs of new content and questions in the section.""",
        
                              f"Explain {concept} using an analogy related to {interest}. Make it simple and engaging.")
        
        print(section)
        return jsonify({
            'section': section
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# create_section('swimming', 'variables')