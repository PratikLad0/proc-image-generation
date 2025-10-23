from PIL import Image, ImageDraw, ImageFont
import re
import os

def extract_canvas_size_from_prompt(prompt: str) -> tuple:
    """Extract custom width and height from prompt"""
    # Look for various dimension patterns
    patterns = [
        r'(\d+)\s*x\s*(\d+)',  # 1920x1080, 1920 x 1080
        r'(\d+)\s*by\s*(\d+)',  # 1920 by 1080
        r'(\d+)\s*width\s*(\d+)\s*height',  # 1920 width 1080 height
        r'width\s*(\d+)\s*height\s*(\d+)',  # width 1920 height 1080
        r'(\d+)\s*wide\s*(\d+)\s*tall',  # 1920 wide 1080 tall
        r'(\d+)\s*pixels?\s*wide\s*(\d+)\s*pixels?\s*tall',  # 1920 pixels wide 1080 pixels tall
        r'size\s*(\d+)\s*x\s*(\d+)',  # size 1920x1080
        r'dimensions?\s*(\d+)\s*x\s*(\d+)',  # dimensions 1920x1080
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            width = int(match.group(1))
            height = int(match.group(2))
            
            # Validate reasonable dimensions
            if 100 <= width <= 4000 and 100 <= height <= 4000:
                return (width, height)
    
    # Look for common aspect ratios
    aspect_ratios = {
        'square': (1080, 1080),
        'landscape': (1920, 1080),
        'portrait': (1080, 1920),
        'widescreen': (1920, 1080),
        'instagram': (1080, 1080),
        'youtube': (1920, 1080),
        'facebook': (1200, 630),
        'twitter': (1200, 675),
    }
    
    prompt_lower = prompt.lower()
    for ratio_name, dimensions in aspect_ratios.items():
        if ratio_name in prompt_lower:
            return dimensions
    
    # Default size
    return (1080, 1080)

def compose_image_with_tags(image_paths: dict, prompt: str, output_path: str, size=None):
    """
    Compose an image based on prompt with tagged images.
    
    Args:
        image_paths: Dict mapping tags to image file paths
        prompt: Text prompt describing the composition
        output_path: Output file path
        size: Canvas size (width, height) - if None, will extract from prompt
    """
    # Extract custom dimensions from prompt if not provided
    if size is None:
        size = extract_canvas_size_from_prompt(prompt)
    
    # Create base canvas
    canvas = Image.new("RGB", size, color=(255, 255, 255))
    
    # Parse prompt for positioning instructions
    positioning = parse_positioning_instructions(prompt)
    
    # Load and position images
    for tag, image_path in image_paths.items():
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path).convert("RGBA")
                
                # Get positioning for this tag
                position = positioning.get(tag, {"type": "center", "x": 0, "y": 0})
                
                # Resize image if needed
                img = resize_image_for_position(img, position, size)
                
                # Calculate final position
                final_x, final_y = calculate_position(img.size, position, size)
                
                # Paste image onto canvas
                if img.mode == "RGBA":
                    canvas.paste(img, (final_x, final_y), img)
                else:
                    canvas.paste(img, (final_x, final_y))
                    
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                continue
    
    # Add text overlay if specified in prompt
    add_text_overlay(canvas, prompt, size)
    
    # Save the result
    canvas.save(output_path, "PNG")
    return output_path


def parse_positioning_instructions(prompt: str) -> dict:
    """Parse positioning instructions from prompt"""
    positioning = {}
    prompt_lower = prompt.lower()
    
    # Look for positioning keywords
    if "background" in prompt_lower or "bg" in prompt_lower:
        # Find which tag is mentioned as background
        for tag in re.findall(r'@(\w+)', prompt):
            if "background" in prompt_lower or "bg" in prompt_lower:
                positioning[tag] = {"type": "background", "x": 0, "y": 0}
                break
    
    if "front" in prompt_lower or "foreground" in prompt_lower:
        # Find which tag is mentioned as front
        for tag in re.findall(r'@(\w+)', prompt):
            if "front" in prompt_lower or "foreground" in prompt_lower:
                positioning[tag] = {"type": "front", "x": 0, "y": 0}
                break
    
    if "center" in prompt_lower:
        for tag in re.findall(r'@(\w+)', prompt):
            positioning[tag] = {"type": "center", "x": 0, "y": 0}
    
    if "left" in prompt_lower:
        for tag in re.findall(r'@(\w+)', prompt):
            positioning[tag] = {"type": "left", "x": 0, "y": 0}
    
    if "right" in prompt_lower:
        for tag in re.findall(r'@(\w+)', prompt):
            positioning[tag] = {"type": "right", "x": 0, "y": 0}
    
    if "top" in prompt_lower:
        for tag in re.findall(r'@(\w+)', prompt):
            positioning[tag] = {"type": "top", "x": 0, "y": 0}
    
    if "bottom" in prompt_lower:
        for tag in re.findall(r'@(\w+)', prompt):
            positioning[tag] = {"type": "bottom", "x": 0, "y": 0}
    
    return positioning


def resize_image_for_position(img: Image.Image, position: dict, canvas_size: tuple) -> Image.Image:
    """Resize image based on its intended position"""
    canvas_width, canvas_height = canvas_size
    img_width, img_height = img.size
    
    if position["type"] == "background":
        # Resize to fill entire canvas
        return img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
    elif position["type"] in ["front", "center"]:
        # Resize to reasonable size for foreground
        max_size = min(canvas_width, canvas_height) // 2
        if max(img_width, img_height) > max_size:
            ratio = max_size / max(img_width, img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return img


def calculate_position(img_size: tuple, position: dict, canvas_size: tuple) -> tuple:
    """Calculate final position for image placement"""
    img_width, img_height = img_size
    canvas_width, canvas_height = canvas_size
    
    if position["type"] == "background":
        return (0, 0)
    elif position["type"] == "center":
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2
        return (x, y)
    elif position["type"] == "left":
        x = 0
        y = (canvas_height - img_height) // 2
        return (x, y)
    elif position["type"] == "right":
        x = canvas_width - img_width
        y = (canvas_height - img_height) // 2
        return (x, y)
    elif position["type"] == "top":
        x = (canvas_width - img_width) // 2
        y = 0
        return (x, y)
    elif position["type"] == "bottom":
        x = (canvas_width - img_width) // 2
        y = canvas_height - img_height
        return (x, y)
    else:
        # Default to center
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2
        return (x, y)


def add_text_overlay(canvas: Image.Image, prompt: str, size: tuple):
    """Add text overlay to canvas if specified in prompt"""
    # Simple text overlay - can be enhanced later
    if "text" in prompt.lower() or "title" in prompt.lower():
        draw = ImageDraw.Draw(canvas)
        try:
            # Try to use a default font, fallback to basic if not available
            font = ImageFont.load_default()
        except:
            font = None
        
        text = "Generated Image"
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) // 2
        y = size[1] - text_height - 20
        
        draw.text((x, y), text, fill=(0, 0, 0), font=font)
