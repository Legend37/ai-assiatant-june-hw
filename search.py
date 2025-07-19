import requests
from bs4 import BeautifulSoup
from serpapi import BingSearch

def search(content: str):
    """
    使用必应搜索接口进行网络搜索
    :param content: 搜索内容
    :return: 组合后的提问内容
    """
    try:
        params = {
            "q": content,
            "api_key": "7e4e5f753b8497b5eea25f4bfe7e9fcf8f40a1425cd244f49e610d4790414df5",  #  SerpApi API 密钥
            "engine": "bing"  # 指定使用必应搜索
        }
        search = BingSearch(params)
        results = search.get_dict()
        
        # 获取第一条结果的 snippet
        first_result = results.get("organic_results", [{}])[0]
        search_results = first_result.get("snippet", "未找到相关信息")
        
        # 按照要求格式组合内容
        return f"Please answer {content} based on the search result:\n\n{search_results}"
    except Exception as e:
        return f"搜索出错: {str(e)}"

if __name__ == "__main__":
    search("Sun Wukong")