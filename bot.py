from huggingface_hub import InferenceClient
from context import retrieve_context  

print("logging in...")
client = InferenceClient(
    provider="hf-inference",
    api_key="<token>",
)
print("** inference client created")

def chat():
    print("Welcome to the RAG Bot! Type 'exit' to quit.")

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() == "exit":
            print("Exiting...")
            break

        # Retrieve relevant context from ChromaDB
        retrieved_context = retrieve_context(user_input)

        # Create completion request
        completion = client.chat.completions.create(
            model="mistralai/Mistral-7B-v0.1",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a sharp and professional lawyer. Here is some relevant information:\n{retrieved_context}"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            max_tokens=500,
        )

        # Print response
        print("\nBot:", completion.choices[0].message["content"])

# Run chat interface
chat()