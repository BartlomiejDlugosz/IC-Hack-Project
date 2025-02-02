import images.image_generator as im_gen
import asyncio

def generate_an_image(hobby:str, topic:str, analogy:str, concept_breakdown:str):
    """Provide information on the topic that is being used for learning;
    The result is path to an image generated in approx 40s"""
    image_path = asyncio.run(im_gen.main(hobby, topic, analogy, concept_breakdown))
    return image_path


if __name__ == "__main__":
    hobby = "Fishing"
    topic = "Standard deviation"
    analogy = "Standard deviation can be understood as variation in fish size"
    concept_breakdown = "Standard deviation measures the amount of variation or dispersion of a set of values. In fishing, if the fish sizes are close to the average size, the standard deviation is low. If the fish sizes vary greatly, the standard deviation is high."
    path = generate_an_image(hobby, topic, analogy, concept_breakdown)