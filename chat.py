import openai

client = openai.OpenAI(
    # Uncomment the following lines to use DeepSeek API
    # base_url="https://api.deepseek.com/v1",  
    # api_key="sk-38eff65a45bd4c4ba49371db2ecaee88"  
    base_url="http://localhost:8080/v1",
    api_key="dummy_key"
)

def chat(messages):
    """。
    Parameters:
        messages: app.py with the conversation history, a list of dictionaries
                  with "role" and "content" keys.
    return:
        generator， yielding response chunks from the model.
    """
    try:
        response = client.chat.completions.create(
            # Uncomment the following line to use DeepSeek model
            # model="deepseek-chat",
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            stream=True
        )
        for chunk in response:
            # compatible with OpenAI and LocalAI's response structure
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = getattr(chunk.choices[0], "delta", None)
                if delta and hasattr(delta, "content") and delta.content:
                    yield delta.content
    except Exception as e:
        yield f"Fail to use model: {str(e)}"
