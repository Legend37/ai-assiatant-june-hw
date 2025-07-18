import os
from chat import client 

def image_generate(content: str):
    """
    使用stablediffusion API生成图片

    Parameters:
        content: 描述要生成的图片内容

    Returns:
        生成的图片URL
    """
    try:
        # 调用图片生成API
        response = client.images.generate(
            prompt=content,
            size="256x256",
            n=1,
        )

        # 获取图片URL
        image_url = response.data[0].url
        return image_url

    except Exception as e:
        return f"图片生成过程中出错: {str(e)}"


if __name__ == "__main__":
    image_generate('A cute baby sea otter')