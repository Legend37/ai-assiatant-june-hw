import openai

client = openai.OpenAI(
    base_url="http://localhost:8080/v1",  
    api_key="dummy_key"  
)

def chat(messages):
    """
    调用本地gpt-3.5-turbo模型生成回复
    参数:
        messages: 聊天记录列表，格式为[{"role": "user"/"assistant", "content": "..."}, ...]
    返回:
        模型生成的回复文本
    """
    try:
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=messages,
            temperature=0.7 
        )
       
        return response.choices[0].message.content
    except Exception as e:
        return f"调用模型失败: {str(e)}"
