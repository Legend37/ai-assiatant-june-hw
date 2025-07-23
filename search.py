import requests
from bs4 import BeautifulSoup
from serpapi import BingSearch
import json

def search(content: str):
    """
    使用必应搜索接口进行网络搜索
    :param content: 搜索内容
    :return: 组合后的提问内容
    """
    if not content or not content.strip():
        return "搜索内容不能为空"
    
    try:
        params = {
            "q": content,
            "api_key": "7e202d72bd9bbe30e7aa6258eb8e4d2457e767a65de37ae80e30966845ad5cd2",
            "engine": "bing"
        }
        search_client = BingSearch(params)
        results = search_client.get_dict()
        
        # 检查是否有错误信息
        if "error" in results:
            error_msg = results["error"]
            return f"搜索API错误: {error_msg}"
        
        # 完整打印结果进行调试（前500字符）
        
        # 安全地获取有机搜索结果，并合并前3条
        organic_results = results.get("organic_results", [])
        
        merged_snippets = []
        for idx, item in enumerate(organic_results[:3]):
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            link = item.get("link", "")
            if snippet and snippet != "未找到相关信息":
                merged_snippets.append(f"[{idx+1}] 标题: {title}\n内容: {snippet}\n来源: {link}")
        
        if merged_snippets:
            result_text = f"Please answer '{content}' based on the following search results:\n\n" + "\n\n".join(merged_snippets)
            return result_text
        else:
            pass
        
        # 尝试其他可能的结果类型
        if "answer_box" in results:
            answer_box = results["answer_box"]
            answer = answer_box.get("answer", "") or answer_box.get("snippet", "")
            if answer:
                return f"Please answer '{content}' based on the search result:\n\n{answer}"
        
        if "knowledge_graph" in results:
            kg = results["knowledge_graph"]
            description = kg.get("description", "")
            if description:
                return f"Please answer '{content}' based on the search result:\n\n{description}"
        
        # 如果都没有找到有用信息
        return f"搜索 '{content}' 未找到相关信息。API返回了数据但没有可用内容。"
        
    except ImportError as e:
        error_msg = f"SerpApi模块导入失败: {str(e)}"
        return error_msg
        
    except Exception as e:
        error_msg = f"搜索过程中发生错误: {str(e)}"
        return error_msg

if __name__ == "__main__":
    # 测试多个查询
    query="Sun Wukong"
    result = search(query)