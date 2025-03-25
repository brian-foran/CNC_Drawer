from openai import OpenAI
import openai
import requests
import os

def img_gen(topic):
    openAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not openAI_API_KEY:
        raise ValueError("Missing API key! Make sure it's set as an environment variable.")
    
    client = OpenAI(api_key=openAI_API_KEY)

#header = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"a simple black and white drawing of a {topic}, black and white vector art, silhouette, simple, thick vector line art, simple silhouette",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        print(image_url)
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    try:
        img_data = requests.get(image_url).content
    except requests.exceptions.RequestException as e:
        print(f"Failed to download image: {e}")
        return

    try:
        with open("prints/image.jpg", "wb") as handler:
            handler.write(img_data)
        with open(f"generated_images/{topic}.jpg", "wb") as handler:
            handler.write(img_data)
    except IOError as e:
        print(f"Failed to save image: {e}")

if __name__ == "__main__":
    img_gen(input("What to draw? "))
