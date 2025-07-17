import os
import re

def read_file_content(file_path):
  
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
    
    from chat import chat
    messages = [{"role": "user", "content": prompt}]
    return chat(messages)

def generate_answer(current_file_text: str, content: str):
   
    prompt = f"文档内容：{current_file_text}\n问题：{content}"
    return generate_text(prompt)

def generate_summary(current_file_text: str):
    
    prompt = f"请为以下文档生成摘要：{current_file_text}"
    return generate_text(prompt)
