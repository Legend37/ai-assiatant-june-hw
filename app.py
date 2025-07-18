import gradio as gr
import os
from chat import chat  
from pdf import read_file_content, generate_answer

messages = [] 
current_file_text = None  

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
