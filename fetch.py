import requests
from bs4 import BeautifulSoup

def fetch(url: str):
    """
    获取网页内容并提取文字信息，生成总结问题
    """
    if not url or not url.strip():
        return "错误:URL不能为空"
        
    try:
        # 获取网页内容
        response = requests.get(url)
        response.raise_for_status()
        
        # 检查内容类型是否为HTML
        content_type = response.headers.get('content-type', '')
        if 'text/html' not in content_type:
            return f"错误：不支持的内容类型 {content_type}"
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取所有p标签的文字内容
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
        processed_results = '\n'.join(paragraphs)
        
        if not processed_results:
            return "错误：无法从网页中提取有效内容"
            
        # 生成总结问题
        question = f"Act as a summarizer. Please summarize {url}. The following is the content:\n\n{processed_results}"
        
        return question
    except Exception as e:
        return f"获取网页内容时出错: {str(e)}"


if __name__ == "__main__":
    fetch("https://dev.qweather.com/en/help")