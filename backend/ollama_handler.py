import subprocess
import json
import requests
import base64
import os
from typing import Dict, List, Optional

class OllamaImageGenerator:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3"
    
    def generate_image_prompt(self, user_prompt: str, tagged_images: Dict[str, str]) -> str:
        """
        Use Llama3 to convert user prompt with @tags into a detailed image generation prompt.
        """
        # Create context about available images
        image_context = ""
        for tag, filename in tagged_images.items():
            image_context += f"- @{tag}: {filename}\n"
        
        # Check if this is a presentation/animation request
        if any(keyword in user_prompt.lower() for keyword in ["presentation", "slideshow", "shift images", "gif", "animation"]):
            # For presentation/animation requests, return the original prompt
            # The GIF generator will handle the presentation logic
            return user_prompt
        
        ollama_prompt = f"""
You are an AI image generation prompt expert. Convert the user's request into a detailed, high-quality prompt for image generation.

User Request: {user_prompt}

Available Images (referenced by @tags):
{image_context}

Instructions:
1. Convert the user's request into a detailed image generation prompt
2. If the user references @tags, describe what those images should represent in the final image
3. Focus on visual composition, style, lighting, and artistic details
4. Make the prompt suitable for AI image generation (like Stable Diffusion)
5. Be specific about positioning, relationships between elements, and overall aesthetic

Respond with ONLY the image generation prompt, no explanations or additional text.
"""

        try:
            cmd = ["ollama", "run", self.model, "--prompt", ollama_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout.strip()
            
            # Clean up the output (remove any model-specific formatting)
            lines = output.split('\n')
            prompt_lines = []
            for line in lines:
                if line.strip() and not line.startswith('>') and not line.startswith('User:'):
                    prompt_lines.append(line.strip())
            
            return ' '.join(prompt_lines)
            
        except subprocess.TimeoutExpired:
            return f"Professional promotional image: {user_prompt}, high quality, detailed, commercial photography style"
        except Exception as e:
            return f"Professional promotional image: {user_prompt}, high quality, detailed, commercial photography style"
    
    def generate_image_with_ollama(self, prompt: str, width: int = 1024, height: int = 1024) -> Optional[str]:
        """
        Generate image using Ollama's image generation capabilities.
        Note: This assumes you have a model like 'stable-diffusion' or similar available in Ollama.
        """
        try:
            # Try to use Ollama's image generation if available
            payload = {
                "model": "stable-diffusion",  # or whatever image generation model you have
                "prompt": prompt,
                "width": width,
                "height": height,
                "format": "png"
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                # Save the generated image
                image_data = response.content
                output_path = f"backend/static/temp/generated_{hash(prompt) % 100000}.png"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                
                return output_path
            else:
                return None
                
        except Exception as e:
            return None
    
    def generate_image_with_external_api(self, prompt: str, width: int = 1024, height: int = 1024) -> Optional[str]:
        """
        Fallback: Generate image using external API (like Replicate, Hugging Face, etc.)
        This is a placeholder - you would need to implement with your preferred service.
        """
        # Placeholder for external API integration
        # You could integrate with:
        # - Replicate API
        # - Hugging Face Inference API
        # - Stability AI API
        # - Or any other image generation service
        
        return None
    
    def refine_image_prompt(self, original_prompt: str, user_feedback: str) -> str:
        """
        Use Llama3 to refine the image generation prompt based on user feedback.
        """
        ollama_prompt = f"""
You are an AI image generation prompt expert. Refine the following image generation prompt based on user feedback.

Original Prompt: {original_prompt}
User Feedback: {user_feedback}

Instructions:
1. Incorporate the user's feedback into the prompt
2. Maintain the core concept while addressing the feedback
3. Make the prompt more specific and detailed
4. Focus on visual improvements and artistic details
5. Ensure the refined prompt is suitable for AI image generation

Respond with ONLY the refined image generation prompt, no explanations.
"""

        try:
            cmd = ["ollama", "run", self.model, "--prompt", ollama_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout.strip()
            
            # Clean up the output
            lines = output.split('\n')
            prompt_lines = []
            for line in lines:
                if line.strip() and not line.startswith('>') and not line.startswith('User:'):
                    prompt_lines.append(line.strip())
            
            return ' '.join(prompt_lines)
            
        except Exception as e:
            return f"{original_prompt}, {user_feedback}, improved version"

# Global instance
ollama_generator = OllamaImageGenerator()

def generate_ai_image(user_prompt: str, tagged_images: Dict[str, str], width: int = None, height: int = None) -> Optional[str]:
    """
    Main function to generate AI image using Llama3 + Ollama.
    """
    # Extract custom dimensions from prompt if not provided
    if width is None or height is None:
        from .image_composer import extract_canvas_size_from_prompt
        canvas_size = extract_canvas_size_from_prompt(user_prompt)
        width, height = canvas_size
    
    # Step 1: Convert user prompt to detailed image generation prompt
    detailed_prompt = ollama_generator.generate_image_prompt(user_prompt, tagged_images)
    
    # Step 2: Try to generate image with Ollama
    image_path = ollama_generator.generate_image_with_ollama(detailed_prompt, width, height)
    
    # Step 3: Fallback to external API if Ollama fails
    if not image_path:
        image_path = ollama_generator.generate_image_with_external_api(detailed_prompt, width, height)
    
    return image_path

def refine_ai_image(original_prompt: str, user_feedback: str) -> str:
    """
    Refine an image generation prompt based on user feedback.
    """
    return ollama_generator.refine_image_prompt(original_prompt, user_feedback)
