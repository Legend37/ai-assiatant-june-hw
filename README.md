# 程序设计实训2025

## Deployment

```powershell
pip install -r requirements.txt
cd LocalAI
docker compose up -d
cd ..
python app.py
```

### Usage 

- **/fetch {YOUR URL}** Summarize the URL given, but in some case the target website may block machine request.
- **/image {YOUR PROMPT}** Generate the image based on your prompts, using localai mode
- **/search {CONTENT}** Use Bing API to search your content. Only support English because of SerpAPI.
- **/file {CONTENT}** Generate response according to your files and questions.
