import openai

client = openai.OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="dummy_key"
)

def image_generate(content: str):
    """
    使用stablediffusion API生成图片

    Parameters:
        content: 描述要生成的图片内容

    Returns:
        生成的图片URL
    """
    try:
        response = client.images.generate(
            prompt=content,
            size="256x256",
            n=1,
        )

        image_url = response.data[0].url
        return image_url

    except Exception as e:
        return f"图片生成过程中出错: {str(e)}"

if __name__ == "__main__":
    image_generate('A cute baby sea otter')