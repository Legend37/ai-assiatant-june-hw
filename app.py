import gradio as gr
import os
from chat import chat  
from pdf import read_file_content, generate_answer
from image_generate import image_generate  

messages = [] 
current_file_text = None  

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
                user_content = f"[File: {user[0]}]"
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
    """Process uploaded file, extract content and update display"""
    global messages, current_file_text
    file_path = file.name
    current_file_text = read_file_content(file_path)
    if current_file_text:
        prompt = f"I uploaded a document, the content is as follows: {current_file_text}"
        messages.append({"role": "user", "content": prompt})
        history = history + [((file.name,), None)]
    return history

def bot(history):
    """Call the model to generate a reply and update chat history"""
    global messages, current_file_text
    
    # 获取最后一条用户消息
    last_message = messages[-1]["content"]

    # 检查是否是图片生成指令
    if last_message.startswith("/image "):
        # 提取图片描述内容
        image_content = last_message[7:]  # 移除"/image "前缀
        
        # 调用图片生成函数
        image_url = image_generate(image_content)
        
        # 更新messages
        messages.append({"role": "assistant", "content": image_url})

        # 判断返回的是URL还是错误信息
        if image_url.startswith("图片生成过程中出错"):
            # 错误信息直接显示文本
            history[-1][1] = image_url
        else:
            # 正确生成的图片URL以元组形式返回以显示图片
            history[-1][1] = (image_url,)
        
        write_debug_info(messages, history)

        return history
    else:
        # 正常的聊天响应处理
        response = ""
        new_history = history
        # Stream update history, create a new copy to avoid state issues
        for chunk in chat(messages):
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

        return new_history

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
    demo.launch()
