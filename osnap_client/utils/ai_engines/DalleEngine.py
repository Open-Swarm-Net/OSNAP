import os
import openai
import tiktoken
import requests

class DalleEngine:
    def __init__(self, size="256x256"):
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        
        openai.api_key = os.getenv("OPENAI_API_KEY")

        self.size = size

    def imagine(self, prompt: str):
        """
        Generates an image from a prompt.

        Args:
        - prompt (str): The prompt to generate an image from.

        Returns:
        - image (bytes): The image as bytes.
        """
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size=self.size
        )
        image_url = response['data'][0]['url']

        # download image
        image = requests.get(image_url, allow_redirects=True)
        return image.content

