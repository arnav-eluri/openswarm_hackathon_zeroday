"""
Sample LLM agent with multiple prompt injection vulnerabilities
"""

import sys


class VulnerableAgent:
    """
    Intentionally vulnerable LLM agent for testing
    """
    
    def __init__(self):
        self.system_prompt = "You are a helpful assistant."
    
    def process_user_input(self, user_input):
        """
        VULNERABILITY 1: F-string interpolation without sanitization
        """
        prompt = f"{self.system_prompt}\n\nUser: {user_input}\nAssistant:"
        return self.invoke_llm(prompt)
    
    def process_with_context(self, user_input, document_content):
        """
        VULNERABILITY 2: Multiple user inputs in prompt
        """
        prompt = f"""
{self.system_prompt}

Document content:
{document_content}

User question: {user_input}

Please answer based on the document.
"""
        return self.invoke_llm(prompt)
    
    def process_with_tools(self, user_input):
        """
        VULNERABILITY 3: Tool calls influenced by user input
        """
        # User input could inject tool call instructions
        prompt = f"User wants to: {user_input}. What tool should we use?"
        tool_decision = self.invoke_llm(prompt)
        
        # DANGER: Tool selection based on LLM output influenced by user
        if "delete" in tool_decision:
            return self.delete_file_tool()
        
        return tool_decision
    
    def invoke_llm(self, prompt):
        """Simulated LLM invocation"""
        # In real code: client.chat.completions.create(...)
        return f"LLM response to: {prompt[:50]}..."
    
    def delete_file_tool(self):
        """Dangerous tool that could be maliciously invoked"""
        return "FILE DELETED"


def main():
    """
    VULNERABILITY 4: CLI input directly to prompt
    """
    agent = VulnerableAgent()
    
    # Get user input from command line
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
    else:
        user_input = input("Enter your message: ")
    
    # VULNERABLE: No validation
    response = agent.process_user_input(user_input)
    print(response)


if __name__ == "__main__":
    main()
