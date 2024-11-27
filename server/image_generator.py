from openai import OpenAI

class ImageGenerator:
    def __init__(self, api_key):
        """
        Initialize the ImageGenerator with the OpenAI API key.
        """
        self.client = OpenAI(api_key=api_key)

    def generate_image(self, prompt, size="1024x1024", n=1, quality="standard"):
        """
        Generates an image using OpenAI's API and returns the URL of the generated image.
        Args:
            prompt (str): The text prompt for generating the image.
            size (str): The size of the image. Default is "1024x1024".
            n (int): Number of images to generate. Default is 1.
            quality (str): Quality of the generated image. Default is "standard".

        Returns:
            str: URL of the generated image, or an error message.
        """
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=n,
                size=size,
                quality=quality
            )
            # Extract and return the image URL
            return response.data[0].url
        except Exception as e:
            return f"Error generating image: {str(e)}"

# This function creates a prompt for generating an image using OpenAI's DALL-E model.
def create_image_prompt(narrative_background, key_cue):
    prompt = (
        f"Create an effective image-generation prompt, no more than 25 words, "
        f"for a children-friendly and visually appealing image. "
        f"Use simple and natural English words that everybody knows."
        f"Start the very beginning of the prompt in CAPS with the name of the related popular animation that children love, e.g., TOM & JERRY:  "
        f"Focus only on crafting the prompt, the characters, setting and activities. "
        f"Avoid any additional commentary or explanation\n"
        f"# NARRATIVE BACKGROUND\n{narrative_background}\n"
        f"# KEY CUE\n{key_cue}"
    )
    return prompt