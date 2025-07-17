import gradio as gr
import os
from chat import chat  
from pdf import read_file_content, generate_answer

messages = [] 
current_file_text = None  

def add_text(history, text):
    """处理用户输入的文本，更新历史记录和消息列表"""
    global messages
    
    history = history + [(text, None)]
    
    messages.append({"role": "user", "content": text})
    return history, gr.update(value="", interactive=False)  

def add_file(history, file):
    """处理上传的文件，提取内容并更新显示"""
    global messages, current_file_text
    file_path = file.name
    current_file_text = read_file_content(file_path)
    if current_file_text:
        prompt = f"我上传了一份文档，内容如下：{current_file_text}"
        messages.append({"role": "user", "content": prompt})
        history = history + [((file.name,), None)]
    return history

def bot(history):
    """调用模型生成回复，更新历史记录"""
    global messages, current_file_text
   
    response = chat(messages)
  
    history[-1][1] = response
  
    messages.append({"role": "assistant", "content": response})
    return history

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
    
   
    clear_btn.click(
        lambda: ( [], [] ),  
        None, 
        [chatbot], 
        queue=False
    ).then(
        lambda: setattr(globals(), 'messages', []),  
        None, 
        None
    )

if __name__ == "__main__":
    demo.queue()
    demo.launch()
