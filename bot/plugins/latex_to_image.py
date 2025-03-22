import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import Dict
from .plugin import Plugin
import random
import string

class LatexToImagePlugin(Plugin):
    """
    A plugin to convert a LaTeX math expression into an image
    """
    def get_source_name(self) -> str:
        return "LatexToImage"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "latex_to_image",
            "description": "Convert a LaTeX math expression into an image.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A LaTeX math expression. Example: 'x^2 + y^2 = z^2'"
                    }
                },
                "required": ["expression"],
            },
        }]
    
    def generate_random_string(self, length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        try:
            expression = kwargs["expression"]

            if not os.path.exists("uploads/latex_images"):
                os.makedirs("uploads/latex_images")

            image_file_path = os.path.join("uploads/latex_images", f"{self.generate_random_string(15)}.png")

            # Render LaTeX expression as an image
            plt.text(0.5, 0.5, f'${expression}$', fontsize=20, ha='center')
            plt.axis('off')
            plt.savefig(image_file_path, bbox_inches='tight', dpi=100)
            plt.clf()  # Clear the figure

            return {
                'direct_result': {
                    'kind': 'photo',
                    'format': 'path',
                    'value': image_file_path
                }
            }
        except Exception as e:
            # Handle exceptions and remove any created files if needed
            print(f"An error occurred: {e}")
            if os.path.exists(image_file_path):
                os.remove(image_file_path)
            return {'result': 'Unable to convert LaTeX expression to image'}
