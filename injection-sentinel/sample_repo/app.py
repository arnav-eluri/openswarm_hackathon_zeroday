"""
Sample Flask application with prompt injection vulnerability
"""

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/chat', methods=['POST'])
def chat():
    """
    VULNERABLE: User input flows directly into LLM prompt
    """
    # Get user input from HTTP request
    user_message = request.json.get('message', '')
    
    # VULNERABILITY: Direct string interpolation
    prompt = f"User said: {user_message}. Please respond helpfully."
    
    # Simulated LLM call
    response = call_llm(prompt)
    
    return jsonify({"response": response})


def call_llm(prompt):
    """Simulated LLM call"""
    # In real code, this would call OpenAI/Anthropic/etc
    return f"Response to: {prompt}"


if __name__ == '__main__':
    app.run(debug=True)
