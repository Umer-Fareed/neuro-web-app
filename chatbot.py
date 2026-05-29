import openai

openai.api_key = "key-53guabstzysvA52hsgwy2wa"

model = "gpt-3.5-turbo"

conversation = [
    {"role": "system", "content": "You are a helpful assistant."}
]

def chat():
    print("Start chatting with the AI (type 'exit' to stop):\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        conversation.append({"role": "user", "content": user_input})

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=conversation
            )

            reply = response['choices'][0]['message']['content']
            conversation.append({"role": "assistant", "content": reply})
            print("AI:", reply)

        except Exception as e:
            print("Error:", e)
            break

if __name__ == "__main__":
    chat()
