from openai import OpenAI
import openai
import requests

def img_gen(topic):

    client = OpenAI(api_key = "sk-proj-E4bAoJwpyeBZpOcxkURoT3BlbkFJbhSoemOEi3opB2wnLi3Z")

    #header = "I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"
    try:
      response = client.images.generate(
          model="dall-e-3",
          #prompt= "Create a very simple black and white line art of " + topic,
          prompt = f"a simple black and white drawing of a {topic}, black and white vector art, silhouette, simple, thick vector line art, simple silhouette",
          size="1024x1024",
          quality="standard",
          n=1,
      )
      print(response.data[0].url)
    except openai.OpenAIError as e:
      #print(e.http_status)
      print(e.error)

    image_url = response.data[0].url

    img_data = requests.get(image_url).content


    with open("prints/image.jpg", "wb") as handler:
        handler.write(img_data)

    with open(f"generated_images/{topic}.jpg", "wb") as handler:
        handler.write(img_data)

if __name__ == "__main__":
    img_gen(input("what to draw? "))
