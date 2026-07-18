class DummyLLM:
    def invoke(self, prompt: str):
        print(f"Invoking LLM with: {prompt}")

def process_user_input(user_input: str):
    llm = DummyLLM()
    # Vulnerable prompt construction
    prompt = f"User said: {user_input}. Respond professionally."
    llm.invoke(prompt)

if __name__ == "__main__":
    process_user_input("Hello there")
