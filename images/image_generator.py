# Iam not sure why, but this appears to be working, POV

import random
import string
import requests

import math
from openai import OpenAI
import os
import asyncio
from dotenv import load_dotenv
#USE pip3 install python-dotenv



class DalleProcessor:
    def __init__(self, key):
        self.client = OpenAI(
        api_key=key)
        
    def askGPT(self, systemPrompt, userPrompt):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use GPT-4 if available: "gpt-4"
                messages=[
                    {"role": "system", "content": systemPrompt},
                    {"role": "user", "content": userPrompt}
                ],
                temperature=0.7  # Controls creativity
            )
            response = response.choices[0].message.content.strip()
            return response

        except Exception as e:
            print("ERROR: ", e)
            return None

    def construct_image_prompt(self, hobby, topic, analogy, concept_breakdown):
        text = f"""
        * Instructions:
        You are teaching adults data science by relating it to their hobby. 
        Generate explanatory image for given text
        The image has to include the analogy provided and be not too crowded (minimalism is ideal).
        Focus on specific, visually representable elements and avoid typography.
        Have no more than 5 objects in the image.
        Hoby:
        {hobby}
        * Data science topic:
        {topic}
        * Analogy:
        {analogy}
        {concept_breakdown}
        * Generate this image. Remove any text.
    """
        if len(text)>1000:
            text = text[:1000]


        return text

    def generate_random_filename(self, length=13):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length)) + ".png"

    def save_image_from_url(self, image_url, prompt):
        # Generate filename from prompt
        local_filename = f"images/saved_images/{self.generate_random_filename()}"
        response = requests.get(image_url)
        with open(local_filename, 'wb') as f:
            f.write(response.content)
        print(f"Image saved as {local_filename}")
        return local_filename

    def generate_image(self, prompt, size="1024x1024"):
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            style='vivid',
            n=1,
        )
        return response.data[0].url

    def generate_and_save(self, hobby, topic, analogy, concept_breakdown):
        prompt = self.construct_image_prompt(hobby, topic, analogy, concept_breakdown)
        image_url = self.generate_image(prompt)
        local_filename = self.save_image_from_url(image_url, prompt)
        return local_filename


        


class OCRProcessor:
    # This makes it better for async function to run
    import keras_ocr
    import numpy as np
    import cv2
    def __init__(self):

        self.pipeline = self.keras_ocr.pipeline.Pipeline()

    def midpoint(self, x1, y1, x2, y2):
        """Calculate the midpoint between two points."""
        x_mid = int((x1 + x2) / 2)
        y_mid = int((y1 + y2) / 2)
        return (x_mid, y_mid)

    def inpaint_text(self, img_path):
        """
        Remove all text from an image using OCR and inpainting.

        Parameters:
        img_path (str): Path to the input image.

        Returns:
        np.array: The inpainted image without text.
        """
        # Read image
        img = self.keras_ocr.tools.read(img_path)

        # Generate (word, box) tuples
        prediction_groups = self.pipeline.recognize([img])

        # Create a mask with the same dimensions as the image
        mask = self.np.zeros(img.shape[:2], dtype="uint8")

        for box in prediction_groups[0]:
            x0, y0 = box[1][0]
            x1, y1 = box[1][1]
            x2, y2 = box[1][2]
            x3, y3 = box[1][3]

            x_mid0, y_mid0 = self.midpoint(x1, y1, x2, y2)
            x_mid1, y_mi1 = self.midpoint(x0, y0, x3, y3)

            thickness = int(math.sqrt((x2 - x1)**2 + (y2 - y1)**2))

            # Apply line mask over detected text
            self.cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255, thickness)

        # Apply inpainting
        img = self.cv2.inpaint(img, mask, 7, self.cv2.INPAINT_NS)

        return img
    
    def save_image(self, img, path):
        """Save an image to the specified path."""
        self.cv2.imwrite(path, img)
        print(f"Image saved at {path}")


    def inpaint_and_save(self, img_path, save_path):
        inpainted_img = self.inpaint_text(img_path)
        self.save_image(inpainted_img, save_path)
        return save_path

    
async def main(hobby:str, topic:str, analogy:str, concept_breakdown:str):
    load_dotenv()
    openai_key = os.environ.get("OPENAI_KEY")
    
    print("dalle init")

    if openai_key is None:
        raise ValueError("OPENAI_KEY environment variable not set")
    

    image_generator = DalleProcessor(openai_key)
    loop = asyncio.get_event_loop()
    ocr_main = await loop.run_in_executor(None, OCRProcessor)
    saved_image_path = await loop.run_in_executor(None, image_generator.generate_and_save, hobby, topic, analogy, concept_breakdown)

    ocr_main.inpaint_and_save(saved_image_path, saved_image_path)

    print(saved_image_path)
    return saved_image_path

if __name__ == "__main__":
    
    
    asyncio.run(main())


