from PIL import Image, ImageDraw, ImageFont
import re
import os

def extract_background_color_from_prompt(prompt: str) -> tuple:
    """Extract background color from prompt, returns RGB tuple"""
    prompt_lower = prompt.lower()
    
    # Common color mappings
    color_map = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203),
        'brown': (165, 42, 42),
        'lightblue': (173, 216, 230),
        'darkblue': (0, 0, 139),
        'lightgreen': (144, 238, 144),
        'darkgreen': (0, 100, 0),
    }
    
    # Look for color keywords in prompt
    for color_name, rgb in color_map.items():
        if f'{color_name} background' in prompt_lower or f'background {color_name}' in prompt_lower or f'{color_name} color' in prompt_lower:
            return rgb
    
    # Look for RGB values in prompt (e.g., "rgb(255, 0, 0)" or "color 255 0 0")
    import re
    rgb_pattern = r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)'
    match = re.search(rgb_pattern, prompt_lower)
    if match:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
            return (r, g, b)
    
    # Look for hex color values (e.g., "#FF0000" or "color #FF0000")
    hex_pattern = r'#([0-9a-f]{6})'
    match = re.search(hex_pattern, prompt_lower)
    if match:
        hex_color = match.group(1)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    
    # Default to white
    return (255, 255, 255)


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
    
    # Extract background color from prompt
    bg_color = extract_background_color_from_prompt(prompt)
    
    # Create base canvas
    canvas = Image.new("RGB", size, color=bg_color)
    
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


def extract_text_from_prompt(prompt: str) -> tuple:
    """Extract text content and language from prompt"""
    prompt_lower = prompt.lower()
    
    # Check if text should be added
    if not any(keyword in prompt_lower for keyword in ["add text", "with text", "text", "write"]):
        return None, None
    
    # Extract text content
    # Look for quoted text
    import re
    quoted_pattern = r'["\']([^"\']+)["\']'
    match = re.search(quoted_pattern, prompt)
    if match:
        text_content = match.group(1)
    else:
        # Look for "text: <content>" pattern
        text_pattern = r'text[:\s]+([^,\.]+)'
        match = re.search(text_pattern, prompt_lower)
        if match:
            text_content = prompt[match.start(1):match.end(1)].strip()
        else:
            text_content = "Generated Image"
    
    # Detect language
    language = "english"
    if "hindi" in prompt_lower or "हिंदी" in prompt:
        language = "hindi"
    elif "spanish" in prompt_lower:
        language = "spanish"
    elif "french" in prompt_lower:
        language = "french"
    
    return text_content, language


def add_text_overlay(canvas: Image.Image, prompt: str, size: tuple):
    """Add text overlay to canvas if specified in prompt"""
    # Extract text content and language
    text_content, language = extract_text_from_prompt(prompt)
    
    # Only add text if explicitly requested
    if text_content is None:
        return
    
    draw = ImageDraw.Draw(canvas)
    
    # Try to load appropriate font based on language
    font = None
    try:
        if language == "hindi":
            # Try to load a font that supports Devanagari script
            try:
                font = ImageFont.truetype("NotoSansDevanagari-Regular.ttf", 48)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf", 48)
                except:
                    font = ImageFont.load_default()
        else:
            # Try to load a standard font
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                except:
                    font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Calculate text position
    text_bbox = draw.textbbox((0, 0), text_content, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Extract text position from prompt (default to bottom center)
    x = (size[0] - text_width) // 2
    y = size[1] - text_height - 30
    
    if "top" in prompt.lower() and "text" in prompt.lower():
        y = 30
    elif "center" in prompt.lower() and "text" in prompt.lower():
        y = (size[1] - text_height) // 2
    
    # Extract text color from prompt
    text_color = (0, 0, 0)  # Default black
    if "white text" in prompt.lower():
        text_color = (255, 255, 255)
    elif "black text" in prompt.lower():
        text_color = (0, 0, 0)
    elif "red text" in prompt.lower():
        text_color = (255, 0, 0)
    elif "blue text" in prompt.lower():
        text_color = (0, 0, 255)
    
    # Add text with outline for better visibility
    # Draw outline
    for adj_x in [-2, -1, 0, 1, 2]:
        for adj_y in [-2, -1, 0, 1, 2]:
            if adj_x != 0 or adj_y != 0:
                outline_color = (255, 255, 255) if text_color == (0, 0, 0) else (0, 0, 0)
                draw.text((x + adj_x, y + adj_y), text_content, fill=outline_color, font=font)
    
    # Draw main text
    draw.text((x, y), text_content, fill=text_color, font=font)
