"""
Additional vulnerable patterns for testing
"""

import os
import json


def vulnerable_concatenation(user_data):
    """
    VULNERABILITY: String concatenation
    """
    prompt = "System: You are helpful.\nUser: " + user_data + "\nAssistant:"
    return prompt


def vulnerable_format(user_data):
    """
    VULNERABILITY: .format() method
    """
    prompt = "User said: {}. Respond.".format(user_data)
    return prompt


def vulnerable_join(user_messages):
    """
    VULNERABILITY: join() with user data
    """
    prompt = "\n".join([
        "System prompt here",
        f"User: {msg}" for msg in user_messages
    ])
    return prompt


def vulnerable_from_file(filepath):
    """
    VULNERABILITY: File content in prompt
    """
    with open(filepath, 'r') as f:
        file_content = f.read()
    
    # File could contain malicious instructions
    prompt = f"Summarize this document:\n\n{file_content}"
    return prompt


def vulnerable_from_env():
    """
    VULNERABILITY: Environment variable in prompt
    """
    user_name = os.environ.get('USER_NAME', 'User')
    prompt = f"Hello {user_name}, how can I help?"
    return prompt


def vulnerable_json_input(json_string):
    """
    VULNERABILITY: JSON parsing into prompt
    """
    data = json.loads(json_string)
    message = data.get('message', '')
    
    prompt = f"Process this request: {message}"
    return prompt


# Example of vulnerable CSV processing
def process_csv_row(row):
    """
    VULNERABILITY: CSV data in prompts
    """
    name, email, message = row
    prompt = f"User {name} ({email}) said: {message}"
    return prompt
