import gradio as gr
import os
from chat import chat  
from pdf import read_file_content
from image_generate import image_generate
from mnist import image_classification  # 导入图片分类函数
from search import search
from fetch import fetch 
messages = [] 
current_file_text = None
current_file_type = None

def write_debug_info(messages, history):
    """Write the current messages and history to answer/answer.txt for debugging purposes"""
    # Create answer directory if it doesn't exist
    os.makedirs('answer', exist_ok=True)
    
    with open('answer/answer.txt', 'a', encoding='utf-8') as f:
        f.write("\n----- Messages -----\n")
        for i, message in enumerate(messages):
            f.write(f"[{i}] {message['role']}: {message['content'][:50]}{'...' if len(message['content']) > 50 else ''}\n")
        
        f.write("\n----- History -----\n")
        for i, (user, assistant) in enumerate(history):
            # User content could be either text or file tuple
            if isinstance(user, tuple):
                user_content = f"File: {user[0]}"
            else:
                user_content = user[:50] + ('...' if len(user) > 50 else '')
            
            # Assistant content could be None, text, or image tuple
            if assistant is None:
                assistant_content = "None"
            elif isinstance(assistant, tuple) and len(assistant) == 1:
                assistant_content = f"Image: {assistant[0][:40]}..."
            else:
                assistant_content = str(assistant)[:50] + ('...' if len(str(assistant)) > 50 else '')
                
            f.write(f"[{i}] user: {user_content}\n")
            f.write(f"    assistant: {assistant_content}\n\n")
        
        f.write("-" * 50 + "\n")

def add_text(history, text):
    """Process user input text, update chat history and message list"""
    global messages
    
    history = history + [(text, None)]
    
    messages.append({"role": "user", "content": text})
    return history, gr.update(value="", interactive=False)  # Clear textbox and disable interaction

def add_file(history, file):
    global messages, current_file_text, current_file_type
    
    try:
        file_path = file.name
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower()
        current_file_type = file_ext

        # 处理PNG图片
        if file_ext == '.png':
            messages.append({"role": "user", "content": f"Please classify {filename}"})
            history = history + [((file.name,), None)]
            return history
        
        # 处理文本/PDF文件
        current_file_text = read_file_content(file_path)
        if current_file_text:
            # 添加文件信息到消息记录
            file_info = f"Uploaded file: {filename} ({file_ext} format)"
            messages.append({"role": "user", "content": file_info})
            history = history + [((file.name,), None)]
            
            # 如果是TXT文件，自动触发总结
            if file_ext == '.txt':
                summary_request = "Please summarize the uploaded document"
                messages.append({"role": "user", "content": summary_request})
                history = history + [(summary_request, None)]
        else:
            # 文件内容读取失败
            error_msg = f"无法读取文件内容: {filename}"
            messages.append({"role": "user", "content": error_msg})
            history = history + [(error_msg, None)]
    
    except Exception as e:
        error_msg = f"文件处理错误: {str(e)}"
        messages.append({"role": "user", "content": error_msg})
        history = history + [(error_msg, None)]
    
    return history
def bot(history):
    """Call the model to generate a reply and update chat history"""
    global messages, current_file_text, current_file_type

    # 限制消息历史长度，避免超过上下文窗口
    def trim_messages(messages, max_messages=10):
        """保留最近的消息，避免上下文过长"""
        if len(messages) <= max_messages:
            return messages
        # 保留系统消息（如果有）和最近的消息
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        recent_messages = messages[-max_messages:]
        return system_messages + recent_messages

    last_message = messages[-1]["content"]
    
    # 检查是否是分类图片请求（格式为"Please classify {filename}"）
    if last_message.startswith("Please classify ") and ".png" in last_message:
        # 从最后一个history条目中获取文件路径
        if len(history) > 0 and isinstance(history[-1][0], tuple) and len(history[-1][0]) > 0:
            file_path = history[-1][0][0]  # 获取文件路径

            classification_result = image_classification(file_path)
            messages.append({"role": "assistant", "content": classification_result})
            history[-1][1] = classification_result
            
            write_debug_info(messages, history)
            yield history
        
    # 检查是否是图片生成指令
    elif last_message.startswith("/image "):

        image_content = last_message[7:]  # 移除"/image "前缀

        image_url = image_generate(image_content)
        messages.append({"role": "assistant", "content": image_url or ""})

        # 将URL转换为本地文件路径，避免SSRF问题
        def url_to_local_path(url):
            if not url:
                return ""
            # 先移除URL前缀
            if url.startswith("http://localhost:8080/"):
                relative_path = url.replace("http://localhost:8080/", "")
            elif url.startswith("http://127.0.0.1:8080/"):
                relative_path = url.replace("http://127.0.0.1:8080/", "")
            else:
                relative_path = url
            
            # 将generated-images路径映射到LocalAI目录
            relative_path = relative_path.replace("generated-images", "LocalAI/generated/images")
            return relative_path

        # 判断返回的是URL还是错误信息
        if not image_url or image_url.startswith("图片生成过程中出错"):
            history[-1][1] = image_url or "图片生成失败"
        else:
            # 转换为本地路径避免SSRF错误
            local_path = url_to_local_path(image_url)
            print(f"DEBUG - 原始URL: {image_url}")
            print(f"DEBUG - 转换后路径: {local_path}")
            print(f"DEBUG - 文件是否存在: {os.path.exists(local_path)}")
            history[-1][1] = (local_path,)
        
        write_debug_info(messages, history)

        yield history
    
    # 检查是否是网络搜索指令
    elif last_message.startswith("/search "):
        search_content = last_message[8:]
        
        combined_content = search(search_content)
        messages[-1]["content"] = combined_content
        
        # 使用修剪后的消息避免上下文过长
        trimmed_messages = trim_messages(messages)
        
        response = ""
        new_history = history
        for chunk in chat(trimmed_messages):
            if chunk and chunk.strip():
                response += chunk
                new_history = history[:-1] + [(history[-1][0], response)]
                yield new_history
        
        if response.strip():
            messages.append({"role": "assistant", "content": response.strip()})
        
        write_debug_info(messages, new_history)
    elif current_file_text and current_file_type == '.txt' and last_message == "Please summarize the uploaded document":
        try:
            from pdf import generate_summary, generate_text
            
            summary_prompt = generate_summary(current_file_text)
            print(f"总结提示: {summary_prompt[:100]}...")  # 调试输出
            
            response = ""
            new_history = history
            for chunk in generate_text(summary_prompt):
                if chunk:
                    response += chunk
                    new_history = history[:-1] + [(history[-1][0], response)]
                    yield new_history
            
            if response.strip():
                messages.append({"role": "assistant", "content": response.strip()})
            else:
                error_msg = "未能生成总结内容xx"
                messages.append({"role": "assistant", "content": error_msg})
                new_history = history[:-1] + [(history[-1][0], error_msg)]
                yield new_history
            
            write_debug_info(messages, new_history)
        
        except Exception as e:
            error_msg = f"总结生成错误: {str(e)}"
            messages.append({"role": "assistant", "content": error_msg})
            history[-1][1] = error_msg
            write_debug_info(messages, history)
            yield history
    
    # 处理/file指令
    elif last_message.startswith("/file "):
        content = last_message[6:].strip()
        from pdf import generate_question, generate_text
        
        if not current_file_text:
            response = "错误：请先上传文件"
            messages.append({"role": "assistant", "content": response})
            history[-1][1] = response
            write_debug_info(messages, history)
            yield history
            return
        
        # 生成问题提示
        question = generate_question(current_file_text, content)
        messages[-1]["content"] = question
        
        # 流式生成回答
        response = ""
        new_history = history
        for chunk in generate_text(question):
            if chunk:
                response += chunk
                new_history = history[:-1] + [(history[-1][0], response)]
                yield new_history
        
        if response.strip():
            messages.append({"role": "assistant", "content": response.strip()})
        
        write_debug_info(messages, new_history)
    
    # 检查是否是网页总结指令
    elif last_message.startswith("/fetch "):
        url = last_message[7:].strip()
        
        if not url:
            messages.append({"role": "assistant", "content": "错误：URL不能为空"})
            history[-1][1] = "错误：URL不能为空"
            write_debug_info(messages, history)
            yield history
            return
            
        # 调用fetch函数获取总结问题
        question = fetch(url)
        
        # 如果fetch返回错误信息，直接显示
        if question.startswith("错误："):
            messages.append({"role": "assistant", "content": question})
            history[-1][1] = question
            write_debug_info(messages, history)
            yield history
            return
            
        # 更新messages
        messages[-1]["content"] = question
        
        # 使用修剪后的消息避免上下文过长
        trimmed_messages = trim_messages(messages)
        
        response = ""
        new_history = history
        for chunk in chat(trimmed_messages):
            if chunk and chunk.strip():
                response += chunk
                new_history = history[:-1] + [(history[-1][0], response)]
                yield new_history
        
        if response.strip():
            messages.append({"role": "assistant", "content": response.strip()})
        
        write_debug_info(messages, new_history)
    
    # 正常的聊天响应以及文件响应
    else:
        # 使用修剪后的消息避免上下文过长
        trimmed_messages = trim_messages(messages)
        
        response = ""
        new_history = history
        # Stream update history, create a new copy to avoid state issues
        for chunk in chat(trimmed_messages):
            # Only add new reply content, avoid repeating previous dialogue
            if chunk and chunk.strip():
                response += chunk
                # Create a new history copy, only update current assistant reply
                new_history = history[:-1] + [(history[-1][0], response)]
                yield new_history
        # After receiving all, update messages, only save the final reply
        if response.strip():
            messages.append({"role": "assistant", "content": response.strip()})
        
        write_debug_info(messages, new_history)

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=(None, os.path.join(os.path.dirname(__file__), "avatar.png"))  
    )
    
    with gr.Row():
        txt = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="输入文本并按回车，或上传文件",
            container=False,
        )
        clear_btn = gr.Button('Clear')
        btn = gr.UploadButton("📁", file_types=["image", "video", "audio", "text", "pdf"])
    
    txt_msg = txt.submit(
        add_text, [chatbot, txt], [chatbot, txt], queue=False
    ).then(
        bot, chatbot, chatbot  
    ).then(
        lambda: gr.update(interactive=True), None, [txt], queue=False  
    )
    

    file_msg = btn.upload(
        add_file, [chatbot, btn], [chatbot], queue=False
    ).then(
        bot, chatbot, chatbot 
    )
    
   
    def clear_all():
        global messages
        messages = []
        return []

    clear_btn.click(
        clear_all,
        None,
        [chatbot],
        queue=False
    )

if __name__ == "__main__":
    demo.queue()
    demo.launch(allowed_paths=["LocalAI"])
