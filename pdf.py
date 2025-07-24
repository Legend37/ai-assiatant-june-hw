import os
import re
import openai  # 确保导入openai

# 创建与chat.py相同的客户端配置
client = openai.OpenAI(
    # base_url="http://localhost:8080/v1",
    # api_key="dummy_key"
    base_url="https://api.deepseek.com/v1",
    api_key="sk-38eff65a45bd4c4ba49371db2ecaee88"
)

def read_file_content(file_path):
    """读取文件内容"""
    if file_path.endswith('.pdf'):
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    elif file_path.endswith(('.txt', '.md')):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    return None
def generate_text(prompt):
    """调用文字补全接口生成文本（支持流式输出）"""
    try:
        # 使用与chat.py相同的配置
        response = client.chat.completions.create(
            # model="gpt-3.5-turbo",  # 使用聊天模型
            model="deepseek-chat",  # 使用DeepSeek聊天模型
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            stream=True
        )
        
        for chunk in response:
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = getattr(chunk.choices[0], "delta", None)
                if delta and hasattr(delta, "content") and delta.content:
                    yield delta.content
    except Exception as e:
        yield f"文字生成失败: {str(e)}"
def generate_summary(current_file_text):
    """生成文件摘要的提示"""
    return (
        f"Please generate a concise summary for the following document(回答语言取决于文件的主体语言):\n\n"
        f"{current_file_text}"
    )

def generate_question(current_file_text, content):
    """生成结合文件内容和用户问题的提问"""
    return (
        f"Please answer the question based on the following document content:\n\n"
        f"Document Content:\n{current_file_text}\n\n"
        f"Question: {content}"
    )

